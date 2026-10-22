"""
test_onnx_equivalence.py - Prueba de integración obligatoria (Fase F8 / F9):
Verifica equivalencia numérica estricta |score_ONNX - score_Python| < 1e-6
para los modelos exportados a ONNX (M1 AVM y M4 Capacidad de Acogida).
"""

import joblib
import numpy as np
import pandas as pd

from src.lodcore.models.m1_avm.train import FEATURES_M1, M1AVMModel
from src.lodcore.models.m4_capacidad.train import FEATURES_M4, M4CapacidadModel

def test_m1_avm_onnx_equivalence():
    df = pd.read_csv("data/validated/municipios_panel_validado.csv")
    X = df[FEATURES_M1].to_numpy(dtype=np.float32)

    model: M1AVMModel = joblib.load("src/lodcore/models/m1_avm/model.joblib")
    preds_py = model.predict(X)
    preds_onnx = model.predict_onnx("src/lodcore/models/m1_avm/model.onnx", X)
    preds_oracle_onnx = model.predict_onnx("oracle/onnx/m1_avm.onnx", X)

    max_diff = float(np.max(np.abs(preds_py - preds_onnx)))
    max_diff_oracle = float(np.max(np.abs(preds_py - preds_oracle_onnx)))

    assert max_diff < 1e-6, f"Divergencia superior a 1e-6 en M1 ONNX: {max_diff}"
    assert max_diff_oracle < 1e-6, f"Divergencia en copia Oracle M1 ONNX: {max_diff_oracle}"

def test_m4_capacidad_onnx_equivalence():
    df = pd.read_csv("data/validated/municipios_panel_validado.csv")
    X = df[FEATURES_M4].to_numpy(dtype=np.float32)

    model: M4CapacidadModel = joblib.load("src/lodcore/models/m4_capacidad/model.joblib")
    preds_py = model.predict(X)
    preds_onnx = model.predict_onnx("src/lodcore/models/m4_capacidad/model.onnx", X)
    preds_oracle_onnx = model.predict_onnx("oracle/onnx/m4_capacidad.onnx", X)

    max_diff = float(np.max(np.abs(preds_py - preds_onnx)))
    max_diff_oracle = float(np.max(np.abs(preds_py - preds_oracle_onnx)))

    assert max_diff < 1e-6, f"Divergencia superior a 1e-6 en M4 ONNX: {max_diff}"
    assert max_diff_oracle < 1e-6, f"Divergencia en copia Oracle M4 ONNX: {max_diff_oracle}"
