"""
recomendar.py - Endpoint lógico N3 para el perfil Ciudadano: Recomendación personalizada MCDM.
"""

from typing import List, Dict, Any
import pandas as pd
from pydantic import BaseModel, Field
from src.lodcore.models.m5_recomendador.recommend import recomendar_municipios_mcdm

class PreferenciasCiudadanoRequest(BaseModel):
    peso_sanidad: float = Field(default=0.30, ge=0.0, le=1.0, description="Importancia relativa de la cobertura sanitaria AP")
    peso_educacion: float = Field(default=0.30, ge=0.0, le=1.0, description="Importancia relativa de las plazas escolares")
    peso_conectividad: float = Field(default=0.20, ge=0.0, le=1.0, description="Importancia de fibra y transporte público CRTM")
    peso_vivienda: float = Field(default=0.20, ge=0.0, le=1.0, description="Importancia de vivienda disponible y asequibilidad")
    presupuesto_max_m2: float = Field(default=2000.0, gt=500.0, le=6000.0, description="Precio máximo de compra admisible (€/m²)")
    tiempo_max_madrid_min: int = Field(default=60, ge=15, le=120, description="Tiempo máximo de desplazamiento a Madrid capital (min)")
    top_k: int = Field(default=3, ge=1, le=20, description="Número de municipios a retornar en el ranking")

def ejecutar_recomendacion_ciudadana(
    req: PreferenciasCiudadanoRequest,
    data_path: str = "data/validated/municipios_panel_validado.csv"
) -> Dict[str, Any]:
    df = pd.read_csv(data_path)
    ranking = recomendar_municipios_mcdm(
        df=df,
        peso_sanidad=req.peso_sanidad,
        peso_educacion=req.peso_educacion,
        peso_conectividad=req.peso_conectividad,
        peso_vivienda=req.peso_vivienda,
        presupuesto_max_m2=req.presupuesto_max_m2,
        tiempo_max_madrid_min=req.tiempo_max_madrid_min,
        top_k=req.top_k
    )
    return {
        "total_evaluados": int(len(df)),
        "top_k": req.top_k,
        "preferencias_aplicadas": req.model_dump(),
        "ranking": ranking,
        "origen": "ESTIMADO",
        "metodo": "M5_MCDM_WEIGHTED_COSINE_NON_COMPENSATORY",
        "dataset_version": "v1.0.0-F2"
    }
