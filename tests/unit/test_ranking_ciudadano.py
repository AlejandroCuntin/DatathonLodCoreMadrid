"""
test_ranking_ciudadano.py - Pruebas del motor de ranking del perfil ciudadano (C2).

Cubre las reglas que el producto no puede romper:
  - Los pesos suman 1,0 y respetan los limites.
  - El presupuesto y el tiempo filtran, y se reporta el motivo.
  - Un municipio colapsado NO se elimina: se marca y se le aplica el techo.
  - El orden es determinista.
  - La familia prioriza educacion y el senior sanidad.
  - El ranking no muta las filas de entrada ni el ICA.
  - El analisis de sensibilidad devuelve valores validos.
  - El panel real completo se puede rankear sin errores.
"""

from __future__ import annotations

import copy
from pathlib import Path

import pandas as pd
import pytest

from src.lodcore.config.perfiles import (
    PESO_MAX,
    PESO_MIN,
    PreferenciasCiudadano,
    pesos_ciudadano,
)
from src.lodcore.models.m5_recomendador.ranking import (
    TECHO_AFINIDAD_ALERTA,
    analisis_sensibilidad,
    rankear_municipios,
)

ROOT = Path(__file__).resolve().parents[2]
PANEL = ROOT / "data" / "validated" / "municipios_panel_validado.csv"


def _fila(
    nombre: str,
    *,
    precio: float = 1500.0,
    alquiler: float = 8.0,
    tiempo: int = 50,
    sanidad: float = 60.0,
    educacion: float = 60.0,
    conectividad: float = 60.0,
    vivienda: float = 60.0,
    hab_medico: float = 800.0,
    ocupacion: float = 70.0,
    ica: float = 60.0,
    capacidad: float = 500,
    factor: str = "EDUCACION",
) -> dict:
    """Fila minima con las columnas que usa el ranking."""
    return {
        "id_municipio": abs(hash(nombre)) % 10000,
        "codigo_ine": "28000",
        "nombre": nombre,
        "comarca": "Prueba",
        "precio_m2_compra": precio,
        "precio_m2_alquiler": alquiler,
        "tiempo_medio_madrid_minutos": tiempo,
        "score_sanidad": sanidad,
        "score_educacion": educacion,
        "score_conectividad": conectividad,
        "score_vivienda": vivienda,
        "hab_por_medico": hab_medico,
        "ocupacion_escolar_pct": ocupacion,
        "indice_capacidad_global": ica,
        "personas_acogida_efectiva": capacidad,
        "factor_limitante": factor,
        "poblacion_2031": 1000,
        "anio_estimado_saturacion": 2045,
        "alerta_planificacion": "ESTABLE",
    }


def _perfil(**kw) -> PreferenciasCiudadano:
    base = dict(
        presupuesto_max_m2_eur=2000.0,
        ingresos_netos_hogar_eur=2500.0,
        tiempo_max_commute_min=90,
        modo_transporte="publico",
        num_hijos=0,
        edad=35,
        tenencia="compra",
        m2_deseados=90.0,
    )
    base.update(kw)
    return PreferenciasCiudadano(**base)


# ---------------------------------------------------------------------------
# Pesos
# ---------------------------------------------------------------------------

def test_pesos_suman_uno_y_respetan_limites():
    perfiles = [
        _perfil(num_hijos=0, edad=30),
        _perfil(num_hijos=2, edad=40),
        _perfil(num_hijos=6, edad=70, tenencia="alquiler"),
        _perfil(edad=50, modo_transporte="privado"),
    ]
    for p in perfiles:
        w = pesos_ciudadano(p)
        assert abs(sum(w.values()) - 1.0) < 1e-9
        assert all(PESO_MIN - 1e-9 <= v <= PESO_MAX + 1e-9 for v in w.values())


def test_familia_prioriza_educacion_y_senior_sanidad():
    soltero = pesos_ciudadano(_perfil(num_hijos=0, edad=30, modo_transporte="privado"))
    familia = pesos_ciudadano(_perfil(num_hijos=2, edad=40, modo_transporte="publico"))
    senior = pesos_ciudadano(_perfil(num_hijos=0, edad=70, modo_transporte="privado"))

    assert familia["educacion"] > soltero["educacion"]
    assert familia["conectividad"] > soltero["conectividad"]
    assert senior["sanidad"] > soltero["sanidad"]


# ---------------------------------------------------------------------------
# Filtros duros
# ---------------------------------------------------------------------------

def test_filtro_presupuesto_excluye_y_reporta_motivo():
    filas = [
        _fila("Barato", precio=1200),
        _fila("Caro", precio=3000),
    ]
    res = rankear_municipios(filas, _perfil(presupuesto_max_m2_eur=2000))
    nombres = [m["nombre"] for m in res["ranking"]]
    assert nombres == ["Barato"]
    assert res["n_excluidos"] == 1
    assert res["excluidos"][0]["nombre"] == "Caro"
    assert res["excluidos"][0]["motivo"] == "PRECIO"


