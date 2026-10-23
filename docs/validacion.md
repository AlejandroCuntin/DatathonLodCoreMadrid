# Informe de Validación Rigurosa, Auditoría y Veredicto Formal
## Proyecto LoDCORE Madrid • II Datathon 2026

> **Regla `AGENTS.md`**: Todo número publicado en este documento procede de un fichero de resultados verificable en el repositorio (`metrics.json` y `shap_background.json`).

---

### 1. Veredicto Formal del Panel de Datos (Fase F2)

**Dictamen de Calidad**: **`APTO CON RESERVAS`**

#### 1.1 Justificación Técnica del Veredicto
- **Fuentes Oficiales Conectadas (F1.1)**:
  - **INE Padrón Municipal Continuo (Año 2025)**: Consumido vía API JSON oficial (tabla 2881) con snapshot inmutable fechado en `data/raw/ine/ine_padron_2881_snapshot_20261023.json`.
  - **CKAN Comunidad de Madrid (Sanidad)**: Recurso oficial de *Recursos y asistencia sanitaria por tipo*, snapshot inmutable en `data/raw/ckan/ckan_madrid_sanidad_snapshot_20261023.json`.
  - **CKAN Comunidad de Madrid (Educación)**: Directorio oficial de *Centros Educativos*, snapshot inmutable en `data/raw/ckan/ckan_madrid_educacion_snapshot_20261023.json`.
- **Identificación Estricta (F1.3)**: 100 % de los 20 municipios piloto casados mediante **código INE de 5 dígitos** (`28xxx`), eliminando cualquier ambigüedad toponímica o error por nombre.
- **Trazabilidad y Linaje por Celda**: Columnas `origen = 'OBSERVADO'`, `metodo = 'INE_PADRON_2025+CKAN_MADRID_DATOS_ABIERTOS'`, `dataset_version = 'v1.0.0-F2'` y `fecha_disponible = '2026-10-14'` registradas obligatoriamente.
- **Quality Gates (F2)**: 20 / 20 municipios superan las 18 validaciones de esquema, rangos $[0, 100]$ y punto-en-tiempo en `src/lodcore/data/quality_gates.py`.

#### 1.2 Modelos que el Panel Puede y NO Puede Alimentar
| Modelo | Veredicto para este Modelo | Justificación y Límites |
|---|---|---|
| **M2 — Indicadores e Isócronas** | **APTO** | Recálculo directo sobre centros de salud y colegios oficiales; 16/20 municipios cumplen el criterio de 30 min. |
| **M3 — Proyección Demográfica** | **APTO** | Población base 2025 verificada con Padrón INE oficial (200.267 hab. agregados); proyecciones 2030/2035 con bandas al 95%. |
| **M4 — Capacidad de Acogida (Core)** | **APTO** | Target determinista sobre dotaciones oficiales y reglas no compensatorias operativas ($>1.500$ hab/médico, $>95\%$ aulas). MAE CV comarcal: 5.15 ptos. |
| **M5 — Recomendador MCDM** | **APTO** | Clustering ($k=4$, silhouette 0.3183) y ranking con filtros de exclusión dura sobre infraestructura real. |
| **M1 — AVM Inmobiliario** | **APTO CON RESERVAS** | Con $n=20$ el modelo Random Forest tiene $R^2$ OOF negativo (-0.34) debido a alta varianza entre comarcas. **Veredicto**: Válido como estimador de esfuerzo y orden de magnitud relativo, pero **NO como tasación inmobiliaria de precisión comercial**. No debe presentarse al jurado como AVM cerrado. |

---

### 2. Puertas de Calidad y Punto-en-Tiempo (Fase F2)
- **Dataset validado**: `data/validated/municipios_panel_validado.csv` (`dataset_version = v1.0.0-F2`).
- **Municipios superados**: **20 / 20** (100 % cumplen población $< 50.000$ hab., no-nulidad de claves INE, rangos $[0, 100]$ en sub-índices y control `fecha_disponible <= fecha_decision`).
- **Evidencia**: `src/lodcore/data/quality_gates.py` y `tests/integration/test_pointintime.py`.

---

### 3. Resultados Auditados por Modelo (F3–F7)

| Modelo | Algoritmo | Esquema CV | Métrica Principal | Equivalencia ONNX (`max_abs_diff`) | Fichero de Evidencia |
|---|---|---|---|---|---|
| **M1 — AVM y Asequibilidad** | `RandomForestRegressor` | `Spatial_GroupKFold_Comarca` | MAE CV: **382.83 €/m²** ($\pm 230.20$) \| $R^2$ in-sample: **0.8032** | **`0.00e+00`** ($< 10^{-6}$) | `src/lodcore/models/m1_avm/metrics.json` |
| **M2 — Indicadores e Isócronas** | `PCA` + `MinMaxScaler` | Determinista (0–100) | 16/20 municipios en isócrona $\le 30$ min a polo de empleo | N/A | `src/lodcore/models/m2_indicadores/metrics.json` |
| **M3 — Proyección Demográfica** | `SARIMAX_EXOG_CI95` | Bandas 95 % a 5 y 10 años | Pob. 2025: **200.267** $\rightarrow$ 2030: **216.597** $\rightarrow$ 2035: **234.336** | N/A | `src/lodcore/models/m3_demografia/metrics.json` |
| **M4 — Capacidad de Acogida (Core)** | `GradientBoostingRegressor` + `SHAP` | `Spatial_GroupKFold_Comarca` | MAE CV: **5.15 ptos** ($\pm 3.42$) \| $R^2$ in-sample: **1.0000** | **`0.00e+00`** ($< 10^{-6}$) | `src/lodcore/models/m4_capacidad/metrics.json` |
| **M5 — Recomendador MCDM** | `KMeans (k=4)` + Coseno Ponderado | No supervisado + MCDM | Silhouette Score: **0.3183** \| Inercia: **78.41** | N/A | `src/lodcore/models/m5_recomendador/metrics.json` |

---

### 4. Auditoría de Explicabilidad SHAP y No-Compensatoriedad
- **Background persistido**: `src/lodcore/models/m4_capacidad/shap_background.json`
- **Hash SHA-256 de integridad**: `cdb4e87de3fcb51c...`
- **Auditoría léxica de no-causalidad**: Verificada automáticamente mediante expresiones regulares en `src/lodcore/explain/redaccion_natural.py` (`verificar_ausencia_causalidad`).
- **Pruebas adversariales de colapso**: Confirmado en `tests/unit/test_models.py` que cualquier municipio con $> 1.500\text{ hab/médico}$ o $> 95\%$ de ocupación escolar ve truncado su ICA a $< 40.0$ puntos (`semaforo_ica = BAJA`).
