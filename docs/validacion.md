# Informe de Validación Rigurosa y Auditoría (Fase F8)
## Proyecto LoDCORE Madrid • II Datathon 2026

> **Regla `AGENTS.md`**: Todo número publicado en este documento procede de un fichero de resultados verificable en el repositorio (`metrics.json` y `shap_background.json`).

---

### 1. Puertas de Calidad y Punto-en-Tiempo (Fase F2)
- **Dataset validado**: `data/validated/municipios_panel_validado.csv` (`dataset_version = v1.0.0-F2`).
- **Municipios superados**: **20 / 20** (100 % cumplen población $< 50.000$ hab., no-nulidad de claves INE, rangos $[0, 100]$ en sub-índices y control `fecha_disponible <= fecha_decision`).
- **Evidencia**: `src/lodcore/data/quality_gates.py` y `tests/integration/test_pointintime.py`.

---

### 2. Resultados Auditados por Modelo (F3–F7)

| Modelo | Algoritmo | Esquema CV | Métrica Principal | Equivalencia ONNX (`max_abs_diff`) | Fichero de Evidencia |
|---|---|---|---|---|---|
| **M1 — AVM y Asequibilidad** | `RandomForestRegressor` | `Spatial_GroupKFold_Comarca` | MAE CV: **382.83 €/m²** ($\pm 230.20$) \| $R^2$ in-sample: **0.8032** | **`0.00e+00`** ($< 10^{-6}$) | `src/lodcore/models/m1_avm/metrics.json` |
| **M2 — Indicadores e Isócronas** | `PCA` + `MinMaxScaler` | Determinista (0–100) | 16/20 municipios en isócrona $\le 30$ min a polo de empleo | N/A | `src/lodcore/models/m2_indicadores/metrics.json` |
| **M3 — Proyección Demográfica** | `SARIMAX_EXOG_CI95` | Bandas 95 % a 5 y 10 años | Pob. 2025: **200.267** $\rightarrow$ 2030: **216.597** $\rightarrow$ 2035: **234.336** | N/A | `src/lodcore/models/m3_demografia/metrics.json` |
| **M4 — Capacidad de Acogida (Core)** | `GradientBoostingRegressor` + `SHAP` | `Spatial_GroupKFold_Comarca` | MAE CV: **5.15 ptos** ($\pm 3.42$) \| $R^2$ in-sample: **1.0000** | **`0.00e+00`** ($< 10^{-6}$) | `src/lodcore/models/m4_capacidad/metrics.json` |
| **M5 — Recomendador MCDM** | `KMeans (k=4)` + Coseno Ponderado | No supervisado + MCDM | Silhouette Score: **0.3183** \| Inercia: **78.41** | N/A | `src/lodcore/models/m5_recomendador/metrics.json` |

---

### 3. Auditoría de Explicabilidad SHAP y No-Compensatoriedad
- **Background persistido**: `src/lodcore/models/m4_capacidad/shap_background.json`
- **Hash SHA-256 de integridad**: `cdb4e87de3fcb51c...`
- **Auditoría léxica de no-causalidad**: Verificada automáticamente mediante expresiones regulares en `src/lodcore/explain/redaccion_natural.py` (`verificar_ausencia_causalidad`).
- **Pruebas adversariales de colapso**: Confirmado en `tests/unit/test_models.py` que cualquier municipio con $> 1.500\text{ hab/médico}$ o $> 95\%$ de ocupación escolar ve truncado su ICA a $< 40.0$ puntos (`semaforo_ica = BAJA`).
