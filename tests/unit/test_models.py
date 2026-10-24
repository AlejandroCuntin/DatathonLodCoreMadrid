"""
test_models.py - Pruebas unitarias y funcionales para M1..M5, explicabilidad sin causalidad,
reglas duras de no-compensatoriedad y endpoints FastAPI N3 (/recomendar, /whatif, /optimizar-presupuesto).
"""

import pytest
from fastapi.testclient import TestClient

from src.lodcore.models.m4_capacidad.reglas_no_compensatorias import aplicar_salvaguarda_no_compensatoria
from src.lodcore.explain.redaccion_natural import (
    verificar_ausencia_causalidad,
    redactar_explicacion_shap,
)
from src.lodcore.serving.fastapi.app import app

client = TestClient(app)

def test_salvaguarda_no_compensatoria_colapso_sanitario():
    muni_colapsado = {
        "nombre": "Municipio Prueba Colapso",
        "hab_por_medico": 1680.0,
        "ocupacion_escolar_pct": 72.0,
        "indice_capacidad_global": 88.5
    }
    res = aplicar_salvaguarda_no_compensatoria(muni_colapsado)
    assert res["alerta_no_compensatoria"] is True
    assert res["semaforo_ica"] == "BAJA"
    assert res["indice_capacidad_ajustado"] < 40.0

def test_salvaguarda_no_compensatoria_colapso_educativo():
    muni_colapsado = {
        "nombre": "Municipio Prueba Aulas",
        "hab_por_medico": 900.0,
        "ocupacion_escolar_pct": 97.4,
        "indice_capacidad_global": 79.0
    }
    res = aplicar_salvaguarda_no_compensatoria(muni_colapsado)
    assert res["alerta_no_compensatoria"] is True
    assert res["semaforo_ica"] == "BAJA"
    assert res["indice_capacidad_ajustado"] < 40.0

def test_salvaguarda_no_compensatoria_no_muta_entrada():
    muni = {
        "hab_por_medico": 900.0,
        "ocupacion_escolar_pct": 80.0,
        "indice_capacidad_global": 70.0
    }
    aplicar_salvaguarda_no_compensatoria(muni)
    assert "indice_capacidad_ajustado" not in muni
    assert "alerta_no_compensatoria" not in muni

def test_salvaguarda_no_compensatoria_exige_campos():
    with pytest.raises(ValueError):
        aplicar_salvaguarda_no_compensatoria({"indice_capacidad_global": 70.0})

def test_redaccion_no_atribuye_regla_dura_por_redondeo():
    texto = redactar_explicacion_shap(
        municipio="Municipio Prueba",
        score_predicho=70.004,
        ic_95_inf=68.0,
        ic_95_sup=72.0,
        base_value=65.0,
        contribuciones=[
            {"feature": "score_sanidad", "feature_value": 80.0, "shap_value": 3.0},
            {"feature": "score_vivienda", "feature_value": 30.0, "shap_value": -1.0},
        ],
        alerta_no_compensatoria=False,
        score_ajustado=70.0,
    )
    assert "regla dura" not in texto
    assert verificar_ausencia_causalidad(texto) is True

def test_detector_lenguaje_causal():
    texto_valido = "El modelo asocia una aportación positiva con el sub-índice sanitario."
    assert verificar_ausencia_causalidad(texto_valido) is True

    with pytest.raises(ValueError):
        verificar_ausencia_causalidad("El déficit de médicos causa el colapso del municipio.")

def test_fastapi_n3_recomendar_endpoint():
    payload = {
        "peso_sanidad": 0.35,
        "peso_educacion": 0.35,
        "peso_conectividad": 0.15,
        "peso_vivienda": 0.15,
        "presupuesto_max_m2": 1800.0,
        "tiempo_max_madrid_min": 65,
        "top_k": 3
    }
    resp = client.post("/recomendar", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert len(data["ranking"]) == 3
    assert data["origen"] == "ESTIMADO"
    assert data["dataset_version"] == "v1.0.0-F2"
    # Verificar orden decreciente de afinidad
    assert data["ranking"][0]["afinidad_mcdm_pct"] >= data["ranking"][1]["afinidad_mcdm_pct"]

def test_fastapi_n3_whatif_endpoint():
    payload = {
        "id_municipio": 14, # Robledo de Chavela
        "nuevos_residentes": 1200,
        "nuevos_medicos_ap": 1,
        "nuevas_plazas_escolares": 150,
        "inversion_conectividad_eur": 250000.0
    }
    resp = client.post("/whatif", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert data["id_municipio"] == 14
    assert data["origen"] == "SIMULADO"
    sim = data["estado_simulado"]
    assert "ic_95_inferior" in sim and "ic_95_superior" in sim
    assert sim["ic_95_inferior"] <= sim["indice_ica_ajustado"] <= sim["ic_95_superior"]
    assert "shap_recalculado" in sim
    assert verificar_ausencia_causalidad(sim["explicacion_natural_es"]) is True

def test_fastapi_n3_whatif_municipio_inexistente_404():
    resp = client.post("/whatif", json={"id_municipio": 99999})
    assert resp.status_code == 404
    assert "No existe el municipio" in resp.json()["detail"]

def test_fastapi_n3_optimizar_presupuesto_endpoint():
    payload = {
        "comarca": "Sierra Oeste",
        "presupuesto_total_eur": 2500000.0
    }
    resp = client.post("/optimizar-presupuesto", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert data["comarca"] == "Sierra Oeste"
    assert data["presupuesto_total_eur"] == 2500000.0
    assert data["presupuesto_utilizado_eur"] <= 2500000.0
    assert data["origen"] == "SIMULADO"
    assert len(data["asignaciones"]) > 0
