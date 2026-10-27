"""M6 · Predicción de tendencia de población a un año objetivo (modelo ONNX).

Idea: un único modelo de horizonte directo. Dado el estado actual de un municipio (características en el año
de origen t) y un horizonte h (años hasta el año objetivo), predice y = ln(P[t+h] / P[t]).
    población_objetivo = población_actual * exp(y)        con h = año_objetivo - año_origen (1..h_max)

Entrena sobre TODOS los municipios del Padrón (no solo los 20 del panel): son miles de pares
(municipio, año de origen, horizonte). Se evalúa con un backtest temporal contra dos referencias
(sin cambio y extrapolación geométrica CAGR a 5 años, que es la lógica de M3) y se publica una banda de
incertidumbre del 95 % por horizonte (residuos fuera de muestra).

Salidas:
    oracle/onnx/m6_proyeccion.onnx            modelo para cargar en la base de datos
    oracle/onnx/m6_proyeccion.metadata.json   columnas de entrada, bandas, métricas y procedencia
    data/validated/m6_entradas_actuales.csv   datos actuales (características en el último año) por municipio
    data/output/m6_metricas.json              métricas del entrenamiento

Alcance: es una predicción de tendencias a partir de la serie histórica de población. No simula inversiones ni
cambios en los servicios y no calcula el ICA (eso corresponde al simulador completo, en una fase posterior).
"""
from __future__ import annotations

import json
import time
from datetime import date
from pathlib import Path

import numpy as np
import pandas as pd

from ...data.panel_proyeccion import (FEATURES, a_ancho, cargar_padron_raw, entradas_actuales,
                                      pares_entrenamiento, recortar_a_tramo_contiguo, unir_codigo_ine,
                                      validar_padron)
from ...ingest.descarga_historica import raiz_proyecto

VERSION = "1.0.0"
DEFECTOS = {
    "h_max": 15,              # hasta 15 años vista: con último año 2025 se proyecta hasta 2040
    "n_estimators": 300,
    "max_depth": 3,
    "learning_rate": 0.05,
    "subsample": 0.8,
    "min_samples_leaf": 20,
    "seed": 2026,
    "cv_folds": 5,
    "anios_backtest": 5,      # año de corte del backtest = último año - 5
    "min_anios": 12,
    "min_municipios": 100,
    "target_opset": 15,       # ajustar al mismo valor que use src/lodcore/models/base.py
}


def cargar_params(raiz: Path) -> dict:
    p = dict(DEFECTOS)
    ruta = Path(raiz) / "params.yaml"
    if ruta.exists():
        try:
            import yaml
            cfg = yaml.safe_load(ruta.read_text(encoding="utf-8")) or {}
            p.update(cfg.get("m6_proyeccion", {}) or {})
        except Exception:  # params.yaml ilegible: se usan los valores por defecto
            pass
    return p


def _nuevo_modelo(p: dict):
    from sklearn.ensemble import GradientBoostingRegressor

    return GradientBoostingRegressor(
        n_estimators=int(p["n_estimators"]), max_depth=int(p["max_depth"]), learning_rate=float(p["learning_rate"]),
        subsample=float(p["subsample"]), min_samples_leaf=int(p["min_samples_leaf"]), random_state=int(p["seed"]))


def _mape(yhat, y) -> float:
    """Error porcentual medio de la POBLACIÓN: |P_pred - P_real| / P_real = |exp(yhat - y) - 1|."""
    return float(np.mean(np.abs(np.exp(np.asarray(yhat) - np.asarray(y)) - 1)) * 100)


def backtest(P: pd.DataFrame, p: dict) -> dict:
    """Origen = año de corte; se entrena solo con pares cuyo objetivo cae en o antes del corte."""
    ultimo = int(P.columns.max())
    corte = ultimo - int(p["anios_backtest"])
    pares = pares_entrenamiento(P, int(p["h_max"]))
    train = pares[pares["anio_origen"] + pares["h"] <= corte]
    test = pares[pares["anio_origen"] == corte]
    if train.empty or test.empty:
        raise ValueError(f"Histórico insuficiente para un backtest con corte en {corte}")
    modelo = _nuevo_modelo(p).fit(train[FEATURES], train["y"])
    pred = pd.Series(modelo.predict(test[FEATURES]), index=test.index)
    por_h = {}
    for h, g in test.groupby("h"):
        por_h[int(h)] = {
            "modelo": _mape(pred.loc[g.index], g["y"]),
            "cagr5": _mape(g["g5"] * g["h"], g["y"]),
            "sin_cambio": _mape(np.zeros(len(g)), g["y"]),
        }
    medias = {k: float(np.mean([v[k] for v in por_h.values()])) for k in ("modelo", "cagr5", "sin_cambio")}
    return {"anio_corte": corte, "n_train": int(len(train)), "n_test": int(len(test)),
            "mape_pct_por_horizonte": por_h, "mape_pct_medio": medias,
            "bate_cagr5": bool(medias["modelo"] < medias["cagr5"]),
            "bate_sin_cambio": bool(medias["modelo"] < medias["sin_cambio"])}


