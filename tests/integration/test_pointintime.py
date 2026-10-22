"""
test_pointintime.py - Prueba de integración para el control de punto-en-tiempo (`fecha_disponible`).
"""

import pandas as pd
import pytest
from src.lodcore.data.pointintime import filtrar_point_in_time, verificar_no_leakage_temporal

def test_filtrar_point_in_time_bloquea_futuro():
    df = pd.DataFrame({
        "id_municipio": [1, 2, 3],
        "fecha_disponible": ["2025-01-01", "2026-10-14", "2027-05-01"],
        "valor": [10, 20, 30]
    })
    filtrado = filtrar_point_in_time(df, fecha_decision="2026-10-22")
    assert len(filtrado) == 2
    assert 3 not in filtrado["id_municipio"].values

def test_verificar_no_leakage_temporal_detecta_fuga():
    df_train = pd.DataFrame({"fecha_disponible": ["2026-01-01", "2026-11-01"]})
    df_test = pd.DataFrame({"fecha_disponible": ["2026-10-15"]})
    with pytest.raises(AssertionError):
        verificar_no_leakage_temporal(df_train, df_test)