def test_filtro_tiempo_excluye():
    filas = [
        _fila("Cerca", tiempo=40),
        _fila("Lejos", tiempo=110),
    ]
    res = rankear_municipios(filas, _perfil(tiempo_max_commute_min=60))
    assert [m["nombre"] for m in res["ranking"]] == ["Cerca"]
    assert res["excluidos"][0]["motivo"] == "TIEMPO"


def test_bajar_presupuesto_no_incorpora_municipios_mas_caros():
    filas = [
        _fila("A", precio=1200),
        _fila("B", precio=1700),
        _fila("C", precio=2400),
    ]
    amplio = rankear_municipios(filas, _perfil(presupuesto_max_m2_eur=2500))
    estrecho = rankear_municipios(filas, _perfil(presupuesto_max_m2_eur=1800))
    precios_estrecho = {m["nombre"]: m["precio_m2"] for m in estrecho["ranking"]}
    assert "C" not in precios_estrecho
    assert len(estrecho["ranking"]) < len(amplio["ranking"])


# ---------------------------------------------------------------------------
# Regla no compensatoria
# ---------------------------------------------------------------------------

def test_colapso_se_mantiene_marcado_y_con_techo():
    filas = [
        _fila(
            "Colapsado",
            sanidad=95, educacion=95, conectividad=95, vivienda=95,
            hab_medico=2500,  # supera 1.500 -> colapso sanitario
            ica=95,
        ),
        _fila("Normal", sanidad=50, educacion=50, conectividad=50, vivienda=50, ica=50),
    ]
    res = rankear_municipios(filas, _perfil())
    colapsado = next(m for m in res["ranking"] if m["nombre"] == "Colapsado")

    # No se elimina: se mantiene y se marca
    assert colapsado["alerta_no_compensatoria"] is True
    assert colapsado["motivo_colapso"]
    assert colapsado["semaforo_ica"] == "BAJA"
    # Y su afinidad queda truncada, aunque sus scores sean perfectos
    assert colapsado["afinidad_pct"] <= TECHO_AFINIDAD_ALERTA
    # Aun asi, al haber solo dos municipios, aparece en la lista
    assert len(res["ranking"]) == 2


def test_el_ranking_no_muta_las_filas_de_entrada():
    filas = [_fila("A"), _fila("B", precio=3000)]
    copia = copy.deepcopy(filas)
    rankear_municipios(filas, _perfil())
    assert filas == copia


def test_el_ranking_no_cambia_el_ica_del_panel():
    filas = [_fila("A", ica=73.5)]
    antes = filas[0]["indice_capacidad_global"]
    rankear_municipios(filas, _perfil())
    assert filas[0]["indice_capacidad_global"] == antes


# ---------------------------------------------------------------------------
# Determinismo y forma de la salida
# ---------------------------------------------------------------------------

def test_orden_determinista():
    filas = [_fila(f"M{i}", vivienda=50 + i, educacion=50 + i) for i in range(6)]
    r1 = rankear_municipios(filas, _perfil())
    r2 = rankear_municipios(filas, _perfil())
    assert [m["nombre"] for m in r1["ranking"]] == [m["nombre"] for m in r2["ranking"]]


def test_salida_tiene_los_campos_prometidos():
    res = rankear_municipios([_fila("A")], _perfil())
    m = res["ranking"][0]
    for clave in (
        "nombre", "afinidad_pct", "desglose", "semaforo_ica",
        "alerta_no_compensatoria", "esfuerzo_financiero_pct",
        "etiqueta_esfuerzo", "fortalezas", "carencias",
        "riesgo_futuro", "motivo_recomendacion",
    ):
        assert clave in m
    assert abs(sum(m["desglose"].values()) - sum(
        v for k, v in m["desglose"].items()
    )) < 1e-9


# ---------------------------------------------------------------------------
# Sensibilidad
# ---------------------------------------------------------------------------

def test_sensibilidad_devuelve_valores_validos():
    filas = [_fila(f"M{i}", vivienda=40 + 8 * i, educacion=90 - 8 * i) for i in range(6)]
    res = analisis_sensibilidad(filas, _perfil(num_hijos=2), delta=0.20, top_k=3)
    assert res["n_variantes"] == 8
    assert -1.0 <= res["spearman_min"] <= 1.0
    assert 0.0 <= res["top_k_solape_min"] <= 1.0
    assert len(res["detalle"]) == 8


# ---------------------------------------------------------------------------
# Datos reales
# ---------------------------------------------------------------------------

@pytest.mark.skipif(not PANEL.exists(), reason="panel validado no disponible")
def test_panel_real_se_rankear_sin_errores():
    df = pd.read_csv(PANEL)
    filas = df.to_dict(orient="records")
    perfil = _perfil(
        presupuesto_max_m2_eur=6000,
        tiempo_max_commute_min=120,
        ingresos_netos_hogar_eur=3000,
    )
    res = rankear_municipios(filas, perfil)
    assert res["n_aceptados"] + res["n_excluidos"] == 20
    assert 1 <= len(res["ranking"]) <= 20
    # El ICA del panel no se ha tocado
    assert df["indice_capacidad_global"].round(4).tolist() == pd.read_csv(PANEL)[
        "indice_capacidad_global"
    ].round(4).tolist()
