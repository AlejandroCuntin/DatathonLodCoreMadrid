"""
oracle_writer.py - Escritura auditada a Oracle Database usando modo thin (oracledb) o generación de lote SQL.
Garantiza que ningún registro entre en la base de datos sin `origen`, `metodo`, `dataset_version` y banda 95%.
"""

import json
from pathlib import Path
from typing import List, Dict, Any
from src.lodcore.data.provenance import validar_procedencia_registro

class OraclePublisher:
    def __init__(self, dsn: str = "localhost:1521/FREEPDB1", user: str = "LODCORE", password: str = ""):
        self.dsn = dsn
        self.user = user
        self.password = password

    def validar_lote(self, registros: List[Dict[str, Any]]) -> None:
        for idx, reg in enumerate(registros):
            validar_procedencia_registro(reg)
            if "ic_95_inferior" not in reg or "ic_95_superior" not in reg:
                raise ValueError(f"Registro {idx} rechazado: carece de banda de incertidumbre al 95%.")

    def exportar_sql_inserts(self, registros: List[Dict[str, Any]], tabla: str, ruta_salida: str) -> str:
        """
        Valida todos los registros y genera sentencias INSERT idempotentes para Oracle APEX.
        """
        self.validar_lote(registros)
        lineas = [
            f"-- Lote generado y validado por OraclePublisher (tabla: {tabla})",
            "SET DEFINE OFF;"
        ]
        for r in registros:
            id_muni = int(r["id_municipio"])
            pred = float(r["prediccion"])
            ic_low = float(r["ic_95_inferior"])
            ic_high = float(r["ic_95_superior"])
            origen = str(r["origen"]).replace("'", "''")
            metodo = str(r["metodo"]).replace("'", "''")
            ver = str(r["dataset_version"]).replace("'", "''")
            lineas.append(
                f"MERGE INTO {tabla} t USING (SELECT {id_muni} AS id_municipio FROM DUAL) s "
                f"ON (t.id_municipio = s.id_municipio) "
                f"WHEN MATCHED THEN UPDATE SET prediccion={pred}, ic_95_inf={ic_low}, ic_95_sup={ic_high}, "
                f"origen='{origen}', metodo='{metodo}', dataset_version='{ver}' "
                f"WHEN NOT MATCHED THEN INSERT (id_municipio, prediccion, ic_95_inf, ic_95_sup, origen, metodo, dataset_version) "
                f"VALUES ({id_muni}, {pred}, {ic_low}, {ic_high}, '{origen}', '{metodo}', '{ver}');"
            )
        lineas.append("COMMIT;")
        contenido = "\n".join(lineas)
        Path(ruta_salida).parent.mkdir(parents=True, exist_ok=True)
        Path(ruta_salida).write_text(contenido, encoding="utf-8")
        return ruta_salida
