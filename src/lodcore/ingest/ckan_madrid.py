"""
ckan_madrid.py - Conector oficial al Portal de Datos Abiertos de la Comunidad de Madrid (CKAN).
Fase F1.1 / F1.2 / F1.3 - Ingesta de Sanidad y Educación, snapshot inmutable y cruce por código INE.
"""

from __future__ import annotations

import json
import logging
import urllib.request
from datetime import date
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

logger = logging.getLogger("lodcore.ingest.ckan")

CKAN_BASE_URL = "https://datos.comunidad.madrid/api/3/action"
RESOURCE_ID_SANIDAD = "631ebd15-c19f-4984-9ad5-bb4b8554b5e0"   # Recursos y asistencia sanitaria por tipo
RESOURCE_ID_EDUCACION = "28d60557-1d73-4281-ab08-6cfd3b2f5f83" # Centros educativos de la CAM

class IngestorCKANMadrid:
    """
    Ingesta de equipamientos de Sanidad y Educación desde el CKAN de la Comunidad de Madrid.
    Garantiza:
    - Snapshot inmutable en data/raw/ckan/
    - Mapeo estricto a código INE de 5 dígitos (28xxx)
    - Trazabilidad y linaje formal
    """

    def __init__(self, raw_dir: Optional[Path] = None):
        if raw_dir is None:
            self.raw_dir = Path("data/raw/ckan")
        else:
            self.raw_dir = Path(raw_dir)
        self.raw_dir.mkdir(parents=True, exist_ok=True)

    def _fetch_datastore(self, resource_id: str, limit: int = 10000, timeout: int = 25) -> Dict[str, Any]:
        url = f"{CKAN_BASE_URL}/datastore_search?resource_id={resource_id}&limit={limit}"
        req = urllib.request.Request(
            url,
            headers={
                "User-Agent": "LoDCORE-Madrid-Datathon/2.0 (UC3M-CAM; contact: lodcore@madrid.gov)",
                "Accept": "application/json"
            }
        )
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            raw_bytes = resp.read()
        return json.loads(raw_bytes.decode("utf-8", errors="replace"))

    def descargar_y_guardar_snapshot_sanidad(self, timeout: int = 25) -> Tuple[Path, Dict[str, Any]]:
        """Descarga centros sanitarios por tipo y persiste snapshot inmutable."""
        fecha_str = date.today().strftime("%Y%m%d")
        snapshot_path = self.raw_dir / f"ckan_madrid_sanidad_snapshot_{fecha_str}.json"

        try:
            payload = self._fetch_datastore(RESOURCE_ID_SANIDAD, limit=10000, timeout=timeout)
            snapshot_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
            logger.info("Snapshot CKAN Sanidad guardado en: %s", snapshot_path)
            return snapshot_path, payload
        except Exception as exc:
            logger.warning("Error descargando CKAN Sanidad: %s. Buscando snapshot previo...", exc)
            previos = sorted(self.raw_dir.glob("ckan_madrid_sanidad_snapshot_*.json"), reverse=True)
            if previos:
                logger.info("Usando snapshot previo de Sanidad: %s", previos[0])
                return previos[0], json.loads(previos[0].read_text(encoding="utf-8"))
            raise RuntimeError("No se pudo conectar a CKAN Sanidad ni hay snapshot previo.") from exc

    def descargar_y_guardar_snapshot_educacion(self, timeout: int = 25) -> Tuple[Path, Dict[str, Any]]:
        """Descarga centros educativos y persiste snapshot inmutable."""
        fecha_str = date.today().strftime("%Y%m%d")
        snapshot_path = self.raw_dir / f"ckan_madrid_educacion_snapshot_{fecha_str}.json"

        try:
            payload = self._fetch_datastore(RESOURCE_ID_EDUCACION, limit=10000, timeout=timeout)
            snapshot_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
            logger.info("Snapshot CKAN Educación guardado en: %s", snapshot_path)
            return snapshot_path, payload
        except Exception as exc:
            logger.warning("Error descargando CKAN Educación: %s. Buscando snapshot previo...", exc)
            previos = sorted(self.raw_dir.glob("ckan_madrid_educacion_snapshot_*.json"), reverse=True)
            if previos:
                logger.info("Usando snapshot previo de Educación: %s", previos[0])
                return previos[0], json.loads(previos[0].read_text(encoding="utf-8"))
            raise RuntimeError("No se pudo conectar a CKAN Educación ni hay snapshot previo.") from exc

    def procesar_sanidad(self, payload: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
        """
        Agrupa los centros sanitarios (centros de salud y consultorios) del año más reciente
        por código INE de 5 dígitos estricto.
        En las fuentes estadísticas de la CAM, 'Código territorio' codifica el municipio
        con dígito de control INE (ej. 1258 -> municipio 125 -> 28125; 275 -> 27 -> 28027).
        """
        records: List[Dict[str, Any]] = payload.get("result", {}).get("records", [])
        if not records:
            return {}

        # Determinar clave de año de forma tolerante a codificación de eñe
        k_anio = next((k for k in records[0].keys() if "o" in k.lower() and len(k) <= 4), "Año")
        k_cod = next((k for k in records[0].keys() if "digo" in k.lower() and "territorio" in k.lower()), "Código territorio")

        # Filtrar solo registros a nivel Municipio
        recs_muni = [r for r in records if r.get("Tipo territorio") in ("Municipios", "Municipio") and r.get(k_cod) is not None]
        if not recs_muni:
            return {}

        anio_max = max(int(r.get(k_anio, 0)) for r in recs_muni)

        sanidad_por_ine: Dict[str, Dict[str, Any]] = {}
        for r in recs_muni:
            if int(r.get(k_anio, 0)) != anio_max:
                continue

            cod_val = r.get(k_cod)
            if cod_val is None or not str(cod_val).isdigit():
                continue

            s = str(cod_val)
            # El código de municipio oficial INE se obtiene retirando el dígito de control final
            if len(s) >= 2:
                muni_num = int(s[:-1])
                codigo_ine = f"28{muni_num:03d}"
            else:
                continue

            tipo = str(r.get("Tipo", "")).strip().lower()
            try:
                valor = int(r.get("Valor", 0))
            except (ValueError, TypeError):
                valor = 0

            if codigo_ine not in sanidad_por_ine:
                sanidad_por_ine[codigo_ine] = {
                    "codigo_ine": codigo_ine,
                    "nombre_territorio": r.get("Territorio", ""),
                    "num_centros_salud_ckan": 0,
                    "num_consultorios_ckan": 0,
                    "anio_referencia": anio_max,
                    "origen": "OBSERVADO",
                    "metodo": "CKAN_MADRID_CENTROS_SANITARIOS_POR_TIPO",
                    "fuente_datos": f"CKAN Comunidad de Madrid (Recursos sanitarios por tipo, tabla oficial, año {anio_max})"
                }

            if "salud" in tipo and "consultorio" not in tipo:
                sanidad_por_ine[codigo_ine]["num_centros_salud_ckan"] += valor
            elif "consultorio" in tipo and "salud" not in tipo:
                sanidad_por_ine[codigo_ine]["num_consultorios_ckan"] += valor
            elif "consultorios locales y centros de salud" in tipo:
                if sanidad_por_ine[codigo_ine]["num_centros_salud_ckan"] == 0:
                    sanidad_por_ine[codigo_ine]["num_centros_salud_ckan"] = valor

        return sanidad_por_ine

    def procesar_educacion(self, payload: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
        """
        Agrupa los centros educativos activos por código INE de 5 dígitos: f'28{int(CDMUNI):03d}'.
        """
        records: List[Dict[str, Any]] = payload.get("result", {}).get("records", [])
        if not records:
            return {}

        educacion_por_ine: Dict[str, Dict[str, Any]] = {}
        for r in records:
            # Filtrar centros dados de baja si el campo SITUACIÓN está disponible
            situacion = str(r.get("SITUACIÓN", r.get("SITUACIN", ""))).upper()
            if "BAJA" in situacion:
                continue

            cdmuni = r.get("CDMUNI")
            if cdmuni is None:
                continue

            try:
                cod_num = int(cdmuni)
            except (ValueError, TypeError):
                continue

            codigo_ine = f"28{cod_num:03d}"
            if codigo_ine not in educacion_por_ine:
                educacion_por_ine[codigo_ine] = {
                    "codigo_ine": codigo_ine,
                    "num_centros_educativos_ckan": 0,
                    "origen": "OBSERVADO",
                    "metodo": "CKAN_MADRID_CENTROS_EDUCATIVOS",
                    "fuente_datos": "CKAN Comunidad de Madrid (Directorio oficial de Centros Educativos)"
                }

            educacion_por_ine[codigo_ine]["num_centros_educativos_ckan"] += 1

        return educacion_por_ine
