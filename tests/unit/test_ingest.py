"""
test_ingest.py - Pruebas unitarias para los conectores de fuentes oficiales y trazabilidad (Fase F1).
Verifica:
- Ingesta de Padrón INE con identificación de 5 dígitos
- Ingesta de CKAN Madrid (Sanidad y Educación)
- Persistencia de snapshots inmutables con fecha
- Correspondencia estricta 20/20 por código INE
"""

import json
from pathlib import Path
import pandas as pd
import pytest

from src.lodcore.ingest.ine_padron import IngestorINEPadron
from src.lodcore.ingest.ckan_madrid import IngestorCKANMadrid
from src.lodcore.data.quality_gates import ejecutar_quality_gates

def test_ine_padron_snapshot_y_cruce_5_digitos():
    ingestor = IngestorINEPadron()
    snap_path, payload = ingestor.descargar_y_guardar_snapshot()
    assert snap_path.exists(), "El snapshot del INE debe existir en disco"
    assert "20261023" in snap_path.name or "snapshot" in snap_path.name

    datos_madrid = ingestor.procesar_poblacion_madrid(payload)
    assert len(datos_madrid) >= 170, "Deben procesarse los municipios oficiales de Madrid"

    # Verificar que las claves son códigos INE de 5 dígitos de Madrid (28xxx)
    for cod_ine, meta in list(datos_madrid.items())[:10]:
        assert len(cod_ine) == 5 and cod_ine.startswith("28"), f"Código INE inválido: {cod_ine}"
        assert meta["poblacion_oficial"] > 0
        assert meta["origen"] == "OBSERVADO"
        assert meta["metodo"] == "INE_TABLA_2881_API"

def test_ckan_madrid_sanidad_y_educacion_cruzan_20_municipios():
    panel_path = Path("data/validated/municipios_panel_validado.csv")
    df = pd.read_csv(panel_path)
    codigos_20 = set(df["codigo_ine"].astype(str).str.zfill(5))
    assert len(codigos_20) == 20, "El piloto debe tener exactamente 20 municipios"

    ckan = IngestorCKANMadrid()
    snap_san, payload_san = ckan.descargar_y_guardar_snapshot_sanidad()
    assert snap_san.exists()
    san_data = ckan.procesar_sanidad(payload_san)
    for cod in codigos_20:
        assert cod in san_data, f"Municipio {cod} no encontrado en datos sanitarios de CKAN"

    snap_edu, payload_edu = ckan.descargar_y_guardar_snapshot_educacion()
    assert snap_edu.exists()
    edu_data = ckan.procesar_educacion(payload_edu)
    for cod in codigos_20:
        assert cod in edu_data, f"Municipio {cod} no encontrado en datos educativos de CKAN"

def test_calidad_trazabilidad_panel_actualizado():
    panel_path = Path("data/validated/municipios_panel_validado.csv")
    df = pd.read_csv(panel_path)
    qg = ejecutar_quality_gates(df)
    assert qg["status"] == "PASSED"
    assert qg["filas_validadas"] == 20

    # Comprobar trazabilidad en todas las filas
    for col in ["origen", "metodo", "dataset_version", "fuente_datos"]:
        assert col in df.columns, f"Falta columna de metadatos {col}"
        assert not df[col].isna().any(), f"Existen valores nulos en columna {col}"
