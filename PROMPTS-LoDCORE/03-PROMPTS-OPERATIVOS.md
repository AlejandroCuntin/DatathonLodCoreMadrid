# Catálogo de los 14 prompts operativos de LoDCORE

> Todos los prompts viven en `.github/prompts/*.prompt.md` (formato oficial de GitHub Copilot,
> con frontmatter YAML). Esta tabla es el índice: cuándo usar cada uno, con qué variables
> y qué produce.

---

## Resumen rápido

| # | Fichero | Tipo | Momento del proyecto | Entrada principal | Produce |
|---|---|---|---|---|---|
| 01 | `01-ingesta-fuente-oficial.prompt.md` | Datos | Sprint 0-1 | `${input:fuente}`, `${input:objetivo}` | Conector + datos con procedencia |
| 02 | `02-auditoria-calidad-y-procedencia.prompt.md` | Datos | Sprint 1 | `${input:dataset}` | Informe de calidad y veredicto |
| 03 | `03-auditoria-fuga-informacion.prompt.md` | ML | Sprint 2-3 | `${input:modelo}` | Informe de fuga + experimentos |
| 04 | `04-diseno-validacion-temporal-espacial.prompt.md` | ML | Sprint 2-3 | `${input:modelo}` | Protocolo + métricas con banda |
| 05 | `05-modelo-avm-random-forest.prompt.md` | Modelo M1 | Sprint 2 | `${input:modo}` | AVM + esfuerzo + bandas |
| 06 | `06-modelo-indices-pca-isocronas.prompt.md` | Modelo M2 | Sprint 2 | `${input:foco}` | Isócronas + 4 sub-índices 0-100 |
| 07 | `07-modelo-proyeccion-demografica.prompt.md` | Modelo M3 | Sprint 3 | `${input:horizonte}` | Población +5/+10 con bandas |
| 08 | `08-modelo-capacidad-acogida-xgboost-shap.prompt.md` | Modelo M4 | Sprint 3 | `${input:horizonte}` | ICA + SHAP + simulador |
| 09 | `09-cuellos-botilla-no-compensatorios.prompt.md` | Modelo M4b | Sprint 3 | `${input:servicio}` | No-compensatoriedad + test |
| 10 | `10-recomendador-clustering-mcdm.prompt.md` | Modelo M5 | Sprint 4 | `${input:perfil}` | Clusters + ranking + exclusiones |
| 11 | `11-explicacion-shap-lenguaje-natural.prompt.md` | Explicabilidad | Sprint 4 | `${input:municipio}` | Ficha municipal en español |
| 12 | `12-publicacion-oracle-y-apex.prompt.md` | Entrega | Sprint 4 | `${input:entorno}` | Tablas + vistas + export APEX |
| 13 | `13-model-cards-e-informe-tecnico.prompt.md` | Documentación | Sprint 5 | `${input:modelo}` | Model cards + informe + glosario |
| 14 | `14-revision-adversarial-pipeline.prompt.md` | Control de calidad | Sprint 5 | `${input:alcance}` | Revisión de 12 ataques |

---

## Detalle por prompt

### 01 · Ingesta de fuente oficial
**Para qué:** cualquiera de los ~30 datasets del PDF "Fuentes de datos" (INE, CKAN Madrid,
Catastro, GTFS, OSM, IGN/CNIG, CONPREL, Notariado, MIVAU, MITECO).
**Clave:** cada celda queda con `origen`, `metodo` y `fuente_url`. Snapshot cacheado e inmutable.
**Detalle crítico:** el municipio se identifica por **código INE de 5 dígitos**, nunca por nombre.
**Salida:** conector Python + esquema `pandera` + etapa DVC + bloque de resumen estandarizado.

### 02 · Auditoría de calidad y procedencia
**Para qué:** antes de entrenar nada. Distingue *no aplicable* de *falta de dato*; clasifica
outliers (error de captura / valor real / imputación defectuosa); recalcula de forma
independiente `hab/médico` y `% ocupación aulas`.
**Veredicto final:** APTO / APTO CON RESERVAS / NO APTO, y **qué modelos puede alimentar**.