def cv_oof(pares: pd.DataFrame, p: dict) -> tuple[dict, dict]:
    """Validación cruzada dejando municipios fuera (no es temporal: el backtest es la métrica honesta).
    Devuelve (métricas, bandas del 95 % por horizonte sobre ln(P[t+h]/P[t]))."""
    from sklearn.metrics import r2_score
    from sklearn.model_selection import GroupKFold, cross_val_predict

    grupos = pares["clave"]
    k = max(2, min(int(p["cv_folds"]), int(grupos.nunique())))
    oof = cross_val_predict(_nuevo_modelo(p), pares[FEATURES], pares["y"], groups=grupos, cv=GroupKFold(n_splits=k))
    res = pares["y"].to_numpy() - oof
    h = pares["h"].to_numpy()
    bandas = {}
    for hh in range(1, int(p["h_max"]) + 1):
        r = res[h == hh]
        if len(r) < 30:
            r = res[np.abs(h - hh) <= 1]
        if len(r):
            bandas[str(hh)] = [float(np.quantile(r, 0.025)), float(np.quantile(r, 0.975))]
    return {"r2_cv_oof": float(r2_score(pares["y"], oof)), "folds": int(k)}, bandas


def exportar_onnx(modelo, ruta: Path, n_features: int, target_opset: int = 15) -> None:
    from skl2onnx import convert_sklearn
    from skl2onnx.common.data_types import FloatTensorType

    onx = convert_sklearn(modelo, initial_types=[("float_input", FloatTensorType([None, n_features]))],
                          target_opset={"": int(target_opset), "ai.onnx.ml": 3})
    Path(ruta).parent.mkdir(parents=True, exist_ok=True)
    Path(ruta).write_bytes(onx.SerializeToString())


def verificar_onnx(modelo, ruta: Path, X, atol: float = 1e-4) -> dict:
    """Equivalencia sklearn <-> ONNX Runtime (float32)."""
    import onnxruntime as ort

    sesion = ort.InferenceSession(str(ruta), providers=["CPUExecutionProvider"])
    entrada = sesion.get_inputs()[0].name
    Xf = np.asarray(X, dtype=np.float32)
    onnx_pred = np.asarray(sesion.run(None, {entrada: Xf})[0]).ravel()
    sk_pred = modelo.predict(Xf.astype(np.float64))
    err = np.abs(onnx_pred - sk_pred)
    return {"max_abs": float(err.max()), "max_rel": float(np.max(err / np.maximum(np.abs(sk_pred), 1e-9))),
            "filas": int(len(Xf)), "ok": bool(err.max() <= atol)}


