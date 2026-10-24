# LoDCORE — Análisis del proyecto y arquitectura recomendada

> Documento de trabajo derivado de la lectura íntegra de los tres PDF del datathon
> (*Diseño e Implementación de la Solución*, *Fuentes de datos*, *Prototipo de interfaz*).

---

## 1. Qué es LoDCORE

**LoDCORE** = *Sistema Predictivo & Recomendador Explicable* para los **41 municipios de la
Comunidad de Madrid con menos de 50.000 habitantes** (INE & CAM 2026).

Problema: existe una **asimetría entre atractivo residencial y capacidad real de acogida**.
Un municipio puede ser muy atractivo (suelo barato, calidad ambiental) y aun así carecer de
residuo o músculo presupuestario para absorber un rápido incremento poblacional.

La tesis que la interfaz vende: *"El crecimiento demográfico no debe traducirse en saturación,
sino en nuevas oportunidades de desarrollo"*.

### Doble destinatario

| Perfil | Producto | Pregunta que responde |
|---|---|---|
| **Ciudadanía / futuros residentes** (jóvenes que se emancipan, familias, teletrabajadores, mayores) | **Portal Ciudadano** — Quiz & Recomendador, Comparador (radar), Ficha Municipal & SHAP | *¿Qué municipios se ajustan a mi perfil, presupuesto y estilo de vida, sin riesgo de saturación a medio plazo?* |
| **Administraciones y planificadores** (DGT Reequilibrio Territorial, ayuntamientos, consorcios) | **Panel Institucional** — Cuadro de Mando, Simulador What-If, Escenarios de Crecimiento | *¿Qué municipios van a sufrir tensiones entre llegada de población y dotaciones actuales, y dónde asigno inversión?* |

### Stack declarado

`Datos públicos abiertos` → `Python` → `Oracle Database` → `Oracle APEX`

---

## 2. Los 5 modelos (cadena) y los 7 factores

```
 7 FACTORES                      5 MODELOS ENCADENADOS                       SALIDA
┌───────────────────┐
│ F1 Demografía     │
│ F2 Vivienda        │
│ F3 Transporte      │
│ F4 Sanidad/Educac. │──▶ [M1] AVM  RF/LGBM ──▶ precio €/m², esfuerzo      ┌──────────────┐
│ F5 Neces. ciudad.  │──▶ [M2] PCA + isócronas ─▶ sub-índices 0-100     │ Índice ICA   │
│ F6 Sostenib. amb.  │──▶ [M3] SARIMAX/Prophet ─▶ población +5/+10 años  │ Semáforo     │
│ F7 Presupuestos    │──▶ [M4] XGBoost + SHAP ─▶ Capacidad de Acogida    │ Explicación  │
└───────────────────┘──▶ [M5] K-Means/GMM + MCDM ─▶ ranking + tipología   └──────────────┘
                                     │
                              41 municipios × ~10-20 años
```

| # | Modelo | Algoritmo | Entrada principal | Qué produce |
|---|---|---|---|---|
| **M1** | Estimación Inmobiliaria y Asequibilidad | **Random Forest / LightGBM (Gradient Boosting)** | Catastro, Ministerio de Transportes, renta media por hogar (INE) | precio justo €/m² (compra y alquiler), **esfuerzo financiero familiar** |
| **M2** | Indicadores de Capacidad e Infraestructura | **PCA + MinMaxScaler** y **grafos** (Dijkstra/A* sobre OSM + GTFS) | GTFS CRTM/Cercanías/Renfe, red viaria, centros sanitarios y educativos, residuos, zonas verdes, riesgo incendios, presupuestos per cápita | 4 sub-índices 0-100: Capacidad Sanitaria/Educativa, Conectividad y Movilidad, Sostenibilidad Ambiental, Músculo Presupuestario/Inversor |
| **M3** | Proyección Demográfica | **SARIMAX / Prophet** | Padrón Municipal (INE/IECM), pirámide de edad, saldos migratorios, proyecciones oficiales | población a 5 y 10 años con **bandas de incertidumbre** y exógenas (precio Madrid capital, presupuesto de inversión municipal) |
| **M4** | Modelo de Capacidad de Acogida | **XGBoost Regressor + SHAP** | Todos los factores: demanda proyectada (M3) vs oferta vivienda (M1), servicios, transporte, TwiceM he'd | Índice ICA futuro, simulación What-If, **cuellos de botella** por municipio |
| **M5** | Recomendador Inteligente | **K-Means / GMM + similitud del coseno ponderada (MCDM)** | Estructura de hogares, distribución por edades, preferencias del questionnaire | tipologías territoriales (nodos metropolitanos dinámicos, municipios familiares ambientales, pueblos rurales conectados) + ranking personalizado con **exclusión** |

