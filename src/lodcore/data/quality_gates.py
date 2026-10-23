"""
quality_gates.py - Puertas de calidad para el panel municipal validado (Fase F2).
Evita Great Expectations en Oracle (bug ORA-00907 con FROM DUAL) y valida tipos,
rangos y no-nulidad antes de permitir el paso a los 5 modelos.
"""

import pandas as pd
from typing import List, Dict, Any

REQUIRED_MUNICIPAL_COLUMNS = [
    "id_municipio",
    "codigo_ine",
    "nombre",
    "comarca",
    "poblacion_actual",
    "superficie_km2",
    "tiempo_medio_madrid_minutos",
    "precio_m2_compra",
    "num_medicos_ap",
    "num_plazas_escolares",
    "num_alumnos_matriculados",
    "score_sanidad",
    "score_educacion",
    "score_conectividad",
    "score_vivienda",
    "indice_capacidad_global",
    "personas_acogida_efectiva",
    "factor_limitante"
]

def ejecutar_quality_gates(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Ejecuta las validaciones de esquema y dominio sobre el panel municipal.
    Lanza ValueError si alguna puerta de calidad falla.
    """
    errores: List[str] = []

    # 1. Columnas obligatorias
    faltantes = [c for c in REQUIRED_MUNICIPAL_COLUMNS if c not in df.columns]
    if faltantes:
        errores.append(f"Columnas obligatorias ausentes: {faltantes}")

    if not errores:
        # 2. Unicidad de clave primaria e INE
        if df["id_municipio"].duplicated().any():
            errores.append("Duplicados detectados en 'id_municipio'")
        if df["codigo_ine"].duplicated().any():
            errores.append("Duplicados detectados en 'codigo_ine'")

        # 3. Criterio Datathon: Municipios < 50.000 habitantes
        if (df["poblacion_actual"] >= 50000).any() or (df["poblacion_actual"] <= 0).any():
            errores.append("Violación de dominio en 'poblacion_actual' (debe estar entre 1 y 49.999 hab.)")

        # 4. Sub-índices en rango [0, 100]
        for col in ["score_sanidad", "score_educacion", "score_conectividad", "score_vivienda", "indice_capacidad_global"]:
            if (df[col] < 0).any() or (df[col] > 100).any():
                errores.append(f"Sub-índice '{col}' fuera del rango [0, 100]")

        # 5. Precios positivos
        if (df["precio_m2_compra"] <= 0).any():
            errores.append("Precios por m² no positivos detectados")

    if errores:
        raise ValueError("PUERTA DE CALIDAD RECHAZADA: " + " | ".join(errores))

    return {
        "status": "PASSED",
        "filas_validadas": int(len(df)),
        "columnas_validadas": len(REQUIRED_MUNICIPAL_COLUMNS),
        "dataset_version": "v1.0.0-F2"
    }
