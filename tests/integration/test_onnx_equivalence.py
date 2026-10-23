"""
test_onnx_equivalence.py - Prueba de integración obligatoria (Fase F8 / F9):

Verifica la equivalencia numérica entre la predicción NATIVA de scikit-learn y el
binario ONNX que se carga en Oracle:

  - error relativo < 1e-6
  - error absoluto < 1e-3

El binario ONNX devuelve float32; exigir un error absoluto < 1e-6 a magnitudes de
2.000 €/m² no es representable. El test también comprueba de forma explícita que
`model.predict()` NO delega en ONNX (regresión del bug que hacía tautológica la
comparación ONNX contra ONNX).
"""

import joblib
import numpy as np
import onnx
import pandas as pd

from src.lodcore.models.base import comparar_equivalencia_onnx
from src.lodcore.models.m1_avm.train import FEATURES_M1, M1AVMModel
from src.lodcore.models.m4_capacidad.train import FEATURES_M4, M4CapacidadModel


def _assert_equivalencia(model, X, ruta_onnx: str, etiqueta: str) -> None:
    preds_py = model.predict(X)
    preds_onnx = model.predict_onnx(ruta_onnx, X)
    resultado = comparar_equivalencia_onnx(preds_py, preds_onnx)
    assert resultado["onnx_equivalence_passed"], (
        f"Divergencia Python vs ONNX en {etiqueta}: "
        f"abs={resultado['onnx_max_abs_diff']:.3e}, "
        f"rel={resultado['onnx_max_rel_diff']:.3e}"
    )


def test_contrato_nombres_onnx_para_oracle():
    """El DDL 05 mapea `float_input` -> columnas y `variable` -> regressionOutput."""
    for ruta, n_features in (
        ("oracle/onnx/m1_avm.onnx", len(FEATURES_M1)),
        ("oracle/onnx/m4_capacidad.onnx", len(FEATURES_M4)),
    ):
        modelo = onnx.load(ruta)
        entradas = list(modelo.graph.input)
        salidas = list(modelo.graph.output)
        assert len(entradas) == 1 and entradas[0].name == "float_input", ruta
        assert entradas[0].type.tensor_type.shape.dim[1].dim_value == n_features, ruta
        assert len(salidas) == 1 and salidas[0].name == "variable", ruta


def test_predict_usa_sklearn_y_no_onnx():
    """Regresión: `predict()` debe ejecutar el estimador nativo, no el grafo ONNX."""
    df = pd.read_csv("data/validated/municipios_panel_validado.csv")
    X = df[FEATURES_M1].to_numpy(dtype=np.float32)
    model: M1AVMModel = joblib.load("src/lodcore/models/m1_avm/model.joblib")

    preds_predict = model.predict(X)
    preds_estimator = model.estimator.predict(X)
    assert np.array_equal(preds_predict, preds_estimator)


def test_m1_avm_onnx_equivalence():
    df = pd.read_csv("data/validated/municipios_panel_validado.csv")
    X = df[FEATURES_M1].to_numpy(dtype=np.float32)

    model: M1AVMModel = joblib.load("src/lodcore/models/m1_avm/model.joblib")
    _assert_equivalencia(model, X, "src/lodcore/models/m1_avm/model.onnx", "M1")
    _assert_equivalencia(model, X, "oracle/onnx/m1_avm.onnx", "M1 (copia Oracle)")


def test_m4_capacidad_onnx_equivalence():
    df = pd.read_csv("data/validated/municipios_panel_validado.csv")
    X = df[FEATURES_M4].to_numpy(dtype=np.float32)

    model: M4CapacidadModel = joblib.load("src/lodcore/models/m4_capacidad/model.joblib")
    _assert_equivalencia(model, X, "src/lodcore/models/m4_capacidad/model.onnx", "M4")
    _assert_equivalencia(model, X, "oracle/onnx/m4_capacidad.onnx", "M4 (copia Oracle)")
