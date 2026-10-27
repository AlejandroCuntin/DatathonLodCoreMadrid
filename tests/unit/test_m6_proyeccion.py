"""Pruebas del modelo M6 (proyección de población). No necesitan red ni Oracle."""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

RAIZ = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(RAIZ))
try:
    from src.lodcore.data import panel_proyeccion as panel
    from src.lodcore.ingest import descarga_historica as desc
    from src.lodcore.models.m6_proyeccion import train as m6
except ModuleNotFoundError:
    sys.path.insert(0, str(RAIZ / "src"))
    from lodcore.data import panel_proyeccion as panel
    from lodcore.ingest import descarga_historica as desc
    from lodcore.models.m6_proyeccion import train as m6

PARAMS_RAPIDOS = {"n_estimators": 60, "min_municipios": 20, "cv_folds": 3, "h_max": 10}


def padron_sintetico(n=40, anio0=1996, anio1=2025, seed=1) -> pd.DataFrame:
    """Municipios con crecimiento persistente (AR(1) sobre el log-crecimiento)."""
    rng = np.random.default_rng(seed)
    filas = []
    for i in range(n):
        p, mu, e = rng.uniform(500, 40000), rng.normal(0.01, 0.015), 0.0
        for a in range(anio0, anio1 + 1):
            e = 0.6 * e + rng.normal(0, 0.01)
            p *= np.exp(mu + e)
            nombre = f"Municipio {i:03d}"
            filas.append((a, nombre, desc.normalizar_nombre(nombre), None, round(p)))
    df = pd.DataFrame(filas, columns=["anio", "municipio", "clave", "codigo_ine", "poblacion"])
    df["fuente"], df["tabla_ine"], df["snapshot"] = "test", 2881, "sintetico"
    return df


def test_normalizar_nombre():
    assert desc.normalizar_nombre("Molar (El)") == "el molar"
    assert desc.normalizar_nombre("Molar, El") == "el molar"
    assert desc.normalizar_nombre("El Molar") == "el molar"
    assert desc.normalizar_nombre("Rascafría") == "rascafria"
    assert desc.normalizar_nombre("San Martín de Valdeiglesias") == "san martin de valdeiglesias"


def _serie(nombre, datos):
    return {"Nombre": nombre, "Data": [{"Anyo": a, "Valor": v} for a, v in datos]}


def test_parsear_padron_usa_solo_series_total():
    series = [
        _serie("Alcobendas. Total. Total.", [(2024, 120000), (2025, 121000)]),
        _serie("Alcobendas. Hombres. Total.", [(2024, 58000), (2025, 58500)]),   # se descarta
        _serie("Molar (El). Total.", [(2024, 9900), (2025, 10000)]),
        _serie("Total. Total.", [(2024, 7000000), (2025, 7100000)]),            # total provincial: se descarta
        _serie("28006 Cercedilla. Total.", [(2025, 7772)]),
    ]
    df = desc.parsear_padron(series)
    assert sorted(df["clave"].unique()) == ["alcobendas", "cercedilla", "el molar"]
    assert int(df.loc[df["clave"] == "cercedilla", "codigo_ine"].iloc[0]) == 28006
    assert len(df) == 5


def test_parsear_padron_detecta_series_duplicadas_y_vacias():
    dup = [_serie("Alcobendas. Total.", [(2025, 1)]), _serie("Alcobendas. Total. Total.", [(2025, 2)])]
    with pytest.raises(ValueError):
        desc.parsear_padron(dup)
    with pytest.raises(ValueError):
        desc.parsear_padron([_serie("Alcobendas. Hombres.", [(2025, 1)])])


def test_validar_padron_acepta_datos_buenos_y_rechaza_malos():
    df = padron_sintetico()
    assert panel.validar_padron(df, min_municipios=20)["municipios"] == 40
    malo = df.copy()
    malo.loc[0, "poblacion"] = -5
    with pytest.raises(ValueError):
        panel.validar_padron(malo, min_municipios=20)
    with pytest.raises(ValueError):
        panel.validar_padron(df[df["anio"] >= 2020], min_municipios=20)   # pocos años


def test_features_punto_en_tiempo():
    """Cambiar datos POSTERIORES a t no puede alterar las características en t."""
    P = panel.a_ancho(padron_sintetico())
    t = 2015
    antes = panel.features_en(P, t)
    P2 = P.astype(float)
    for c in [c for c in P2.columns if c > t]:
        P2[c] = P2[c] * 3.0
    pd.testing.assert_frame_equal(antes, panel.features_en(P2, t))


def test_objetivo_de_los_pares():
    P = panel.a_ancho(padron_sintetico())
    pares = panel.pares_entrenamiento(P, 10)
    fila = pares.sample(1, random_state=0).iloc[0]
    t, h, clave = int(fila["anio_origen"]), int(fila["h"]), fila["clave"]
    assert fila["y"] == pytest.approx(np.log(P.loc[clave, t + h] / P.loc[clave, t]))
    assert (pares["anio_origen"] + pares["h"] <= P.columns.max()).all()


def test_backtest_mejora_a_no_cambiar_nada():
    P = panel.a_ancho(padron_sintetico(n=60))
    p = {**m6.DEFECTOS, **PARAMS_RAPIDOS}
    bt = m6.backtest(P, p)
    assert bt["anio_corte"] == 2020
    assert bt["bate_sin_cambio"] is True
    assert set(bt["mape_pct_medio"]) == {"modelo", "cagr5", "sin_cambio"}


def test_pipeline_completo_sin_onnx(tmp_path):
    raw = tmp_path / "data" / "raw"
    raw.mkdir(parents=True)
    (tmp_path / "params.yaml").write_text("m6_proyeccion: {}\n", encoding="utf-8")
    df = padron_sintetico(n=40)
    for anio, g in df.groupby("anio"):
        g.to_csv(raw / f"{anio}_raw_ine_padron.csv", index=False)
    res = m6.ejecutar(raiz=tmp_path, params=PARAMS_RAPIDOS, exportar=False, log=lambda *_: None)
    assert (tmp_path / "data" / "output" / "m6_metricas.json").exists()
    entradas = pd.read_csv(tmp_path / "data" / "validated" / "m6_entradas_actuales.csv")
    assert len(entradas) == 40 and {"poblacion_actual", "g5", "vol5"} <= set(entradas.columns)
    assert res["onnx"] is None


def test_onnx_equivalente_a_sklearn(tmp_path):
    pytest.importorskip("skl2onnx")
    pytest.importorskip("onnxruntime")
    P = panel.a_ancho(padron_sintetico())
    p = {**m6.DEFECTOS, **PARAMS_RAPIDOS}
    pares = panel.pares_entrenamiento(P, p["h_max"])
    modelo = m6._nuevo_modelo(p).fit(pares[panel.FEATURES], pares["y"])
    ruta = tmp_path / "m6.onnx"
    m6.exportar_onnx(modelo, ruta, len(panel.FEATURES), p["target_opset"])
    assert m6.verificar_onnx(modelo, ruta, pares[panel.FEATURES].head(500))["ok"]
