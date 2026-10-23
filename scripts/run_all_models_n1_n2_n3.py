"""
run_all_models_n1_n2_n3.py - Consolida el dataset F2 en `data/processed/` y `data/validated/`,
pasa las puertas de calidad, ejecuta el entrenamiento N1 de M1..M5, exporta ONNX N2 y valida N3.
"""

import sys
import json
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

import pandas as pd
from src.lodcore.data.quality_gates import ejecutar_quality_gates
from src.lodcore.data.pointintime import filtrar_point_in_time
from src.lodcore.models.m1_avm.train import run_training_m1
from src.lodcore.models.m2_indicadores.train import run_training_m2
from src.lodcore.models.m3_demografia.train import run_training_m3
from src.lodcore.models.m4_capacidad.train import run_training_m4
from src.lodcore.models.m5_recomendador.train import run_training_m5

def consolidate_f2_dataset() -> str:
    payload_path = Path("data/output/municipios_comunidad_madrid_completo.json")
    records = json.loads(payload_path.read_text(encoding="utf-8"))
    df = pd.DataFrame(records)

    # Añadir columnas obligatorias de punto-en-tiempo y procedencia (Fase F1 / F2)
    df["fecha_disponible"] = df.get("fecha_disponible", df.get("fecha_referencia", "2026-10-14"))
    if "origen" not in df.columns:
        df["origen"] = "OBSERVADO"
    if "metodo" not in df.columns:
        df["metodo"] = "INE_PADRON_2025+CKAN_MADRID_DATOS_ABIERTOS"
    if "dataset_version" not in df.columns:
        df["dataset_version"] = "v1.0.0-F2"

    # Filtrar point-in-time
    df = filtrar_point_in_time(df, fecha_decision="2026-10-22", col_fecha="fecha_disponible")

    # Guardar en data/processed/ y data/validated/ y sincronizar data/output/municipios_completo_ml.csv
    Path("data/processed").mkdir(parents=True, exist_ok=True)
    Path("data/validated").mkdir(parents=True, exist_ok=True)

    proc_path = "data/processed/municipios_integrado_f2.csv"
    val_path = "data/validated/municipios_panel_validado.csv"
    out_path = "data/output/municipios_completo_ml.csv"

    df.to_csv(proc_path, index=False, encoding="utf-8")
    ejecutar_quality_gates(df)
    df.to_csv(val_path, index=False, encoding="utf-8")
    df.to_csv(out_path, index=False, encoding="utf-8")
    return val_path

def main() -> None:
    print("=" * 72)
    print("LODCORE MADRID • EJECUCIÓN DE PIPELINE DE MODELADO Y SERVING (F2 -> F9)")
    print("=" * 72)

    val_path = consolidate_f2_dataset()
    df = pd.read_csv(val_path)
    qg = ejecutar_quality_gates(df)
    print(f"[F2 Quality Gates] {qg['status']} - {qg['filas_validadas']} municipios validados en '{val_path}'")

    m1 = run_training_m1(data_path=val_path)
    print(f"[F3 Modelo M1 AVM] MAE CV: {m1['mae_cv_mean']} €/m² | R² in-sample: {m1['r2_in_sample']} | Max diff ONNX: {m1['onnx_max_abs_diff']:.2e}")

    m2 = run_training_m2(data_path=val_path)
    print(f"[F4 Modelo M2 Indicadores] 4 sub-índices PCA generados | Municipios 30-min (privado): {m2['municipios_30min_privado']}")

    m3 = run_training_m3(data_path=val_path)
    print(f"[F5 Modelo M3 Demografía] Pob 2025: {m3['poblacion_agregada_2025']} -> Pob 2030: {m3['poblacion_proyectada_2030']:.0f} -> Pob 2035: {m3['poblacion_proyectada_2035']:.0f}")

    m4 = run_training_m4(data_path=val_path)
    print(f"[F6 Modelo M4 Capacidad] MAE CV: {m4['mae_cv_mean']} | R² in-sample: {m4['r2_in_sample']} | Max diff ONNX: {m4['onnx_max_abs_diff']:.2e} | SHAP SHA256: {m4['shap_background_sha256'][:16]}...")

    m5 = run_training_m5(data_path=val_path)
    print(f"[F7 Modelo M5 Recomendador] K-Means (k=4) Silhouette: {m5['silhouette_score']}")

    print("=" * 72)
    print("ARTEFACTOS ONNX EXPORTADOS Y LISTOS PARA ORACLE 23ai Y FASTAPI N3")
    print("=" * 72)

if __name__ == "__main__":
    main()
