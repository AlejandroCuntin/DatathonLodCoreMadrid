# -*- coding: utf-8 -*-
"""
audit_f3_leakage.py - Auditoría de fuga de información (F3) del modelo M4.

Reproduce los experimentos "con y sin leakage" sobre el panel validado:
  - E1: variables crudas (sin scores)
  - E0: baseline M4 (4 scores + variables fisicas)
  - E2: baseline + score_holgura (formula completa)
  - E3: baseline + target (fuga trivial)
  - E4: baseline + nivel_idoneidad + ranking_ica (derivadas del target)
  - E5: baseline + poblacion_2031 (futuro de M3)

Para cada configuracion compara GroupKFold por comarca (honesto) con KFold
aleatorio (fuga espacial). Ademas calcula el sesgo de seleccion del piloto
frente a los municipios <50k del padron INE.

Uso:
    python scripts/audit_f3_leakage.py
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.metrics import mean_absolute_error, r2_score, root_mean_squared_error
from sklearn.model_selection import GroupKFold, KFold

ROOT = Path(__file__).resolve().parent.parent
TARGET = "indice_capacidad_global"

BASELINE = [
    "score_sanidad", "score_educacion", "score_conectividad", "score_vivienda",
    "hab_por_medico", "ocupacion_escolar_pct", "stock_vivienda_vacia_est",
    "suelo_urbano_disponible_m2",
]
RAW = [
    "poblacion_actual", "superficie_km2", "densidad", "tiempo_medio_madrid_minutos",
    "precio_m2_compra", "precio_m2_alquiler", "num_medicos_ap", "num_plazas_escolares",
    "num_alumnos_matriculados", "num_centros_salud", "num_centros_educativos",
    "paradas_x1000", "cobertura_fibra_pct", "stock_vivienda_vacia_est",
    "suelo_urbano_disponible_m2", "hab_por_medico", "ocupacion_escolar_pct",
]

CONFIGS = {
    "E1 CLEAN_RAW (sin scores)": RAW,
    "E0 BASELINE M4 (4 scores + fisicas)": BASELINE,
    "E2 BASELINE + score_holgura": BASELINE + ["score_holgura"],
    "E3 BASELINE + target": BASELINE + [TARGET],
    "E4 BASELINE + nivel_idoneidad + ranking_ica": BASELINE + ["_nivel_ord", "ranking_ica"],
    "E5 BASELINE + poblacion_2031": BASELINE + ["poblacion_2031"],
}


def evaluate(df: pd.DataFrame, features: list[str], cv: str) -> dict:
    X = df[features].to_numpy(float)
    y = df[TARGET].to_numpy(float)
    groups = df["comarca"].to_numpy()
    if cv == "group":
        splits = list(GroupKFold(n_splits=5).split(X, y, groups))
    else:
        splits = list(KFold(n_splits=5, shuffle=True, random_state=2026).split(X, y))
    oof = np.zeros(len(y))
    for train_idx, test_idx in splits:
        model = GradientBoostingRegressor(
            n_estimators=120, learning_rate=0.05, max_depth=3, random_state=2026
        )
        model.fit(X[train_idx], y[train_idx])
        oof[test_idx] = model.predict(X[test_idx])
    return {
        "r2_oof": round(float(r2_score(y, oof)), 4),
        "mae_oof": round(float(mean_absolute_error(y, oof)), 2),
        "rmse_oof": round(float(root_mean_squared_error(y, oof)), 2),
    }


def selection_bias(df: pd.DataFrame) -> dict:
    payload = json.loads(
        (ROOT / "data/raw/ine/ine_padron_2881_snapshot_20261024.json").read_text(encoding="utf-8")
    )
    pob = {}
    for serie in payload:
        meta = {m.get("T3_Variable"): m for m in serie.get("MetaData", [])}
        mun, sexo = meta.get("Municipios"), meta.get("Sexo")
        if not mun or not sexo or str(sexo.get("Codigo")) != "0":
            continue
        code = str(mun.get("Codigo", ""))
        if len(code) == 5 and code.startswith("28") and serie.get("Data"):
            latest = max(serie["Data"], key=lambda d: d.get("Anyo", 0))
            if latest.get("Valor") is not None:
                pob[code] = int(round(float(latest["Valor"])))
    allpop = pd.Series(pob)
    small = allpop[allpop < 50000]
    pilot = df["poblacion_actual"]
    return {
        "ine_total": int(len(allpop)),
        "ine_menores_50k": int(len(small)),
        "piloto_n": int(len(pilot)),
        "piloto_mediana": int(pilot.median()),
        "menores_50k_mediana": int(small.median()),
        "piloto_total_pob": int(pilot.sum()),
        "menores_50k_total_pob": int(small.sum()),
        "piloto_tramos": pd.cut(pilot, [0, 5000, 20000, 50000], right=False)
        .value_counts().sort_index().to_dict(),
        "menores_50k_tramos": pd.cut(small, [0, 5000, 20000, 50000], right=False)
        .value_counts().sort_index().to_dict(),
    }


def main() -> None:
    df = pd.read_csv(ROOT / "data/validated/municipios_panel_validado.csv")
    df["_nivel_ord"] = df["nivel_idoneidad"].map({"BAJA": 0, "MEDIA": 1, "ALTA": 2})

    print(f"{'Configuracion':52} {'CV':6} {'R2':>8} {'MAE':>7} {'RMSE':>7}")
    results = []
    for name, features in CONFIGS.items():
        for cv in ("group", "random"):
            r = evaluate(df, features, cv)
            results.append({"config": name, "cv": cv, "n_features": len(features), **r})
            print(f"{name:52} {cv:6} {r['r2_oof']:8.4f} {r['mae_oof']:7.2f} {r['rmse_oof']:7.2f}")

    print("\nCorrelacion con el target:")
    cols = BASELINE + ["score_holgura", "ranking_ica", "_nivel_ord", "poblacion_2031"]
    corr = df[cols + [TARGET]].corr()[TARGET].drop(TARGET).sort_values(ascending=False)
    for k, v in corr.items():
        print(f"  {k:32} {v: .4f}")

    print("\nSesgo de seleccion:")
    sb = selection_bias(df)
    for k, v in sb.items():
        print(f"  {k}: {v}")


if __name__ == "__main__":
    main()