### Reglas de negocio visibles en el prototipo (hard-coded en la UI)

- Ratio sanitario crítico: **> 1.500 hab/médico** → colapso.
- Ocupación escolar crítica: **> 95 %** de ocupación en aulas.
- Semáforo ICA Global: **Baja (<40) / Media (40-59) / Alta (≥60)**.
- Alerta global: **Holdura / Tensión / Colapso Crítico**; semáforo de alerta: **Sostenible / Crítico**.
- Escenario de estrés: **+5 % / +10 %** de población.
- Criterio de accesibilidad: **isócrona de 30 minutos**, transporte público vs. privado.

> ⚠️ **Hallazgo crítico**: la hipótesis de complementariedad *no compensatoria* ("la carencia severa de
> un servicio crítico no se compensa con zonas verdes o suelo") **NO está implementada en M4**.
> XGBoost es compensatorio por construcción. Es el gap técnico más importante del proyecto y
> donde un prompt de revisión adversarial es obligatorio.

---

## 3. Fuentes de datos (ya inventariadas en `Fuentes de datos.pdf`)

| Bloque | Fuentes |
|---|---|
| Demografía, hogares, estructura | INEbase, tabla INE `68535`, `datos.comunidad.madrid`, IEstadis, DESVAN Almudena |
| Vivienda, precios, suelo | Catastro (estadísticas + SEC descarga), MIVAU, INE precios vivienda, Notariado, SIT Madrid, `datos.comunidad.madrid` |
| Transporte, movilidad | `datos.crtm.es` (GTFS), CRTM, Renfe datos abiertos, **OpenStreetMap**, Ministerio de Transportes |
| Educación, sanidad, servicios sociales | 5 datasets CKAN de `datos.comunidad.madrid` (establecimientos sanitarios, centros por tipo, servicios sociales, registro atención social, discapacidad en hogares) |
| Medioambiente, residuos, agua, riesgos | generación residuos domésticos, calidad del aire, SNCZI (MITECO), Canal de Isabel II, `datos.gob.es` |
| Economía, empleo, presupuestos | **CONPREL** (Hacienda, presupuestos municipales), INE productos y servicios |
| Cartografía y límites | `datos.gob.es`, **CNIG**, **IGN**, SIT Madrid |

Todas las APIs son públicas y documentadas:
- **INE JSON API**: `https://servicios.ine.es/wstempus/js/ES/{FUNCIÓN}/{ID}` (`DATOS_TABLA`, `VALORES_VARIABLE`); municipios: `VALORES_VARIABLE/19?clasif=121&det=2`; OpenAPI/Swagger en `ine.es/OpenAPI`.
- **CKAN Madrid**: `https://datos.comunidad.madrid/api/3/action/datastore_search` (+ `datastore_search_sql`) con `resource_id`.

---

## 4. Análisis crítico: los 8 riesgos que pueden hundir el proyecto

| # | Riesgo | Gravedad | Mitigación |
|---|---|---|---|
| **R1** | **n = 41 municipios.** Random Forest/XGBoost con panel de 41 unidades es un problema de ML tabular con muestra mínima. K-fold aleatorio sobre municipios ⇒ fuga espacial y temporal. | 🔴 Crítica | `GroupKFold` por municipio + split temporal (entrenar ≤t, validar >t) + **spatial K-fold** por comarca. Reportar banda de error honesta. |
| **R2** | **Fuga de leakage entre fases.** M4 usa demanda proyectada (M3) contra oferta (M1). Si M1 se entrena con precios que ya contienen la demanda futura implícita, M4 aprende a predecir con información no disponible en el momento de decisión. | 🔴 Crítica | Separación temporal estricta en *feature store*: cada fila etiquetada con `fecha_informacion_disponible`; pipeline de *point-in-time*. |
| **R3** | **M5 (recomendador) usa M2/M4, y M4 usa M2** ⇒ doble conteo de la misma señal en el score final. | 🟠 Alta | Declarar explícitamente la matriz de dependencias y aplicar correlación/decorrelación de pesos; documentar que el score es un índice compuesto, no una suma de performance. |
| **R4** | **Incertidumbre no cuantificada.** El documento exige "bandas de incertidumbre" pero XGBoost/RF no las dan. | 🟠 Alta | Predicción conformal (split/CP+), quantile regression, o NGBoost. Ver `arXiv:2312.06531` (conformal para AVM). |
| **R5** | **Hiperparámetros de no compensatoriedad ausentes.** La tesis central no se puede "aprender" con un único score. | 🔴 Crítica | Modelar cuellos de botella como restricciones explícitas: `min` sobre sub-índices, umbrales duros (1500 hab/médico, 95 % aulas), o modelo de *survival* al colapso. |
| **R6** | **GTFS y OSM son "vivos".** Los feeds cambian; un dataset sin snapshot es irreproducible. | 🟠 Alta | Versionar el dataset (DVC), congelar `feed_fecha` en cada fila, y marcar `valor_observado` vs `valor_estimado` en la propia tabla. |
| **R7** | **Datos faltantes en municipios pequeños.** El propio doc lo admite: "heterogeneidad en la dotación". Imputar un ratio sanitario con 1 médico crea ruido que domina el índice. | 🟠 Alta | Propagar incertidumbre en la imputación (N-folds); marcar imputaciones y *no* publicar el sub-índice si el % de valores no observados supera un umbral. |
| **R8** | **Trazabilidad de la explicación.** La app muestra SHAP, pero sin *provenance* de la fila (observado/imputado/proyectado/simulado) la explicación miente. | 🟡 Media | Columna de procedencia obligatoria por variable + versión de modelo + timestamp en cada predicción expuesta por la API. |
| **R9** | **Great Expectations no funciona en Oracle** (inyecta `FROM DUAL` → `ORA-00907`; issues #10948/#8618, sin arreglo previsto para Oracle). | 🟠 Alta | Usar **pandera + tests de `dbt-oracle`** como puertas de calidad. GX solo como extra, con `add_table` sobre vistas. |
| **R10** | **MLflow no tiene backend Oracle** (issue #15195 abierto: su DDL no es Oracle-clean). | 🟠 Alta | Tracking en Postgres y espejo del registro a Oracle, o probar `oracle+oracledb://` **el primer día**. |
| **R11** | **El runtime ONNX de Oracle solo existe en 23ai/26ai** y cubre 4 funciones (clasificación, regresión, clustering, embeddings). | 🟠 Alta | **Prueba UN modelo end-to-end en la semana 1**. Si la BD es 19c/21c, el fallback es FastAPI + REST Data Source. |
| **R12** | **Los valores SHAP solo son reproducibles si el conjunto de background está fijado** (`shap.Explainer(model, X_bg)`). | 🟠 Alta | Persistir `background_hash` + `model_version` con cada fila de explicación. |
| **R13** | **DVC no tiene remote nativo de OCI.** | 🟡 Media | API S3-compatible de OCI Object Storage (`dvc remote modify oci endpointurl https://<ns>.compat.objectstorage.<region>.oraclecloud.com`) o `rclone`. |
| **R14** | **Atribución obligatoria del IGN/CartoBase (CC BY 4.0)**: sin ella, la página "Fuentes Oficiales" es ilegal. | 🟡 Media | Tabla `fuente_oficial` con `organismo`, `url`, `licencia`, `atribucion` y renderizado en la APP. |

---

## 5. Arquitectura recomendada (Python → Oracle DB → APEX)

### 5.1 Principio rector
> **Python calcula, Oracle almacena y explica, APEX consume y narra. Ningún modelo se entrena dentro de APEX.**

### 5.2 Layout de repo recomendado

```
lodcore/
├── AGENTS.md                     # instrucciones para agentes de IA (ver 02-PROMPTS)
├── .github/prompts/*.prompt.md   # prompts Copilot/Codex/Claude (ver 03-PROMPTS)
├── pyproject.toml                # uv + ruff + mypy + pytest
├── dvc.yaml                      # pipeline: ingest -> features -> m1..m5 -> export
├── params.yaml                   # hiperparámetros por modelo (única fuente de verdad)
├── src/lodcore/
│   ├── ingest/                   # ine.py, ckan_madrid.py, catastro.py, gtfs.py, osm.py
│   ├── data/                     # validación (pandera), schemas, provenance
│   ├── features/                 # feature store + point-in-time joins
│   ├── models/
│   │   ├── m1_avm/               # RF + LGBM + conformal
│   │   ├── m2_indices/           # PCA + isócronas (osmnx + GTFS)
│   │   ├── m3_demography/        # SARIMAX/Prophet + bandas
│   │   ├── m4_hosting_capacity/  # XGBoost + SHAP + cuellos de botella
│   │   └── m5_recommender/       # KMeans/GMM + MCDM
│   ├── explain/                  # SHAP -> JSON para APEX, redacción en lenguaje natural
│   └── publish/                  # writer a Oracle (oracledb thin mode)
├── oracle/
│   ├── ddl/                      # tablas, índices, vistas
│   └── apex_export/              # export del workspace APEX
├── tests/
└── notebooks/                    # EDA, solo lectura
```

### 5.3 Contrato de datos hacia Oracle (esquema mínimo)

```sql
-- Provenance: TODA variable del dataset lleva esta taxonomía (requisito explícito del PDF)
CREATE TABLE lodcore.var_provenance (
  var_id            VARCHAR2(64),
  municipio_ine     CHAR(5),
  anio              NUMBER(4),
  valor             NUMBER,
  origen            VARCHAR2(20) CHECK (origen IN
                        ('OBSERVADO','IMPUTADO','ESTIMADO','PROYECTADO','SIMULADO')),
  metodo            VARCHAR2(200),   -- 'INE tabla 68535', 'RandomForest RF200', 'SARIMAX(1,1,1)x(1,1,1,12)', ...
  confianza_95_lo   NUMBER,
  confianza_95_hi   NUMBER,
  fuente_url        VARCHAR2(500),
  ingested_at       TIMESTAMP DEFAULT SYSTIMESTAMP,
  dataset_version   VARCHAR2(40)     -- tag DVC
);
```

### 5.4 Patrón de integración — arquitectura por **tres niveles** (recomendación en negrita)

**Hallazgo verificado** (documentación oficial Oracle 26ai, `onnx-support.html`):
Oracle AI Database importa modelos ONNX como **objetos `MINING_MODEL` de primera clase** y los puntúa
con los operadores OML (`PREDICTION`, `CLUSTER`, `VECTOR_EMBEDDING`). Por tanto **no hace falta un
microservicio Python en runtime para los 5 modelos**.

| Nivel | Qué corre dónde | Qué contiene | Por qué |
|---|---|---|---|
| **N1 · Entrenamiento (CI/CD, Python)** | Python + DVC + MLflow + pandera | Ingesta, features, entrenamiento de M1-M5, bandas conformal, SHAP, exportación ONNX | Es donde vive el rigor estadístico. **Nunca en runtime** |
| **N2 · Scoring de los 5 modelos (Oracle)** | Oracle AI Database 23ai/26ai | `model.onnx` importado como `MINING_MODEL` + vistas con `PREDICTION()` | Cero saltos HTTP; el modelo bajo el mismo perímetro de seguridad que los datos; **la página "Los 5 Modelos ML" se genera desde `USER_MINING_MODELS`** |
| **N3 · Lógica por usuario (FastAPI)** | Servicio Python mínimo | Solo **Quiz & Recomendador** (preferencias por usuario) y **Simulador What-If** (contrafactual + recálculo de SHAP) | Estas dos cosas no se pueden expresar en SQL sin perder legibilidad |

```
  N1  Python (train)            N2  Oracle AI Database            N3  FastAPI (2 endpoints)
  ┌────────────────────┐        ┌──────────────────────────┐     ┌──────────────────────┐
  │ DVC → pandera →   │  ONNX  │ MODELO_OML ×5 (MINING_    │     │ /recomendar         │
  │ sklearn/xgb/lgbm  │ ─────► │   MODEL) + PREDICTION()  │     │ /whatif              │
  │ SHAP → JSON        │  BLOB  │ SHAP_EXPLICACION        │     │ (preferencias +      │
  │ MLflow registry    │        │ V_MAPA / V_COMPARADOR…  │     │  contrafactual)      │
  └────────────────────┘        └──────────────────────────┘     └──────────┬───────────┘
                                     ▲                                     │
                                     └───────── APEX lee vistas ───────────┘
                                                  (REST Data Source solo para N3)
```

**Flujo de una predicción, de punta a punta**
```
Python entrena  →  skl2onnx/onnxmltools  →  model.onnx (bytes)
   →  oracledb: bind BLOB  →  DBMS_VECTOR.LOAD_ONNX_MODEL('ICA_MODEL', model_data => :blob)
   →  CREATE VIEW v_prediccion AS SELECT m.codigo_ine, PREDICTION(ICA_MODEL, m.*) AS ica FROM ...
   →  APEX lee v_prediccion
```
**Prueba de equivalencia obligatoria en CI**: error relativo < 1e-6 y absoluto < 1e-3 (ONNX
devuelve float32; a escala de ~2.000 €/m², un error absoluto < 1e-6 no es representable) antes de promover
ningún modelo. Los fallos típicos son dtypes (float64 vs float32) y operadores no soportados.

**Gráficas: usar lo nativo de APEX siempre que exista.**
- **Comparador → chart Radar nativo** (3 series = 3 municipios, 7 ejes = vuestras 7 capas). Sin JS.
- **Semáforo → chart "Status Meter Gauge" nativo.** Sin CSS a medida.
- **Ficha Municipal & SHAP → waterfall con ECharts** (`series: [{type:'waterfall'}]`), porque APEX no
  tiene waterfall. Alternativa sin JS: renderizar el SVG en Python y guardarlo como BLOB en Oracle.
- **Mapa → Map Region** con `SDO_GEOMETRY` (o GeoJSON si la capa viene de un REST Enabled SQL).

**"Fuentes Oficiales" puede ser un RAG real**: `DBMS_VECTOR.LOAD_ONNX_MODEL` con un modelo de
embeddings (MiniLM), columnas `VECTOR` + índice HNSW, y el patrón de `oracle/apex` →
`sample-apps/sample-vector-search/` (Vector Search en APEX con *Search Configurations*).

**Opción alternativa si la BD es 19c/21c** (sin ONNX in-database): el modelo vive en FastAPI y APEX
lo consume por **REST Data Source (Simple HTTP)**. Es la opción B de antes y funciona, pero pierde el
"todo dentro de Oracle" y obliga a operar el servicio.

### 5.5 Páginas APEX → fuente de datos (mapa de la capa de servicio)

| Página APEX | Query / fuente principal | Nota técnica |
|---|---|---|
| Mapa Territorial | `vw_mapa_ica` (GeoJSON + `semaforo` + `cuello_botella_dominante`) | Oracle Spatial / `oracle.geojson` (23ai) |
| Quiz & Recomendador | `fn_rank_municipios(perfil_json)` | "ranking de exclusión": exclusión dura de municipios que incumplen umbrales |
| Comparador | `vw_radar_municipios` | Radar chart (APEX Charts / Oracle JET) con 3 municipios |
| Ficha Municipal & SHAP | `vw_ficha_shap` | SHAP waterfall: filas = variables, valor = contribución |
| Cuadro de Mando | `vw_cuadro_mando` | Agregado por comarca y corona |
| Simulador What-If | `fn_simular_inversion(municipio, delta_inversion, escenario)` | Requiere el modelo cargado en runtime |
| Escenarios Crecimiento | `fn_escenario_crecimiento(delta_pct)` | Recalcula ratios: `hab/médico`, `ocupación_aulas` |
| Los 5 Modelos ML | `vw_modelos` (metadatos + métricas + versión) | Alimentado desde MLflow |
| Fuentes Oficiales | `vw_fuentes` | Se genera desde `var_provenance` |

---

## 6. Plan de trabajo sugerido (sprint por sprint)

**Sprint 0 — Cimientos (1 semana)**
1. `AGENTS.md` + `.github/prompts/` + `pyproject.toml` + `ruff`/`mypy`/`pytest` + DVC.
2. Esquema Oracle + tabla `var_provenance` + la vista `vw_fuentes`.
3. Ingesta mínima real: Padrón Municipal (INE) + Catastro + 1 dataset CKAN. Aunque sea con 10 municipios.
3b. **PRUEBA DE RIESGO TEMPRANO (el día 1)**: entrenar un `RandomForestRegressor` tonto, convertirlo
con `skl2onnx`, cargarlo con `DBMS_VECTOR.LOAD_ONNX_MODEL` y puntuarlo con `PREDICTION()`. Si esto no
funciona en vuestra BD, activad el fallback FastAPI **ahora**, no en la semana 4.

**Sprint 1 — Dataset y Feature Store (1,5 semanas)**
4. Ingesta completa de las 7 fuentes con `origen` explícito por celda.
5. Tabla `variables` + `municipios` + `panel_annual` (municipio × año × variable).
6. Validación con `pandera` + `ydata-profiling` + suite de Great Expectations.
7. Punto en el tiempo: toda fila lleva `fecha_disponible`.

**Sprint 2 — M1 (AVM) y M2 (Índices) (2 semanas)**
8. M1: RF/LGBM con CV espacial-temporal, bandas conformal, esfuerzo financiero.
9. M2: isócronas OSMnx + GTFS (CRTM), PCA → 4 sub-índices 0-100 con MinMax.

**Sprint 3 — M3 (Demografía) y M4 (ICA + SHAP) (2 semanas)**
10. M3: SARIMAX con exógenas, bandas al 80/95 %; Prophet como contraste.
11. M4: XGBoost con CV agrupada, SHAP, y **modelo de cuellos de botella no compensatorio**.
12. Publicación de resultados + SHAP JSON en Oracle.

**Sprint 4 — M5 (Recomendador) y APEX (2 semanas)**
13. M5: K-Means vs GMM (BIC/silhouette) + MCDM ponderado por perfil.
14. Simulador What-If + escenarios +5 %/+10 %.

**Sprint 5 — Endurecimiento (1 semana)**
15. Adversarial review de prompts de modelo (fuga, no-compensatoriedad, reproducibilidad).
16. Model cards, ficha metodológica, reproducible end-to-end (`dvc repro`).

---

## 7. Criterios de aceptación técnicos

| Nº | Criterio |
|---|---|
| CA-1 | `dvc repro` reconstruye el dataset y las predicciones desde cero con la misma versión de datos. |
| CA-2 | Toda variable expuesta por la API lleva `origen` ∈ {OBSERVADO, IMPUTADO, ESTIMADO, PROYECTADO, SIMULADO} y `metodo`. |
| CA-3 | Ningún modelo se evalúa con CV aleatorio sobre municipios; se usa split temporal + agrupado, y se reporta la banda. |
| CA-4 | Toda predicción expone intervalo de confianza al 95 %. |
| CA-5 | Cada ficha municipal incluye top-3 fortalezas y top-3 cuellos de botella con su valor SHAP y su regla de negocio en lenguaje natural. |
| CA-6 | El simulador What-If recalcula desde el modelo real, no desde una fórmula reimplementada. |
| CA-7 | La app APEX funciona con datos de las 41 fichas y con los umbrales del prototipo (1500 hab/médico, 95 % aulas, 30 min). |
| CA-8 | Cada modelo tiene su *model card* con métricas, supuestos, límites y fecha de entrenamiento. |
| CA-9 | Cada modelo publicado existe como `MINING_MODEL` en Oracle (o, si no hay ONNX in-DB, como endpoint documentado), y `score_ONNX == score_Python` con error relativo < 1e-6 y absoluto < 1e-3 (float32). |
| CA-10 | La página "Los 5 Modelos ML" se genera desde `USER_MINING_MODELS` / el espejo del registro de MLflow: no hay texto escrito a mano. |
| CA-11 | Toda cifra de la UI tiene `fuente_id`, `licencia` y `fecha_descarga` (atribución IGN incluida). |

---

*Documento generado a partir de la lectura de los PDF del datathon. Ver `02-INVENTARIO-GITHUB.md`
para el catálogo de recursos y `03-PROMPTS-OPERATIVOS.md` para los prompts listos para usar.*
