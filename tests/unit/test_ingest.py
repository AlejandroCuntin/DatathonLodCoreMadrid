"""
test_ingest.py - Pruebas unitarias para los conectores de fuentes oficiales y trazabilidad (Fase F1).
Garantías:
- Inmutabilidad de snapshots (los tests no mutan datos versionados en disco ni llaman a red)
- Filtrado semántico estricto de centros educativos en ALTA
- Mapeo unívoco 20/20 por código INE de 5 dígitos
- Verificación de procedencia honesta OBSERVADO+SIMULADO en el panel
"""

import json
from datetime import date
from pathlib import Path
import pandas as pd
import pytest

from src.lodcore.ingest.ine_padron import IngestorINEPadron
from src.lodcore.ingest.ckan_madrid import IngestorCKANMadrid
from src.lodcore.data.quality_gates import ejecutar_quality_gates

def test_ine_padron_snapshot_existente_es_inmutable_y_no_se_sobrescribe(tmp_path):
    """Verifica que si existe un snapshot previo, el conector no lo muta ni llama a red."""
    fake_raw = tmp_path / "fake_ine"
    fake_raw.mkdir()
    fake_payload = [
        {
            "MetaData": [
                {"T3_Variable": "Municipios", "Codigo": "28125", "Nombre": "Robledo de Chavela"},
                {"T3_Variable": "Sexo", "Codigo": "0"}
            ],
            "Data": [{"Anyo": 2025, "Valor": 4818}]
        }
    ]
    hoy_str = date.today().strftime("%Y%m%d")
    snap_file = fake_raw / f"ine_padron_2881_snapshot_{hoy_str}.json"
    snap_file.write_text(json.dumps(fake_payload), encoding="utf-8")
    mtime_antes = snap_file.stat().st_mtime

    ingestor = IngestorINEPadron(raw_dir=fake_raw)
    p, loaded_payload = ingestor.descargar_y_guardar_snapshot(overwrite=False)

    assert p == snap_file
    assert snap_file.stat().st_mtime == mtime_antes, "El snapshot inmutable no debe mutarse"
    datos = ingestor.procesar_poblacion_madrid(loaded_payload)
    assert "28125" in datos
    assert datos["28125"]["poblacion_oficial"] == 4818
    assert datos["28125"]["origen"] == "OBSERVADO"

def test_ckan_madrid_filtrado_semantico_alta_centros_educativos():
    """Verifica que solo se contabilicen centros en situación 'ALTA' y de enseñanza reglada."""
    ckan = IngestorCKANMadrid()
    mock_payload = {
        "result": {
            "records": [
                {"CDMUNI": 125, "CENTRO": "COLEGIO ACTIVO", "TIPO_ABRV": "CP INF-PRI", "SITUACIÓN": "ALTA"},
                {"CDMUNI": 125, "CENTRO": "COLEGIO DADO DE BAJA", "TIPO_ABRV": "CP INF-PRI", "SITUACIÓN": "BAJA"},
                {"CDMUNI": 125, "CENTRO": "CENTRO EN TRÁMITE", "TIPO_ABRV": "CP INF-PRI", "SITUACIÓN": "EN TRÁMITE"},
                {"CDMUNI": 125, "CENTRO": "ACADEMIA DE DANZA", "TIPO_ABRV": "DANZA", "SITUACIÓN": "ALTA"},
                {"CDMUNI": 125, "CENTRO": "IES ACTIVO", "TIPO_ABRV": "IES", "SITUACIÓN": "ALTA"}
            ]
        }
    }
    res = ckan.procesar_educacion(mock_payload, solo_reglada=True)
    assert "28125" in res
    # Solo deben contabilizarse el CP INF-PRI activo y el IES activo = 2
    assert res["28125"]["num_centros_educativos_ckan"] == 2

def test_cruce_20_municipios_con_snapshots_locales():
    """Verifica correspondencia de los 20 municipios piloto con los snapshots oficiales en data/raw."""
    panel_path = Path("data/validated/municipios_panel_validado.csv")
    df = pd.read_csv(panel_path)
    codigos_20 = set(df["codigo_ine"].astype(str).str.zfill(5))
    assert len(codigos_20) == 20

    # Último snapshot local disponible (sin fijar una fecha concreta)
    ine_snaps = sorted(Path("data/raw/ine").glob("ine_padron_2881_snapshot_*.json"))
    assert ine_snaps, "Debe existir al menos un snapshot INE en data/raw/ine/"
    ine_data = IngestorINEPadron().procesar_poblacion_madrid(
        json.loads(ine_snaps[-1].read_text(encoding="utf-8"))
    )
    for cod in codigos_20:
        assert cod in ine_data, f"Municipio {cod} no encontrado en snapshot INE"

    # Último snapshot CKAN Educación disponible
    edu_snaps = sorted(Path("data/raw/ckan").glob("ckan_madrid_educacion_snapshot_*.json"))
    assert edu_snaps, "Debe existir al menos un snapshot CKAN Educación en data/raw/ckan/"
    edu_data = IngestorCKANMadrid().procesar_educacion(
        json.loads(edu_snaps[-1].read_text(encoding="utf-8")), solo_reglada=True
    )
    for cod in codigos_20:
        assert cod in edu_data, f"Municipio {cod} no encontrado en snapshot Educación"

def test_calidad_y_procedencia_honesta_panel_validado():
    """Comprueba que el panel validado no enmascare variables sintéticas como 100% observadas."""
    panel_path = Path("data/validated/municipios_panel_validado.csv")
    df = pd.read_csv(panel_path)
    qg = ejecutar_quality_gates(df)
    assert qg["status"] == "PASSED"
    assert qg["filas_validadas"] == 20

    # Procedencia honesta
    assert (df["origen"] == "OBSERVADO+SIMULADO").all(), "El panel debe declarar origen mixto OBSERVADO+SIMULADO"
    for fd in df["fuente_datos"]:
        assert "SINT" in fd or "calibrado" in fd.lower(), "fuente_datos debe explicitar la presencia de datos sintéticos calibrados"
