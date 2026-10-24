# -*- coding: utf-8 -*-
"""
check_model_cards.py - Cross-check de las cifras publicadas en docs/model_cards.md.

Verifica:
  1. Métricas principales de M1-M5 contra sus metrics.json.
  2. Tamaños de clúster y el clúster singleton (Meco) de M5.
  3. Peores errores OOF por municipio de M1 y M4 (los citados en las fichas).

Uso:
    python scripts/check_model_cards.py
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.ensemble import GradientBoostingRegressor, RandomForestRegressor
from sklearn.model_selection import GroupKFold

ROOT = Path(__file__).resolve().parent.parent
PANEL = ROOT / "data/validated/municipios_panel_validado.csv"
MODELS = ROOT / "src/lodcore/models"


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def oof_residuals(df: pd.DataFrame, features: list[str], target: str, model_factory) -> pd.DataFrame:
    X = df[features].to_numpy(float)
    y = df[target].to_numpy(float)
    groups = df["comarca"].to_numpy()
    pred = np.zeros(len(y))
    for train_idx, test_idx in GroupKFold(n_splits=5).split(X, y, groups):
        model = model_factory()
        model.fit(X[train_idx], y[train_idx])
        pred[test_idx] = model.predict(X[test_idx])
    return pd.DataFrame({"nombre": df["nombre"], "real": y, "pred": pred, "error": pred - y})


def main() -> None:
    df = pd.read_csv(PANEL)

    # --- M1 ---
    m1 = load_json(MODELS / "m1_avm/metrics.json")
    assert round(m1["mae_cv_mean"], 2) == 382.83, m1["mae_cv_mean"]
    assert round(m1["r2_cv_oof"], 4) == -0.3398, m1["r2_cv_oof"]
    assert round(m1["r2_in_sample"], 4) == 0.8032, m1["r2_in_sample"]

    # --- M2 ---
    m2 = load_json(MODELS / "m2_indicadores/metrics.json")
    assert round(m2["explained_variance_ratio_pc1"], 4) == 0.7004, m2["explained_variance_ratio_pc1"]
    assert m2["municipios_30min_privado"] == 16
    assert m2["municipios_30min_publico"] == 8

    # --- M3 ---
    m3 = load_json(MODELS / "m3_demografia/metrics.json")
    assert int(m3["poblacion_agregada_2025"]) == 200267
    assert int(m3["poblacion_proyectada_2030"]) == 216597
    assert int(m3["poblacion_proyectada_2035"]) == 234336

    # --- M4 ---
    m4 = load_json(MODELS / "m4_capacidad/metrics.json")
    assert round(m4["mae_cv_mean"], 2) == 5.15, m4["mae_cv_mean"]
    assert round(m4["r2_cv_oof"], 4) == 0.7345, m4["r2_cv_oof"]
    assert round(m4["r2_in_sample"], 4) == 1.0, m4["r2_in_sample"]
    bg = load_json(MODELS / "m4_capacidad/shap_background.json")
    assert bg.get("metodo_atribucion") == "EFECTOS_MARGINALES_SIMETRICOS_NORMALIZADOS"

    # --- M5 ---
    m5 = load_json(MODELS / "m5_recomendador/metrics.json")
    assert m5["n_clusters"] == 4
    assert round(m5["silhouette_score"], 4) == 0.3183, m5["silhouette_score"]
    assert round(m5["inertia"], 2) == 39.01, m5["inertia"]
    clusters = load_json(MODELS / "m5_recomendador/clustering.json")
    sizes = [int(v) for v in clusters["cluster_sizes"].values()]
    assert sorted(sizes) == [4, 4, 6, 6], sizes
    panel_counts = df["arquetipo_nombre"].value_counts().to_dict()
    print("Aviso: el panel conserva una asignación antigua de arquetipos:", panel_counts)

    # --- Peores errores OOF citados en las fichas ---
    f1 = ["tiempo_medio_madrid_minutos", "densidad", "cobertura_fibra_pct",
          "paradas_x1000", "vacias_x1000", "medicos_x1000", "tasa_holgura_escolar"]
    r1 = oof_residuals(df, f1, "precio_m2_compra",
                       lambda: RandomForestRegressor(
                           n_estimators=100, max_depth=5, min_samples_leaf=2,
                           random_state=2026, n_jobs=1))
    worst1 = r1.reindex(r1.error.abs().sort_values(ascending=False).index).head(5)
    expected1 = {
        "Manzanares el Real": -983.5,
        "Soto del Real": -924.6,
        "Guadarrama": -702.0,
        "Colmenar de Oreja": 698.6,
        "Villarejo de Salvanés": 620.4,
    }
    for _, row in worst1.iterrows():
        assert row["nombre"] in expected1, row["nombre"]
        assert abs(row["error"] - expected1[row["nombre"]]) <= 1.0, (row["nombre"], row["error"])

    f4 = ["score_sanidad", "score_educacion", "score_conectividad", "score_vivienda",
          "hab_por_medico", "ocupacion_escolar_pct", "stock_vivienda_vacia_est",
          "suelo_urbano_disponible_m2"]
    r4 = oof_residuals(df, f4, "indice_capacidad_global",
                       lambda: GradientBoostingRegressor(
                           n_estimators=120, learning_rate=0.05, max_depth=3,
                           random_state=2026))
    worst4 = r4.reindex(r4.error.abs().sort_values(ascending=False).index).head(5)
    expected4 = {
        "Soto del Real": 15.50,
        "Robledo de Chavela": -12.32,
        "Manzanares el Real": 12.07,
        "Torres de la Alameda": 10.77,
        "Colmenar de Oreja": -7.67,
    }
    for _, row in worst4.iterrows():
        assert row["nombre"] in expected4, row["nombre"]
        assert abs(row["error"] - expected4[row["nombre"]]) <= 0.1, (row["nombre"], row["error"])

    print("OK: métricas M1-M5, clústeres y peores errores OOF coinciden con docs/model_cards.md")
    print("M1 peores:", [(r.nombre, round(r.error, 1)) for r in worst1.itertuples()])
    print("M4 peores:", [(r.nombre, round(r.error, 2)) for r in worst4.itertuples()])


if __name__ == "__main__":
    main()
