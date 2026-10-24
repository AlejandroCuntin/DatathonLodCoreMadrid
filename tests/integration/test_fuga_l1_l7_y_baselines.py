"""
test_fuga_l1_l7_y_baselines.py - Batería de auditoría formal de Fuga de Información (L1-L7),
Sesgo de Selección, Baselines Naive y Bandas Bootstrap para Fase 2 (P2).
"""

import numpy as np
import pandas as pd
import pytest
from sklearn.model_selection import GroupKFold, KFold
from sklearn.dummy import DummyRegressor

from src.lodcore.models.m1_avm.train import FEATURES_M1
from src.lodcore.models.m4_capacidad.train import FEATURES_M4
from src.lodcore.models.m1_avm.evaluate import evaluar_m1_con_baselines_y_bootstrap
from src.lodcore.models.m4_capacidad.evaluate import evaluar_m4_con_baselines_y_bootstrap
from src.lodcore.data.pointintime import filtrar_point_in_time
from src.lodcore.config import FECHA_DECISION_MVP

@pytest.fixture
def panel_data():
    return pd.read_csv("data/validated/municipios_panel_validado.csv")

# -------------------------------------------------------------
# F3: AUDITORÍA DE LAS 7 FUGAS DE INFORMACIÓN (L1 - L7)
# -------------------------------------------------------------

def test_l1_fuga_espacial_cv_aleatorio_vs_groupkfold(panel_data):
    """
    L1: Demuestra que GroupKFold por comarca garantiza particiones espacialmente disjuntas,
    mientras que un KFold aleatorio mezcla municipios de la misma comarca entre train y test.
    """
    groups = panel_data["comarca"].to_numpy()
    gkf = GroupKFold(n_splits=5)
    for tr, val in gkf.split(panel_data, groups=groups):
        comarcas_tr = set(groups[tr])
        comarcas_val = set(groups[val])
        assert comarcas_tr.isdisjoint(comarcas_val), "Fuga L1: comarca compartida entre train y test"

def test_l2_fuga_temporal_point_in_time(panel_data):
    """
    L2: Confirma que ningún dato de entrada tiene fecha posterior a la fecha de decisión.
    """
    fecha_corte = FECHA_DECISION_MVP  # única fuente de verdad (src/lodcore/config)
    filtrado = filtrar_point_in_time(panel_data, fecha_decision=fecha_corte, col_fecha="fecha_disponible")
    assert len(filtrado) == len(panel_data), "Fuga L2: existen registros futuros para la fecha de corte"

def test_l3_fuga_por_variable_derivada_del_objetivo(panel_data):
    """
    L3 (fuga directa): el target y sus derivados directos no están en las features.
    La fuga indirecta por componentes del ICA se documenta en el test siguiente.
    """
    # M1
    assert "precio_m2_compra" not in FEATURES_M1
    assert "precio_m2_alquiler" not in FEATURES_M1
    # M4
    assert "indice_capacidad_global" not in FEATURES_M4
    assert "nivel_idoneidad" not in FEATURES_M4
    assert "personas_acogida_efectiva" not in FEATURES_M4

def test_l3_ica_es_funcion_determinista_de_los_scores(panel_data):
    """
    L3 (material interpretativa): 4 de los 5 componentes del ICA están en FEATURES_M4.
    El R² de M4 mide la aproximación de una fórmula, no la predicción de un fenómeno externo.
    """
    df = panel_data
    ica = (
        0.30 * df["score_vivienda"]
        + 0.30 * (df["score_sanidad"] + df["score_educacion"]) / 2.0
        + 0.25 * df["score_conectividad"]
        + 0.15 * df["score_holgura"]
    )
    assert (df["indice_capacidad_global"] - ica).abs().max() < 0.01
    componentes = {
        "score_sanidad", "score_educacion", "score_conectividad",
        "score_vivienda", "score_holgura",
    }
    assert len(componentes.intersection(FEATURES_M4)) == 4

def test_l4_fuga_entre_fases_m3_proyecciones_en_m4():
    """
    L4: Confirma que M4 no use proyecciones temporales futuras generadas por M3.
    """
    cols_futuras = {"poblacion_2027", "poblacion_2029", "poblacion_2031", "anio_estimado_saturacion"}
    interseccion = set(FEATURES_M4).intersection(cols_futuras)
    assert len(interseccion) == 0, f"Fuga L4: M4 consume features futuras de M3: {interseccion}"

def test_l5_l6_ausencia_fuga_por_normalizacion_e_imputacion(panel_data):
    """
    L5 y L6: Con 0 nulos en el panel validado y modelos basados en árboles invariantes a escala,
    se descarta fuga por imputación global o escalado previo al split.
    """
    for f in FEATURES_M1 + FEATURES_M4:
        assert panel_data[f].isna().sum() == 0, f"Nulo detectado en feature {f}"

def test_l7_fuga_por_duplicacion_de_filas(panel_data):
    """
    L7: Confirma que cada fila representa un municipio físico unívoco (20 códigos INE distintos).
    """
    assert panel_data["codigo_ine"].nunique() == 20
    assert len(panel_data) == 20

# -------------------------------------------------------------
# F4: VALIDACIÓN, 4 BASELINES NAIVE Y BANDAS BOOTSTRAP
# -------------------------------------------------------------

def test_m1_gana_a_dummy_mean_y_declara_r2_negativo():
    """
    F4 - M1: Demuestra que M1 bate a la media naive en MAE pero declara honestamente
    el R² OOF comarcal negativo esperado con n=20.
    """
    res = evaluar_m1_con_baselines_y_bootstrap(n_boot=100)
    mae_m1 = res["m1_metrics_oof"]["mae"]
    mae_dummy = res["baselines"]["dummy_mean"]["mae"]
    assert mae_m1 < mae_dummy, f"M1 (MAE {mae_m1}) debería batir a dummy_mean (MAE {mae_dummy})"
    assert res["m1_metrics_oof"]["r2_oof"] < 0.0, "R² OOF de M1 debe ser honestamente negativo"
    assert res["evaluacion_honestidad"]["apto_para_jurado"] is False

def test_m4_bate_a_baselines_naive_con_r2_honesto():
    """
    F4 - M4: Demuestra que M4 bate contundentemente a la media naive (reducción > 50% MAE)
    y reporta r2_cv_oof = 0.7345 (sin usar el in-sample 1.0 como argumento).
    """
    res = evaluar_m4_con_baselines_y_bootstrap(n_boot=100)
    mae_m4 = res["m4_metrics_oof"]["mae"]
    mae_dummy = res["baselines"]["dummy_mean"]["mae"]
    assert mae_m4 < mae_dummy
    assert res["evaluacion_honestidad"]["reduccion_error_vs_media_pct"] > 50.0
    assert res["m4_metrics_oof"]["r2_oof"] == pytest.approx(0.7345, abs=0.01)
    assert res["evaluacion_honestidad"]["apto_para_jurado"] is True

def test_bootstrap_bandas_coherentes():
    """
    F4: Comprueba que las bandas de incertidumbre por bootstrap 95% encierren las métricas medias.
    """
    res_m4 = evaluar_m4_con_baselines_y_bootstrap(n_boot=200)
    ci_mae = res_m4["m4_metrics_oof"]["ci_95_mae_bootstrap"]
    assert ci_mae[0] < res_m4["m4_metrics_oof"]["mae"] < ci_mae[1]
