"""
test_optimizador.py - Pruebas unitarias para la Heurística Voraz de Presupuesto Comarcal (M4-OPT).
Verifica:
- Restricción presupuestaria dura e identidad presupuestaria
- Poda de ineficiencia residencial (no gastar en municipios saturados por vivienda como Navalcarnero)
- Asignación efectiva en comarcas con cuello de botella en servicios
- Contrato JSON unificado para FastAPI y Oracle APEX
"""

import pytest
from src.lodcore.models.m4_capacidad.optimizador_presupuestario import optimizar_presupuesto_comarca

def test_optimizador_respeta_presupuesto_e_identidad():
    presupuesto = 1_500_000.0
    res = optimizar_presupuesto_comarca(comarca="Sierra Oeste", presupuesto_total_eur=presupuesto)

    assert res["presupuesto_total_eur"] == presupuesto
    assert res["presupuesto_utilizado_eur"] <= presupuesto
    assert res["remanente_eur"] >= 0.0
    assert res["presupuesto_utilizado_eur"] + res["remanente_eur"] == pytest.approx(presupuesto, abs=1e-2)
    assert res["metodologia"].startswith("Heurística voraz")
    assert res["origen"] == "SIMULADO"

    # Verificar contrato de asignaciones
    for asig in res["asignaciones"]:
        assert "codigo_ine" in asig
        assert "municipio" in asig
        assert "coste_eur" in asig
        assert "ganancia_personas" in asig
        assert "nuevo_ica" in asig
        assert "semaforo" in asig
        assert asig["coste_eur"] > 0
        assert asig["ganancia_personas"] > 0

def test_optimizador_poda_ineficiencia_vivienda_navalcarnero():
    """Comprueba que en Comarca Sur (Navalcarnero saturado por vivienda) no se malgasta presupuesto."""
    presupuesto = 2_000_000.0
    res = optimizar_presupuesto_comarca(comarca="Comarca Sur", presupuesto_total_eur=presupuesto)

    assert res["presupuesto_utilizado_eur"] == 0.0
    assert res["remanente_eur"] == presupuesto
    assert res["incremento_acogida_comarcal"] == 0
    assert len(res["asignaciones"]) == 0

def test_optimizador_comarca_invalida_lanza_error():
    with pytest.raises(ValueError, match="Comarca 'Inexistente' no encontrada"):
        optimizar_presupuesto_comarca(comarca="Inexistente", presupuesto_total_eur=1_000_000.0)
