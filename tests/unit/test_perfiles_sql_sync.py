"""
test_perfiles_sql_sync.py - Vigila que Oracle y Python usen los MISMOS numeros.

No necesita conexion a Oracle: lee el fichero SQL y compara sus valores con las
constantes de Python. Si alguien cambia un ajuste en un sitio y no en el otro,
el test falla antes de que el jurado lo descubra.

Fuente de verdad: src/lodcore/config/perfiles.py y src/lodcore/config/thresholds.py.
Copia:            oracle/ddl/04-perfiles_y_ranking.sql
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest

from src.lodcore.config.perfiles import (
    DIMENSIONES,
    MAX_TRANSFERENCIA_TOTAL,
    PESO_MAX,
    PESO_MIN,
    PESOS_BASE_IGUALES,
    SUPUESTOS_AJUSTES,
)
from src.lodcore.config.thresholds import (
    MAX_HABITANTES_POR_MEDICO_AP,
    MAX_OCUPACION_ESCOLAR_PCT,
    UMBRAL_ICA_BAJA,
    UMBRAL_ICA_MEDIA,
)

ROOT = Path(__file__).resolve().parents[2]
SQL_FILE = ROOT / "oracle" / "ddl" / "04-perfiles_y_ranking.sql"

pytestmark = pytest.mark.skipif(
    not SQL_FILE.exists(), reason="04-perfiles_y_ranking.sql no disponible"
)


def _sql() -> str:
    return SQL_FILE.read_text(encoding="utf-8")


def _parametros() -> dict:
    """Extrae PERFILES_PARAMETROS: nombre -> valor."""
    patron = re.compile(
        r"VALUES\s*\(\s*'([^']+)'\s*,\s*(-?[\d.]+)\s*,", re.IGNORECASE
    )
    # Solo dentro de los INSERT de PERFILES_PARAMETROS
    bloque = _sql().split("INSERT INTO PERFILES_PARAMETROS", 1)[1].split("--", 1)[0]
    return {m.group(1): float(m.group(2)) for m in patron.finditer(bloque)}


def _base() -> dict:
    """Extrae PERFILES_BASE: dimension -> peso (perfil ciudadano)."""
    patron = re.compile(
        r"VALUES\s*\(\s*'ciudadano'\s*,\s*'([^']+)'\s*,\s*(-?[\d.]+)\s*\)", re.IGNORECASE
    )
    bloque = _sql().split("INSERT INTO PERFILES_BASE", 1)[1].split("--", 1)[0]
    return {m.group(1): float(m.group(2)) for m in patron.finditer(bloque)}


def _ajustes() -> dict:
    """Extrae PERFILES_AJUSTES: regla -> {dimension, delta, tope, rango}."""
    patron = re.compile(
        r"VALUES\s*\(\s*'([^']+)'\s*,\s*'([^']+)'\s*,\s*(-?[\d.]+)\s*,\s*(NULL|-?[\d.]+)\s*,\s*(-?[\d.]+)\s*,",
        re.IGNORECASE,
    )
    bloque = _sql().split("INSERT INTO PERFILES_AJUSTES", 1)[1].split("--", 1)[0]
    salida = {}
    for m in patron.finditer(bloque):
        tope = None if m.group(4).upper() == "NULL" else float(m.group(4))
        salida[m.group(1)] = {
            "dimension": m.group(2),
            "delta": float(m.group(3)),
            "tope": tope,
            "rango": float(m.group(5)),
        }
    return salida


# ---------------------------------------------------------------------------
# Parametros
# ---------------------------------------------------------------------------

def test_parametros_sql_coinciden_con_python():
    p = _parametros()
    assert p["max_transferencia_total"] == pytest.approx(MAX_TRANSFERENCIA_TOTAL)
    assert p["peso_min"] == pytest.approx(PESO_MIN)
    assert p["peso_max"] == pytest.approx(PESO_MAX)


def test_umbrales_de_la_regla_dura_coinciden_con_thresholds():
    p = _parametros()
    assert p["max_hab_por_medico"] == pytest.approx(MAX_HABITANTES_POR_MEDICO_AP)
    assert p["max_ocupacion_escolar_pct"] == pytest.approx(MAX_OCUPACION_ESCOLAR_PCT)
    assert p["umbral_ica_baja"] == pytest.approx(UMBRAL_ICA_BAJA)
    assert p["umbral_ica_media"] == pytest.approx(UMBRAL_ICA_MEDIA)
    # El techo debe ser coherente con la regla no compensatoria
    assert p["techo_afinidad_alerta"] == pytest.approx(UMBRAL_ICA_BAJA - 1)


# ---------------------------------------------------------------------------
# Pesos base
# ---------------------------------------------------------------------------

def test_pesos_base_sql_coinciden_con_python():
    base = _base()
    assert set(base) == set(DIMENSIONES)
    for d in DIMENSIONES:
        assert base[d] == pytest.approx(PESOS_BASE_IGUALES[d])
    assert sum(base.values()) == pytest.approx(1.0)


# ---------------------------------------------------------------------------
# Reglas de ajuste
# ---------------------------------------------------------------------------

def test_numero_de_reglas_coincide():
    assert len(_ajustes()) == len(SUPUESTOS_AJUSTES)


def test_cada_regla_coincide_en_delta_y_rango():
    ajustes = _ajustes()
    for regla, supuesto in SUPUESTOS_AJUSTES.items():
        assert regla in ajustes, f"La regla '{regla}' falta en el SQL"
        assert ajustes[regla]["delta"] == pytest.approx(float(supuesto["delta"])), (
            f"Delta distinto en la regla '{regla}'"
        )
        assert ajustes[regla]["rango"] == pytest.approx(
            float(supuesto["rango_sensibilidad"])
        ), f"Rango de sensibilidad distinto en la regla '{regla}'"


def test_topes_coinciden():
    ajustes = _ajustes()
    assert ajustes["hijo"]["tope"] == pytest.approx(float(SUPUESTOS_AJUSTES["hijo"]["tope"]))
    for regla in SUPUESTOS_AJUSTES:
        if regla == "hijo":
            continue
        assert ajustes[regla]["tope"] is None, f"La regla '{regla}' no debe tener tope propio"


def test_dimensiones_de_las_reglas_son_validas():
    for regla, datos in _ajustes().items():
        assert datos["dimension"] in DIMENSIONES, f"Dimension invalida en '{regla}'"


# ---------------------------------------------------------------------------
# Contrato de las funciones
# ---------------------------------------------------------------------------

def test_el_sql_declara_las_dos_funciones():
    sql = _sql()
    assert "FUNCTION f_pesos_ciudadano" in sql
    assert "FUNCTION f_ranking_ciudadano" in sql


def test_el_sql_declara_el_techo_no_compensatorio():
    sql = _sql().upper()
    assert "LEAST(AFINIDAD" in sql, "El ranking SQL no aplica el techo a la afinidad"
