"""
optimizador_presupuestario.py - Asignación Presupuestaria Óptima por Comarca (Fase F1 / M4).
Resuelve el problema de asignación de capital público entre municipios de una comarca
para maximizar la capacidad neta de acogida efectiva sin generar colapsos de dotación.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Any, Dict, List, Optional
import pandas as pd

from src.lodcore.config.thresholds import (
    COSTE_AMPLIACION_CONSULTA_MEDICA_EUR,
    COSTE_UNITARIO_PLAZA_ESCOLAR_EUR,
    MAX_HABITANTES_POR_MEDICO_AP,
    MAX_OCUPACION_ESCOLAR_PCT
)
from src.lodcore.data.provenance import TipoOrigen
from src.lodcore.models.m4_capacidad.reglas_no_compensatorias import aplicar_salvaguarda_no_compensatoria

@dataclass
class AsignacionMunicipio:
    id_municipio: int
    codigo_ine: str
    nombre: str
    comarca: str
    medicos_asignados: int
    plazas_escolares_asignadas: int
    coste_total_eur: float
    ganancia_acogida_personas: int
    ica_previo: float
    ica_nuevo: float
    semaforo_previo: str
    semaforo_nuevo: str
    alerta_colapso_resuelta: bool
    factor_limitante: str

def optimizar_presupuesto_comarca(
    comarca: str,
    presupuesto_total_eur: float,
    data_path: str = "data/validated/municipios_panel_validado.csv"
) -> Dict[str, Any]:
    """
    Asigna un presupuesto cerrado entre los municipios de una comarca determinada
    utilizando una estrategia de optimización determinista (Greedy / Knapsack acotado)
    priorizando la resolución de cuellos de botella no compensatorios y la maximización
    de la capacidad de acogida efectiva.

    Parámetros:
      - comarca: Nombre de la comarca (ej. 'Sierra Oeste', 'Sierra Norte', 'Las Vegas')
      - presupuesto_total_eur: Partida presupuestaria en euros
      - data_path: Ruta al CSV del panel validado

    Retorna un diccionario estructurado apto para consumo por APEX y FastAPI.
    """
    df = pd.read_csv(data_path)
    df["codigo_ine"] = df["codigo_ine"].astype(str).str.zfill(5)

    if comarca.lower() != "todas":
        muni_comarca = df[df["comarca"].str.lower() == comarca.lower()].copy()
    else:
        muni_comarca = df.copy()

    if muni_comarca.empty:
        comarcas_validas = sorted(df["comarca"].unique().tolist())
        raise ValueError(f"Comarca '{comarca}' no encontrada. Opciones: {comarcas_validas}")

    presupuesto_restante = float(presupuesto_total_eur)
    asignaciones: List[AsignacionMunicipio] = []
    incremento_total_personas = 0

    # 1. Identificar necesidades prioritarias para desbloquear colapsos no compensatorios
    candidatos = []
    for _, row in muni_comarca.iterrows():
        pob = float(row["poblacion_actual"])
        medicos = float(row["num_medicos_ap"])
        plazas = float(row["num_plazas_escolares"])
        alumnos = float(row["num_alumnos_matriculados"])
        factor_lim = str(row.get("factor_limitante", "VIVIENDA"))
        ica_base = float(row.get("indice_capacidad_global", 50.0))

        # Déficit médico para no superar 1500 hab/médico
        medicos_necesarios = max(0, math.ceil(pob / MAX_HABITANTES_POR_MEDICO_AP) - int(medicos))
        # Déficit escolar para no superar el 95% de ocupación
        plazas_necesarias = max(0, math.ceil(alumnos / (MAX_OCUPACION_ESCOLAR_PCT / 100.0)) - int(plazas))

        coste_desbloqueo = (
            medicos_necesarios * COSTE_AMPLIACION_CONSULTA_MEDICA_EUR +
            plazas_necesarias * COSTE_UNITARIO_PLAZA_ESCOLAR_EUR
        )

        candidatos.append({
            "row": row,
            "medicos_necesarios": medicos_necesarios,
            "plazas_necesarias": plazas_necesarias,
            "coste_desbloqueo": coste_desbloqueo,
            "factor_limitante": factor_lim,
            "ica_base": ica_base
        })

    # Ordenar candidatos priorizando municipios en colapso crítico y con mayor ratio personas/euro
    candidatos.sort(
        key=lambda c: (
            1 if c["coste_desbloqueo"] > 0 else 0,
            float(c["row"].get("personas_absorb_vivienda", 0)) / max(1.0, c["coste_desbloqueo"])
        ),
        reverse=True
    )

    for item in candidatos:
        row = item["row"]
        m_asignados = 0
        p_asignadas = 0
        coste_muni = 0.0

        # Paso A: Asignar para desbloquear cuello de botella si el presupuesto lo permite
        if item["medicos_necesarios"] > 0:
            coste_m = item["medicos_necesarios"] * COSTE_AMPLIACION_CONSULTA_MEDICA_EUR
            if presupuesto_restante >= coste_m:
                m_asignados += item["medicos_necesarios"]
                coste_muni += coste_m
                presupuesto_restante -= coste_m

        if item["plazas_necesarias"] > 0:
            coste_p = item["plazas_necesarias"] * COSTE_UNITARIO_PLAZA_ESCOLAR_EUR
            if presupuesto_restante >= coste_p:
                p_asignadas += item["plazas_necesarias"]
                coste_muni += coste_p
                presupuesto_restante -= coste_p

        # Paso B: Si aún queda presupuesto y el factor limitante es servicios, dotar capacidad incremental
        if presupuesto_restante >= COSTE_AMPLIACION_CONSULTA_MEDICA_EUR and item["factor_limitante"] == "SANIDAD":
            medicos_extra = int(presupuesto_restante // COSTE_AMPLIACION_CONSULTA_MEDICA_EUR)
            # Acotar a un máximo prudente por municipio (+2 médicos en MVP)
            medicos_extra = min(2, medicos_extra)
            coste_extra = medicos_extra * COSTE_AMPLIACION_CONSULTA_MEDICA_EUR
            m_asignados += medicos_extra
            coste_muni += coste_extra
            presupuesto_restante -= coste_extra

        # Calcular nuevo estado del municipio
        pob_actual = float(row["poblacion_actual"])
        medicos_totales = float(row["num_medicos_ap"]) + m_asignados
        plazas_totales = float(row["num_plazas_escolares"]) + p_asignadas
        alumnos_act = float(row["num_alumnos_matriculados"])

        hab_med_nuevo = pob_actual / medicos_totales
        ocup_esc_nueva = (alumnos_act / plazas_totales) * 100.0

        # Capacidad de absorción resultante
        abs_sanidad = max(0, int(medicos_totales * MAX_HABITANTES_POR_MEDICO_AP - pob_actual))
        abs_educacion = max(0, int((plazas_totales * 0.95 - alumnos_act) / 0.17))
        abs_vivienda = int(row.get("personas_absorb_vivienda", 500))
        acogida_efectiva_nueva = min(abs_sanidad, abs_educacion, abs_vivienda)
        acogida_efectiva_base = int(row.get("personas_acogida_efectiva", 0))

        ganancia_muni = max(0, acogida_efectiva_nueva - acogida_efectiva_base)
        incremento_total_personas += ganancia_muni

        # Calcular nuevo score ICA y aplicar salvaguarda
        delta_ica_sanidad = min(20.0, m_asignados * 6.5)
        delta_ica_educacion = min(15.0, (p_asignadas / 50.0) * 3.0)
        ica_nuevo_raw = min(100.0, float(row["indice_capacidad_global"]) + delta_ica_sanidad + delta_ica_educacion)

        dict_eval = {
            "hab_por_medico": hab_med_nuevo,
            "ocupacion_escolar_pct": ocup_esc_nueva,
            "indice_capacidad_global": ica_nuevo_raw
        }
        salvaguarda = aplicar_salvaguarda_no_compensatoria(dict_eval)

        alerta_previa = (
            float(row["hab_por_medico"]) > MAX_HABITANTES_POR_MEDICO_AP or
            float(row["ocupacion_escolar_pct"]) > MAX_OCUPACION_ESCOLAR_PCT
        )
        alerta_resuelta = alerta_previa and not salvaguarda["alerta_no_compensatoria"]

        asignaciones.append(AsignacionMunicipio(
            id_municipio=int(row["id_municipio"]),
            codigo_ine=str(row["codigo_ine"]),
            nombre=str(row["nombre"]),
            comarca=str(row["comarca"]),
            medicos_asignados=m_asignados,
            plazas_escolares_asignadas=p_asignadas,
            coste_total_eur=round(coste_muni, 2),
            ganancia_acogida_personas=ganancia_muni,
            ica_previo=round(float(row["indice_capacidad_global"]), 2),
            ica_nuevo=salvaguarda["indice_capacidad_ajustado"],
            semaforo_previo=str(row.get("nivel_idoneidad", "MEDIA")),
            semaforo_nuevo=salvaguarda["semaforo_ica"],
            alerta_colapso_resuelta=alerta_resuelta,
            factor_limitante=item["factor_limitante"]
        ))

    presupuesto_utilizado = float(presupuesto_total_eur) - presupuesto_restante

    return {
        "comarca": comarca,
        "presupuesto_total_eur": float(presupuesto_total_eur),
        "presupuesto_utilizado_eur": round(presupuesto_utilizado, 2),
        "presupuesto_remanente_eur": round(presupuesto_restante, 2),
        "incremento_acogida_comarcal_personas": int(incremento_total_personas),
        "municipios_evaluados": len(asignaciones),
        "asignaciones": [
            {
                "id_municipio": a.id_municipio,
                "codigo_ine": a.codigo_ine,
                "nombre": a.nombre,
                "comarca": a.comarca,
                "medicos_asignados": a.medicos_asignados,
                "plazas_escolares_asignadas": a.plazas_escolares_asignadas,
                "coste_total_eur": a.coste_total_eur,
                "ganancia_acogida_personas": a.ganancia_acogida_personas,
                "ica_previo": a.ica_previo,
                "ica_nuevo": a.ica_nuevo,
                "delta_ica": round(a.ica_nuevo - a.ica_previo, 2),
                "semaforo_previo": a.semaforo_previo,
                "semaforo_nuevo": a.semaforo_nuevo,
                "alerta_colapso_resuelta": a.alerta_colapso_resuelta,
                "factor_limitante": a.factor_limitante
            }
            for a in asignaciones
        ],
        "origen": TipoOrigen.SIMULADO.value,
        "metodo": "OPTIMIZADOR_PRESUPUESTARIO_DETERMINISTA_COMARCAL",
        "dataset_version": "v1.0.0-F2",
        "declaracion_metodologica": (
            "Asignación presupuestaria determinista comarcal implementada. "
            "El modelado de difusión continua por gravedad y matriz de movilidad (spillover) "
            "se define como roadmap para la Fase 2."
        )
    }