def ejecutar(raiz: Path | None = None, params: dict | None = None, exportar: bool = True, log=print) -> dict:
    raiz = Path(raiz) if raiz else raiz_proyecto()
    p = {**cargar_params(raiz), **(params or {})}
    t0 = time.time()

    log("[M6 1/5] Cargando y validando el padrón histórico")
    df = cargar_padron_raw(raiz / "data" / "raw")
    df, descartados = recortar_a_tramo_contiguo(df)
    if descartados:
        log(f"         AVISO: hueco en la serie del INE; se usa el tramo contiguo {int(df['anio'].min())}-"
            f"{int(df['anio'].max())} y se descartan los años {descartados} (no se inventan datos)")
    informe = validar_padron(df, min_anios=int(p["min_anios"]), min_municipios=int(p["min_municipios"]))
    log(f"         {informe['municipios']} municipios · {informe['anio_min']}-{informe['anio_max']} · "
        f"{informe['celdas_vacias_pct']} % celdas vacías")

    log("[M6 2/5] Construyendo pares (municipio, año de origen, horizonte)")
    P = a_ancho(df)
    pares = pares_entrenamiento(P, int(p["h_max"]))
    ultimo = int(P.columns.max())
    log(f"         {len(pares)} pares · horizontes 1-{int(p['h_max'])} · proyectable hasta {ultimo + int(p['h_max'])}")

    log("[M6 3/5] Backtest temporal y validación cruzada")
    bt = backtest(P, p)
    m = bt["mape_pct_medio"]
    log(f"         MAPE medio de población tras corte {bt['anio_corte']}: modelo {m['modelo']:.2f} % · "
        f"CAGR5 {m['cagr5']:.2f} % · sin cambio {m['sin_cambio']:.2f} %")
    if not bt["bate_cagr5"]:
        log("         AVISO: el modelo NO mejora a la extrapolación CAGR5; hay que declararlo en la presentación")
    cv, bandas = cv_oof(pares, p)
    log(f"         r2_cv_oof (municipios fuera) = {cv['r2_cv_oof']:.3f}")

    log("[M6 4/5] Entrenando el modelo final y preparando los datos actuales")
    final = _nuevo_modelo(p).fit(pares[FEATURES], pares["y"])
    entradas, sin_cruce = unir_codigo_ine(entradas_actuales(P, df),
                                          raiz / "data" / "validated" / "municipios_panel_validado.csv")
    if sin_cruce:
        log(f"         AVISO: municipios del panel sin cruce por nombre con el padrón: {sin_cruce}")
    (raiz / "data" / "validated").mkdir(parents=True, exist_ok=True)
    (raiz / "data" / "output").mkdir(parents=True, exist_ok=True)
    cols = ["clave", "municipio", "codigo_ine", "anio_origen", "poblacion_actual", "ln_pob", "g1", "g3", "g5", "vol5"]
    entradas[[c for c in cols if c in entradas.columns]].to_csv(
        raiz / "data" / "validated" / "m6_entradas_actuales.csv", index=False, encoding="utf-8")

    resumen = {"version": VERSION, "generado": date.today().isoformat(), "padron": informe,
               "parametros": {k: p[k] for k in DEFECTOS}, "backtest": bt, "validacion_cruzada": cv,
               "sin_cruce_panel": sin_cruce, "segundos": round(time.time() - t0, 1)}
    (raiz / "data" / "output" / "m6_metricas.json").write_text(
        json.dumps(resumen, ensure_ascii=False, indent=2), encoding="utf-8")

    salida = {"metricas": resumen, "onnx": None}
    if exportar:
        log("[M6 5/5] Exportando a ONNX y verificando equivalencia")
        ruta = raiz / "oracle" / "onnx" / "m6_proyeccion.onnx"
        exportar_onnx(final, ruta, len(FEATURES), int(p["target_opset"]))
        muestra = pares[FEATURES].sample(min(2000, len(pares)), random_state=int(p["seed"]))
        ver = verificar_onnx(final, ruta, muestra)
        log(f"         error máx. |sklearn - ONNX| = {ver['max_abs']:.2e}")
        if not ver["ok"]:
            raise RuntimeError(f"El ONNX no reproduce al modelo de Python: {ver}")
        meta = {
            "modelo": "m6_proyeccion", "version": VERSION, "generado": date.today().isoformat(),
            "descripcion": "Predicción de tendencia de población a un año objetivo (horizonte directo)",
            "entradas": FEATURES, "tensor_entrada": "float_input", "salida": "variable",
            "objetivo": "ln(poblacion[t+h] / poblacion[t])",
            "uso": "poblacion_objetivo = poblacion_actual * EXP(prediccion); h = anio_objetivo - anio_origen",
            "anio_origen": ultimo, "h_min": 1, "h_max": int(p["h_max"]), "anio_max_proyectable": ultimo + int(p["h_max"]),
            "bandas_residuo_log_95": bandas,
            "origen": "PROYECTADO",
            "metodo": "GradientBoostingRegressor de horizonte directo sobre el log-crecimiento del Padrón (INE 2881)",
            "dataset_version": f"padron-{informe['anio_min']}-{informe['anio_max']}",
            "target_opset": int(p["target_opset"]),
            "metricas": {"backtest": bt["mape_pct_medio"], "bate_cagr5": bt["bate_cagr5"], **cv},
            "verificacion_onnx": ver,
            "limitaciones": ["Predicción de tendencia a partir de la serie de población del Padrón",
                             "No modela inversiones, políticas ni cambios en los servicios",
                             "No calcula el ICA (corresponde al simulador completo)"],
        }
        (raiz / "oracle" / "onnx" / "m6_proyeccion.metadata.json").write_text(
            json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")
        salida["onnx"] = str(ruta)
    else:
        log("[M6 5/5] Exportación a ONNX omitida (exportar=False)")
    return salida


if __name__ == "__main__":
    ejecutar()
