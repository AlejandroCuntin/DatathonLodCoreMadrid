"""
app.py - Servidor mínimo FastAPI Nivel N3 para LoDCORE Madrid.
Siguiendo el diseño de arquitectura:
  - Nivel N1: Entrenamiento y exportación ONNX (Python/CI)
  - Nivel N2: Scoring masivo en Oracle Database (DBMS_VECTOR.LOAD_ONNX_MODEL + PREDICTION())
  - Nivel N3: Runtime dinámico mínimo en FastAPI exclusivamente para `/recomendar` y `/whatif`
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from src.lodcore import __version__, DATASET_VERSION
from src.lodcore.serving.fastapi.recomendar import (
    PreferenciasCiudadanoRequest,
    ejecutar_recomendacion_ciudadana
)
from src.lodcore.serving.fastapi.whatif import (
    SimuladorWhatIfRequest,
    MunicipioNoEncontrado,
    ejecutar_simulacion_whatif
)

app = FastAPI(
    title="LoDCORE Madrid • API Nivel N3 (Ciudadano & Institución)",
    description=(
        "Servicio de inferencia interactiva para el II Datathon LoDCOREMadrid 2026. "
        "Expone únicamente `/recomendar` (M5 MCDM coseno ponderado) y `/whatif` "
        "(M4 contrafactual con atribuciones aditivas y reglas duras no compensatorias)."
    ),
    version=__version__
)

app.add_middleware(
    CORSMiddleware,
    # CORS prohíbe combinar origen comodín con credenciales: al no usar cookies,
    # se desactivan las credenciales para que el navegador acepte el comodín.
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health", tags=["Diagnóstico"])
def health_check():
    return {
        "status": "ok",
        "service": "lodcore-madrid-n3-fastapi",
        "version": __version__,
        "dataset_version": DATASET_VERSION,
        "endpoints_activos": ["/recomendar", "/whatif"]
    }

@app.post("/recomendar", tags=["Portal Ciudadano (M5)"])
def post_recomendar(req: PreferenciasCiudadanoRequest):
    """
    Calcula el ranking personalizado de municipios según las preferencias del ciudadano
    utilizando similitud del coseno ponderada (MCDM) y aplicando la salvaguarda no compensatoria.
    """
    try:
        return ejecutar_recomendacion_ciudadana(req)
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

@app.post("/whatif", tags=["Panel Institucional (M4)"])
def post_whatif(req: SimuladorWhatIfRequest):
    """
    Ejecuta una simulación contrafactual sobre un municipio ante cambios demográficos o
    inversiones dotacionales, recalculando atribuciones, bandas al 95 % y el semáforo no compensatorio.
    """
    try:
        return ejecutar_simulacion_whatif(req)
    except MunicipioNoEncontrado as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
