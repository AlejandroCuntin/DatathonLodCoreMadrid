"""
train.py - Entrenamiento del Modelo M5 (Clustering no supervisado de tipologías municipales K-Means)
y exportación de `clustering.json` y `metrics.json`.
"""

import json
from pathlib import Path
from typing import Dict, Any
import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import silhouette_score
from src.lodcore.data.provenance import TipoOrigen

FEATURES_M5_CLUSTER = [
    "score_sanidad",
    "score_educacion",
    "score_conectividad",
    "score_vivienda",
    "tiempo_medio_madrid_minutos",
    "precio_m2_compra",
    "densidad"
]

NOMBRES_ARQUETIPOS = {
    0: "Nodos Metropolitanos y Corredores Dinámicos",
    1: "Cabeceras Comarcales Equilibradas",
    2: "Pueblos Conectados de Calidad Ambiental y Teletrabajo",
    3: "Reserva de Oportunidad Residencial y Suelo Asequible"
}

def run_training_m5(
    data_path: str = "data/output/municipios_completo_ml.csv",
    out_dir: str = "src/lodcore/models/m5_recomendador"
) -> Dict[str, Any]:
    df = pd.read_csv(data_path)
    X_raw = df[FEATURES_M5_CLUSTER].to_numpy(dtype=np.float64)
    scaler = StandardScaler()
    X_std = scaler.fit_transform(X_raw)

    kmeans = KMeans(n_clusters=4, n_init=20, random_state=2026)
    labels = kmeans.fit_predict(X_std)
    sil_score = float(silhouette_score(X_std, labels))

    asignaciones = []
    for idx, row in df.iterrows():
        cid = int(labels[idx])
        asignaciones.append({
            "id_municipio": int(row["id_municipio"]),
            "codigo_ine": int(row["codigo_ine"]),
            "nombre": str(row["nombre"]),
            "cluster_id": cid,
            "tipologia_m5": NOMBRES_ARQUETIPOS.get(cid, f"Tipología {cid}"),
            "arquetipo_actual": str(row.get("arquetipo_nombre", ""))
        })

    metrics = {
        "model_name": "M5_CLUSTERING_MCDM_COSINE",
        "algorithm": "KMeans_k4_WeightedCosine",
        "n_clusters": 4,
        "silhouette_score": round(sil_score, 4),
        "inertia": round(float(kmeans.inertia_), 2),
        "n_municipios": int(len(df)),
        "dataset_version": "v1.0.0-F2",
        "origen": TipoOrigen.ESTIMADO.value,
        "metodo": "KMEANS_STD_SILHOUETTE"
    }

    out_p = Path(out_dir)
    out_p.mkdir(parents=True, exist_ok=True)
    (out_p / "clustering.json").write_text(
        json.dumps({"clusters": asignaciones, "centroids_features": FEATURES_M5_CLUSTER}, indent=2, ensure_ascii=False),
        encoding="utf-8"
    )
    (out_p / "metrics.json").write_text(json.dumps(metrics, indent=2, ensure_ascii=False), encoding="utf-8")
    return metrics

if __name__ == "__main__":
    m = run_training_m5()
    print(f"[M5 Recomendador] Clustering completado. Silhouette score: {m['silhouette_score']}")