### 03 · Auditoría de fuga de información
**Para qué:** el control más importante del proyecto. 7 tipos de fuga (L1-L7) + sesgo de
selección. Incluye el **test empírico**: reentrenar con y sin fuga y medir la diferencia.
**Salida:** tabla de disponibilidad (as-of date) por variable + tabla de experimentos + dictamen.

### 04 · Diseño de validación temporal y espacial
**Para qué:** n = 41 municipios exige tres niveles: expanding window temporal, `GroupKFold`
por municipio y spatial K-fold por comarca. Moran's I decide si el nivel C es obligatorio.
**Banda de 95 % por bootstrap de municipio** (las filas de un municipio no son independientes).
**Obligatorio:** 4 baselines naive. Un modelo que no gana a la persistencia no se publica.

### 05 · M1 — AVM con Random Forest / LightGBM
**Para qué:** precio €/m² (compra y alquiler) + esfuerzo financiero familiar.
**Decisión clave:** RF(200) como punto de partida, justificado con la literatura española
(Alicante, *Expert Systems with Applications* 2021: RF(200) alcanza error < 2 % con el menor
coste frente a 300/400/500 equivalentes).
**Banda:** predicción conformal, comparada con quantile regression, NGBoost y conformal
espacialmente ponderada (arXiv:2312.06531).
**Aviso en la ficha:** el alquiler no genera "esfuerzo financiero" sino **coste de oportunidad**.

### 06 · M2 — PCA e isócronas
**Para qué:** los 4 sub-índices 0-100 y las isócronas de 30 min (público vs privado).
**Decisiones:** punta + valle; máx. 1 transbordo; centroide **ponderado por población**.
**Trampa señalada:** PCA con n=41 produce componentes no interpretables → compara con
**AMPI (Mazziotta-Pareto)** del manual OECD/JRC 2008 y justifica la elección.
**Trampa señalada 2:** el signo de las componentes PCA es arbitrario → hay que **fijarlo y
persistirlo**, o la APP se rompe entre ejecuciones.

### 07 · M3 — Proyección demográfica
**Para qué:** población a 5 y 10 años con bandas.
**Decisión clave:** tabla de identificabilidad por longitud de serie (<12 años → no SARIMAX).
**Baseline real:** drift + ajuste regional, no ARIMA.
**Bandas con cobertura verificada** por backtesting: si la banda al 95 % cubre el 70 %, miente.
**Test de shock:** requisito explícito del PDF ("aprobación de un gran proyecto de vivienda").

### 08 · M4 — XGBoost + SHAP
**Para qué:** el ICA futuro, la simulación What-If y los cuellos de botella.
**Lo más importante:** el ICA **no es una variable observada**. Hay que **definirla con una
fórmula explícita** y compararla con la definición alternativa (delta del índice).
**Criterio de cuello de botella:** valor en el peor quintil **Y** contribución SHAP negativa
(un SHAP negativo con valor normal es ruido, no un cuello de botella).
**Advertencia obligatoria en la APP:** el modelo no conoce la estructura causal de la inversión;
las simulaciones fuera del rango observado se marcan como extrapolación no fiable.

### 09 · M4b — Cuellos de botella no compensatorios
**Para qué:** implementar la hipótesis fundacional, que XGBoost no puede cumplir solo.
**4 formulaciones comparadas** (min / media geométrica / **regla de veto** / penalización suave)
→ elige una y justifícala. La **regla de veto** es la más fiel: "un municipio en colapso queda
por debajo del umbral de Media, por mucho que acumule el resto".
**Test que hay que pasar:** un municipio con ICA base 85 y colapso sanitario debe quedar < 40,
y +50 % de zonas verdes **no** debe subirle el score.

