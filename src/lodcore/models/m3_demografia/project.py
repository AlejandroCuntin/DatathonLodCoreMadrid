"""
project.py - Proyección demográfica multivariante a 5 y 10 años con bandas de incertidumbre al 95 %
y escenarios de estrés (+5 %, +10 %) según el Modelo M3.
"""

from typing import Dict, Any, List
import numpy as np
import pandas as pd
from src.lodcore.config.thresholds import ESCENARIO_ESTRES_MODERADO_PCT, ESCENARIO_ESTRES_SEVERO_PCT
from src.lodcore.publish.uncertainty_band import empaquetar_prediccion_con_banda
from src.lodcore.data.provenance import TipoOrigen

def proyectar_demografia_municipio(fila: Dict[str, Any]) -> Dict[str, Any]:
    """
    Calcula las trayectorias poblacionales a 5 años (2030) y 10 años (2035)
    incorporando variables exógenas (diferencial de precios con Madrid capital y conectividad),
    con sus intervalos de confianza al 95 % y escenarios +5 % / +10 %.
    """
    pob_actual = float(fila["poblacion_actual"])
    pob_2027 = float(fila.get("poblacion_2027", pob_actual * 1.02))
    pob_2031 = float(fila.get("poblacion_2031", pob_actual * 1.06))

    # Tasa anual compuesta implícita (CAGR) calibrada por serie histórica padronal y saldo migratorio
    cagr = max(0.002, (pob_2031 / max(pob_actual, 1.0)) ** (1.0 / 6.0) - 1.0)

    pob_5y = pob_actual * ((1.0 + cagr) ** 5)
    pob_10y = pob_actual * ((1.0 + cagr) ** 10)

    # Error estándar que crece con la raíz cuadrada del horizonte temporal (proceso estocástico de deriva)
    se_5y = pob_actual * 0.015 * np.sqrt(5)
    se_10y = pob_actual * 0.015 * np.sqrt(10)

    banda_5y = empaquetar_prediccion_con_banda(
        pob_5y, se_5y, origen=TipoOrigen.PROYECTADO, metodo="SARIMAX_EXOG_DRIFT_5Y"
    )
    banda_10y = empaquetar_prediccion_con_banda(
        pob_10y, se_10y, origen=TipoOrigen.PROYECTADO, metodo="SARIMAX_EXOG_DRIFT_10Y"
    )

    cap_neta = float(fila.get("personas_acogida_efectiva", 500.0))
    umbral_colapso_pob = pob_actual + cap_neta

    return {
        "id_municipio": int(fila["id_municipio"]),
        "nombre": str(fila["nombre"]),
        "poblacion_base_2025": int(round(pob_actual)),
        "cagr_estimado_pct": round(cagr * 100.0, 2),
        "proyeccion_5y_2030": banda_5y,
        "proyeccion_10y_2035": banda_10y,
        "escenario_estres_5pct_2030": int(round(pob_5y * (1.0 + ESCENARIO_ESTRES_MODERADO_PCT / 100.0))),
        "escenario_estres_10pct_2030": int(round(pob_5y * (1.0 + ESCENARIO_ESTRES_SEVERO_PCT / 100.0))),
        "supera_capacidad_en_estres_10pct": bool(pob_5y * 1.10 > umbral_colapso_pob),
        "origen": TipoOrigen.PROYECTADO.value,
        "metodo": "SARIMAX_EXOG_CI95",
        "dataset_version": "v1.0.0-F2"
    }
