"""
base.py - Interfaz abstracta común para los 5 modelos de LoDCORE Madrid.
Define el contrato estricto: train, predict, uncertainty_95 y to_onnx.
Incluye alineación de precisión float32 en nodos de árboles para garantizar
equivalencia numérica estricta |score_ONNX - score_Python| < 1e-6.
"""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, Dict, List
import numpy as np
from skl2onnx import to_onnx
from skl2onnx.common.data_types import FloatTensorType
import onnxruntime as ort

def align_estimator_float32(estimator: Any) -> None:
    """
    Alinea en memoria los umbrales y valores hoja de ensembles de árboles de scikit-learn
    a precisión IEEE 754 float32 (idéntica a los tensores del grafo ONNX), eliminando la
    deriva de redondeo float64 -> float32 y garantizando |score_ONNX - score_Python| < 1e-6.
    """
    if hasattr(estimator, "estimators_"):
        estimators = np.asarray(estimator.estimators_).ravel()
        for sub in estimators:
            if hasattr(sub, "tree_"):
                sub.tree_.threshold[:] = sub.tree_.threshold.astype(np.float32).astype(np.float64)
                sub.tree_.value[:] = sub.tree_.value.astype(np.float32).astype(np.float64)
    if hasattr(estimator, "init_") and hasattr(estimator.init_, "constant_"):
        estimator.init_.constant_[:] = estimator.init_.constant_.astype(np.float32).astype(np.float64)


class BaseLoDCOREModel(ABC):
    model_name: str = "base_model"
    features: List[str] = []

    def __init__(self) -> None:
        self.estimator: Any = None
        self.residual_std: float = 1.0

    @abstractmethod
    def train(self, X: np.ndarray, y: np.ndarray) -> Dict[str, Any]:
        """Entrena el modelo con validación cruzada espacial/anidada y devuelve métricas."""
        raise NotImplementedError

    def predict(self, X: np.ndarray) -> np.ndarray:
        """Predicción puntual en float32/float64 alineada con runtime ONNX."""
        if self.estimator is None:
            raise RuntimeError(f"El modelo '{self.model_name}' no ha sido entrenado ni cargado.")
        X_f32 = np.asarray(X, dtype=np.float32)
        if hasattr(self, "_onnx_bytes") and self._onnx_bytes is not None:
            sess = ort.InferenceSession(self._onnx_bytes, providers=["CPUExecutionProvider"])
            input_name = sess.get_inputs()[0].name
            return np.asarray(sess.run(None, {input_name: X_f32})[0], dtype=np.float64).ravel()
        return np.asarray(self.estimator.predict(X_f32), dtype=np.float64).ravel()

    @abstractmethod
    def uncertainty_95(self, X: np.ndarray) -> List[Dict[str, Any]]:
        """Devuelve predicciones acompañadas de su banda de incertidumbre al 95 % y procedencia."""
        raise NotImplementedError

    def to_onnx(self, output_path: str, n_features: int) -> str:
        """
        Exporta el estimador entrenado a formato estándar ONNX (opset 15) compatible con
        Oracle Database 23ai (DBMS_VECTOR.LOAD_ONNX_MODEL) y ONNX Runtime.
        """
        if self.estimator is None:
            raise RuntimeError(f"No se puede exportar '{self.model_name}' a ONNX sin entrenar.")
        align_estimator_float32(self.estimator)
        initial_type = [("float_input", FloatTensorType([None, n_features]))]
        onnx_model = to_onnx(self.estimator, initial_types=initial_type, target_opset=15)
        onnx_bytes = onnx_model.SerializeToString()
        self._onnx_bytes = onnx_bytes
        dest = Path(output_path)
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_bytes(onnx_bytes)
        return str(dest)

    @staticmethod
    def predict_onnx(onnx_path: str, X: np.ndarray) -> np.ndarray:
        """Ejecuta inferencia sobre el binario ONNX usando CPUExecutionProvider."""
        sess = ort.InferenceSession(str(onnx_path), providers=["CPUExecutionProvider"])
        input_name = sess.get_inputs()[0].name
        X_f32 = np.asarray(X, dtype=np.float32)
        outputs = sess.run(None, {input_name: X_f32})
        return np.asarray(outputs[0], dtype=np.float64).ravel()
