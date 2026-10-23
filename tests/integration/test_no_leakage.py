"""
test_no_leakage.py - Verifica ausencia de fuga espacial (GroupKFold por comarca)
y ausencia de fuga entre fases (las features de M4 no incluyen proyecciones futuras de M3).
"""

import numpy as np
import pandas as pd
from sklearn.model_selection import GroupKFold

from src.lodcore.models.m4_capacidad.train import FEATURES_M4

def test_spatial_groupkfold_no_comarca_overlap():
    df = pd.read_csv("data/validated/municipios_panel_validado.csv")
    groups = df["comarca"].to_numpy()
    gkf = GroupKFold(n_splits=5)
    for train_idx, val_idx in gkf.split(df, groups=groups):
        comarcas_train = set(groups[train_idx])
        comarcas_val = set(groups[val_idx])
        assert comarcas_train.isdisjoint(comarcas_val), "Fuga espacial: la misma comarca aparece en train y test"

def test_no_leakage_between_m3_future_and_m4_features():
    columnas_futuras_m3 = {"poblacion_2027", "poblacion_2029", "poblacion_2031", "anio_estimado_saturacion"}
    interseccion = set(FEATURES_M4).intersection(columnas_futuras_m3)
    assert len(interseccion) == 0, f"Fuga entre fases detectada en M4: {interseccion}"
