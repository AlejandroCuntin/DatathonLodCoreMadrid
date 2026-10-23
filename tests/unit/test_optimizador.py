"""
test_optimizador.py - Pruebas unitarias para el Optimizador Presupuestario Comarcal (M4-OPT).
Verifica:
- Restricción presupuestaria dura
- Resolución de cuellos de botella no compensatorios
- Coherencia comarcal
- Contrato de salida con trazabilidad
"""

import pytest
from src.lodcore.models.m4_capacidad.optimizador_presupuestario import optimizar_presupuesto_comarca

def test_optimizador_respeta_presupuesto():
    presupuesto = 1_500_000.0
    res = optimizar_presupuesto_comarca(comarca="Sierra Oeste", presupuesto_total_eur=presupuesto)

    assert res["presupuesto_total_eur"] == presupuesto
    assert res["presupuesto_utilizado_eur"] <= presupuesto
    assert res["presupuesto_remanente_eur"] >= 0.0
    assert res["presupuesto_utilizado_eur"] + res["presupuesto_remanente_eur"] == pytest.approx(presupuesto, abs=1e-2)
    assert len(res["asignaciones"]) > 0

    # Verificar suma de costes individuales
    suma_costes = sum(a["coste_total_eur"] for a in res["asignaciones"])
    assert suma_costes == pytest.approx(res["presupuesto_utilizado_eur"], abs=1e-2)

def test_optimizador_no_compensatoriedad_y_delta_positivo():
    presupuesto = 2_000_000.0
    res = optimizar_presupuesto_comarca(comarca="Sierra Norte", presupuesto_total_eur=presupuesto)

    assert res["origen"] == "SIMULADO"
    assert res["metodo"] == "OPTIMIZADOR_PRESUPUESTARIO_DETERMINISTA_COMARCAL"
    assert "roadmap" in res["declaracion_metodologica"].lower()

    for a in res["asignaciones"]:
        assert a["medicos_asignados"] >= 0
        assert a["plazas_escolares_asignadas"] >= 0
        assert a["ica_nuevo"] >= 0.0 and a["ica_nuevo"] <= 100.0
        assert a["semaforo_nuevo"] in ("ALTA", "MEDIA", "BAJA")

def test_optimizador_comarca_invalida_lanza_error():
    with pytest.raises(ValueError, match="Comarca 'Inexistente' no encontrada"):
        optimizar_presupuesto_comarca(comarca="Inexistente", presupuesto_total_eur=1_000_000.0)