### 10 · M5 — Recomendador
**Para qué:** tipologías territoriales (K-Means/GMM con BIC/silueta/estabilidad) + ranking MCDM.
**K-Means vs GMM:** tabla de 5 criterios × k=2..8 × bootstrap ARI.
**Nombrar los clusters verificablemente:** "pueblos rurales conectados" solo si los datos lo sostienen.
**Similitud del coseno vs SAW:** se implementan ambas (y TOPSIS, VIKOR, ELECTRE) y se explica
por qué difieren; el score final es una mezcla con α justificado.
**Ranking de exclusión:** los criterios duros **excluyen** y se muestran ("Excluidos 2 municipios
por colapso sanitario: …"); los blandos **ponderan**.

### 11 · Explicabilidad en lenguaje natural
**Para qué:** la Ficha Municipal & SHAP y el popup del mapa.
**8 reglas de redacción** (un claim = un número; siempre con umbral; nada de causalidad;
incertidumbre presente; sin jerga; sin alarmismo; sin lenguaje discriminante; ≤3 frases).
**Los 5 tests automáticos:** trazabilidad de números, umbrales, no-compensatoriedad,
no-causalidad, registro lingüístico.
**Caso límite crítico:** si la banda cruza un umbral, el texto dice **"indeterminado"** en vez
de afirmar TENSION o NORMAL.
**Dos registros** (ciudadanía / administraciones) generados desde la **misma plantilla**.

### 12 · Publicación en Oracle y capa APEX
**Para qué:** el puente Python → Oracle DB → APEX.
**Decisión clave:** patrón recomendado = Python escribe en Oracle (oracledb **thin mode**) y APEX
lee vistas. Alternativas documentadas: FastAPI + ORDS, y modelo nativo en Oracle (DBMS_ML / ONNX).
**DDL con `CHECK (origen IN (...))` en la base de datos**, no solo en Python.
**Todas las vistas de datos predictivos** incluyen `origen`, `metodo`, `dataset_version` y banda.

### 13 · Model cards e informe técnico
**Para qué:** la página "Los 5 Modelos ML" del prototipo y el informe para las administraciones.
**Sección obligatoria: "Límites y riesgos conocidos"** con ≥ 4 ítems, cada uno con un
**ejemplo concreto de municipio o dato** donde el modelo falla.
**Cross-check de números:** un script verifica que cada número del informe existe en los
artefactos y que informe, model card y APP coinciden.

### 14 · Revisión adversarial
**Para qué:** el control de calidad final, en contexto fresco.
**12 ataques concretos:** consistencia pipeline/publicado, tautología del ICA, no-compensatoriedad,
caducidad del GTFS, backtest honesto, municipios excluidos, escala relativa vs absoluta,
credibilidad del What-If, reproducibilidad real, correspondencia de municipios, trazabilidad de
la narrativa, y **cumplimiento de los claims del PDF de diseño** (tabla APTO/PARCIAL/NO CUMPLIDO).
**Incluye una sección de "puntos fuertes"**: una revisión solo negativa no genera confianza.

---

## Variables de entrada admitidas

| Prompt | Variables | Obligatorias |
|---|---|---|
| 01 | `fuente`, `objetivo`, `periodo` | `fuente`, `objetivo` |
| 02 | `dataset`, `variables` | `dataset` |
| 03 | `modelo` | `modelo` |
| 04 | `modelo`, `objetivo`, `anios_test` | `modelo`, `objetivo` |
| 05 | `modo` | — (por defecto `ambos`) |
| 06 | `foco` | — (por defecto `ambos`) |
| 07 | `horizonte` | — (por defecto `ambos`) |
| 08 | `horizonte` | — (por defecto `5`) |
| 09 | `servicio` | — (por defecto: todos) |
| 10 | `perfil` | — (por defecto: todos) |
| 11 | `municipio` | — (por defecto: peor ICA) |
| 12 | `entorno` | — (por defecto `dev`) |
| 13 | `modelo` | — (por defecto `todos`) |
| 14 | `alcance` | — (por defecto `completo`) |

---

## Cómo Adaptarlos a vuestro ritmo

El datathon tiene tiempo limitado. Si vais justos:

**Mínimo viable (2 sprints):** 01 → 02 → 04 → 05 → 08 → 09 → 12 → 14.
(Prioriza: AVM, ICA con no-compensatoriedad, publicación y revisión adversarial.)

**Si os sobra tiempo:** añade 03 (fuga), 06 (isócronas reales), 07 (bandas), 10 (clustering),
11 (narrativa fina), 13 (documentación).

**Si el jurado es técnico:** el prompt 03 y el 14 son los que más puntos dan: un evaluador que
re-entrena con `GroupKFold` y ve si tus números aguantan.

---

## Anexo · De dónde viene cada prompt (trazabilidad de las fuentes)

Cada prompt de `.github/prompts/` se construyó a partir de fuentes concretas, comprobadas en
GitHub durante la investigación. Esta tabla permite auditar de dónde sale cada decisión de diseño.

| Prompt LoDCORE | Fuente principal de la que deriva | Qué se toma de ella |
|---|---|---|
| 01 · Ingesta | `datania/ine-catalog` + CKAN API de Madrid + `remix/partridge` | IDs de tabla INE, patrón de cliente CKAN, snapshot inmutable con fecha |
| 02 · Calidad | `ai-boost/awesome-prompts → data_analysis.txt` (6 capas) + `fivetran/great_expectations` | Estructura OVERVIEW→RISKS, separación "no aplicable" vs. "falta de dato", validación como tests |
| 03 · Fuga | `ai-boost → diagnose.txt` (construir el feedback loop) + `verification_specialist.txt` | "El bucle de feedback es lo importante", exigencia de evidencia ejecutable, *spot-check* |
| 04 · Validación | `ai-boost → ml_systems_architect.txt` + `pysal/esda` (Moran's I) | Protocolo en 3 niveles, baselines obligatorios, banda de 95 %, justificación espacial |
| 05 · M1 AVM | Paper Alicante (ESWA 2021, RF(200)) + `scikit-learn-contrib/MAPIE` + `paezha/idealista18` | RF(200) como punto de partida, CQR/split conformal, dataset de validación en Madrid |
| 06 · M2 Índices | `carlos-mendez.org` PCA (6 pasos) + pooled PCA + `gboeing/osmnx` + `r5py` | Pipeline de índice, comparabilidad temporal, isócronas GTFS+OSM |
| 07 · M3 Demografía | `statsmodels` SARIMAX + `MKB-Datalab` SARIMAX/Prophet + `AidanCooper/forecasting` (MASE) | Diagnóstico ADF/KPSS, baseline seasonal-naïve, bandas con cobertura verificada |
| 08 · M4 ICA | `shap/shap` + `dmlc/xgboost` (`monotone_constraints`) + arXiv:2510.06912 | Target explícito, criterio de cuello de botella (quintil + signo SHAP), prompt de ML con dataset/métricas explícitos |
| 09 · No-compensatoriedad | Hipótesis del PDF de diseño + `monotone_constraints` de XGBoost | La tesis del proyecto convertida en **test ejecutable** |
| 10 · M5 Recomendador | `scikit-learn` (`plot_gmm_selection`, BIC/AIC) + `akestoridis/mcdm` + IEST *Tipología Municipal* | Selección de k con BIC/silueta/estabilidad, métodos MCDM comparados, precedente institucional |
| 11 · Narrativa | arXiv:2409.00079 (SHAP → lenguaje natural) + arXiv:2510.06912 | Prompt de conversión SHAP→texto, rigor de la fidelidad de la explicación |
| 12 · Oracle/APEX | `oracle/apex` + blogs Oracle (OML+APEX, REST-enabling OML) + `oracle/python-oracledb` | Patrón Python→Oracle→APEX, `oracledb` thin mode, Map region con `SDO_GEOMETRY` o GeoJSON |
| 13 · Model cards | `ai-boost → Technical_Documentation_Strategist.txt` + `SE-ML/awesome-seml` (Model Card Toolkit) | Secciones obligatorias de la model card, cross-check de números |
| 14 · Revisión adversarial | `ai-boost → verification_specialist.txt` + `doubt_driven_development.txt` | Sesgo hacia la disproof, 12 ataques concretos, sección de puntos fuertes |
