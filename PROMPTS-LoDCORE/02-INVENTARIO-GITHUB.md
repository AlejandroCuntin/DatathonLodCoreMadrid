# 02 · Inventario de la investigación: GitHub, librerías, papers y fuentes

> Resultado de una búsqueda exhaustiva en Google + GitHub (API `api.github.com/search/repositories`
> y `repos/*/contents`, más lectura directa vía `raw.githubusercontent.com`).
> Las estrellas (★) están **verificadas** contra la API o la página del repo.
> El objetivo de este inventario no es "listar repos Famous" sino responder, para cada recurso,
> **qué aporta exactamente y a qué parte de LoDCORE sirve**.

---

## 0. TL;DR — los 15 recursos que más impacto tienen en LoDCORE

| # | Recurso | ★ | Para qué sirve en LoDCORE |
|---|---|---|---|
| 1 | **IEST — Tipología Municipal de la Comunidad de Madrid** | — | **Precedente institucional exacto**: PCA → cluster → indicadores sintéticos. El argumento "la región ya lo hace así" |
| 2 | **r5py/r5py** | 194 | Fusión GTFS+OSM en un router multimodal → isócronas de 30 min **reales**, con transbordos |
| 3 | **gboeing/osmnx** | 5.882 | Brazo privado (coche) y a pie; `ox.routing.isochrone()`; settings para OSM **histórico** |
| 4 | **carlos-mendez.org PCA tutorials** | — | Tu pipeline M2 en 6 pasos, más **PCA pooled** para que los años sean comparables |
| 5 | **scikit-learn-contrib/MAPIE** | 1.607 | Bandas de predicción conformal (CQR, split, CV+) — el requisito de incertidumbre |
| 6 | **shap/shap** | 25.825 | `TreeExplainer` exacto para XGBoost; beeswarm, waterfall, valores por municipio |
| 7 | **dmlc/xgboost** | 28.901 | Modelo M4, `monotone_constraints` para la no-compensatoriedad |
| 8 | **paezha/idealista18** | 59 | Microdatos de vivienda de **Madrid** (94.815 anuncios) **enriquecidos con el Catastro** |
| 9 | **fivetran/great_expectations** | 11.890 | Validación del dataset y la distinción observado/imputado/proyectado |
| 10 | **oracle/apex** | 661 | Apps de ejemplo por versión; el Map region acepta `SDO_GEOMETRY` o GeoJSON |
| 11 | **pysal/esda** | 261 | Moran's I y LISA para justificar el spatial K-fold y validar la tipología |
| 12 | **inigoflores/ds-municipios-catastro-es** | 4 | Códigos INE ↔ MHAP de los municipios (clave para cruzar Catastro con el padrón) |
| 13 | **datania/ine-catalog** | 5 | Referencia completa de la API JSON del INE, clonada y versionable |
| 14 | **ai-boost/awesome-prompts** | 9.115 | 361 prompts de rol listos (MLOps, Data Governance, ML Architect, diagnosis) |
| 15 | **github/awesome-copilot** | 40.310 | El estándar de formato `.prompt.md` + instrucciones + agentes |

---

## 1. Prompts, bibliotecas de prompting e instrucciones para agentes

### 1.1 Colecciones de prompts (adopción directa)

| Recurso | ★ | Licencia | Por qué sirve | Cómo usarlo |
|---|---|---|---|---|
| **[github/awesome-copilot](https://github.com/github/awesome-copilot)** | 40.310 | MIT | **El estándar de facto** de prompts e instrucciones para agentes: carpeta `prompts/`, `instructions/`, `agents/`, `chatmodes/`, `skills/`, `workflows/`. | Copiar ficheros `.prompt.md` a `.github/prompts/` de tu repo. Contienen el `prompt.instructions.md` que define el formato (frontmatter + Mission/Scope/Inputs/Workflow/Output/QA) |
| **[ai-boost/awesome-prompts](https://github.com/ai-boost/awesome-prompts)** | 9.115 | GPL-3.0 | **361 prompts de rol** en `.txt` con estructura Rol → Contexto → Proceso → Output → Quality standards. Relevantes: `ml_systems_architect.txt`, `MLOps_Engineer.txt`, `analytics_engineer.txt`, `data_analyst.txt`, `data_analysis.txt`, `Data_Governance_Architect.txt`, `Data_Platform_Architect.txt`, `diagnose.txt`, `verification_specialist.txt`, `doubt_driven_development.txt`, `agents_md_author.txt`, `sql_assistant.txt`, `test_strategy_architect.txt`, `code_reviewer_security.txt`, `Technical_Documentation_Strategist.txt`, `academic_paper_architect.txt` | **Adaptar 6-8 de estos al dominio LoDCORE** (ver `03-PROMPTS-OPERATIVOS.md`). El `doubt_driven_development` es el que inspiration el prompt 14 |
| **[dair-ai/Prompt-Engineering-Guide](https://github.com/dair-ai/Prompt-Engineering-Guide)** | 79.436 | MIT | Guía canónica: patrones (COSTAR, RTF, CRISPE), técnicas, notebooks. | Referencia de método; de aquí salen los frameworks embebidos en los prompts |
| **[f/prompts.chat](https://github.com/f/awesome-chatgpt-prompts)** (antes `f/awesome-chatgpt-prompts`) | 173.955 | CC0-1.0 | Mayor biblioteca abierta de prompts. | Buscar por tarea; descartar los genéricos de "productivity" |
| **[promptslab/Awesome-Prompt-Engineering](https://github.com/promptslab/Awesome-Prompt-Engineering)** | 6.388 | Apache-2.0 | Papers y herramientas: ChainForge, LMQL, OpenPrompt, promptsource, `betterprompt`. | Para evaluación y versionado de prompts |
| **[NirDiamant/Prompt_Engineering](https://github.com/NirDiamant/Prompt_Engineering)** | 7.914 | MIT | 22 notebooks Jupyter sobre prompting. | Formación rápida del equipo |
| **[jasontang-ai/Context-Engineering](https://github.com/davidkimai/Context-Engineering)** (repo movido) | 9.259 | MIT | Manual de *context design* (más allá del prompt). | Útil para decidir qué meter en `AGENTS.md` y qué no |
| **[markoniga/llm-prompts-for-dse](https://github.com/markoniga/llm-prompts-for-dse)** | 1 | n/a | **Cadena de prompts de data workflow servida por MCP**: `interpret_intent → context_gap → generate_code → validate_risk → run → test_results → reconcile → create_pr → merge_guard`. El patrón `context_gap` (declarar qué falta y parar) es directamente aplicable a la ingesta de datos | Adoptar el **patrón**, no el repo |
| **[andre-simplifica/oracle-apex-ai-skills](https://github.com/andre-simplifica/oracle-apex-ai-skills)** | 20 | MIT | **Skills de IA para Oracle APEX 24.2+**: `oracle-apex-dev` (SQL/PL-SQL/REST/jobs/seguridad), `oracle-apex-object-lock` (locks cooperativos), `oracle-apex-export` (exports y snapshots). Trae `AGENTS.md` | **Altamente relevante**: vuestro frontend es APEX. Instalar en el repo del frontend |
| **[agentsmd/agents.md](https://github.com/agentsmd/agents.md)** | — | — | Estándar abierto (`AGENTS.md`), admitido por Codex, Cursor, Aider, Jules, Gemini CLI, Factory, RooCode y Claude Code vía `CLAUDE.md` | Escribir un `AGENTS.md` canónico y, si hace falta, un `CLAUDE.md` fino que lo referencie |
| **[davidkimai/…]** → ver tabla anterior | | | | |

### 1.2 Prompt files e instrucciones concretas (ficheros sueltos de alto valor)

| Fichero | Qué aporta |
|---|---|
| `awesome-copilot/instructions/prompt.instructions.md` | **El estándar de autoría** de `.prompt.md`: campos de frontmatter requeridos, nomenclatura kebab-case, estructura del cuerpo, uso de `${input:x}`, mínimo privilegio en `tools`, y checklist de QA. **Es la plantilla que siguen los 14 prompts de este proyecto** |
| `ai-boost/awesome-prompts/prompts/data_analysis.txt` | Framework de 6 capas (OVERVIEW → PATTERNS → ANOMALIES → DRIVERS → OPPORTUNITIES → RISKS) con estructura de salida fija y estándares de calidad ("ground every claim in specific data points") |
| `ai-boost/awesome-prompts/prompts/ml_systems_architect.txt` | Proceso de 5 fases (definición → pipeline → entrenamiento → serving → monitoring) con preguntas concretas por fase. Base del prompt 08 |
| `ai-boost/awesome-prompts/prompts/Data_Governance_Architect.txt` | Data quality, data catalog, **lineage**, AI/ML data standards (provenance, bias testing). Base del prompt 02 y del requisito de procedencia |
| `ai-boost/awesome-prompts/prompts/diagnose.txt` | "Construye primero el feedback loop" + 10 tipos de bucle de detección. Base del prompt 03 |
| `ai-boost/awesome-prompts/prompts/verification_specialist.txt` | "No confirmes que funciona: intenta romperlo", con advertencia de *spot-check* (el evaluador puede re-ejecutar tus comandos). Base del prompt 14 |
| `ai-boost/awesome-prompts/prompts/doubt_driven_development.txt` | Ciclo CLAIM → EXTRACT → DOUBT → RECONCILE → STOP. Base del prompt 14 |
| `ai-boost/awesome-prompts/prompts/agents_md_author.txt` | Reglas para escribir `AGENTS.md`: qué incluir, qué excluir, cómo no duplicar el README |
| `ai-boost/awesome-prompts/prompts/sql_assistant.txt`, `database_schema_designer.txt` | Support para el DDL Oracle y las vistas |

### 1.3 Frameworks con respaldo científico (citables en la memoria del proyecto)

| Framework | Origen | Uso en este proyecto |
|---|---|---|
| **COSTAR** (Contexto, Objetivo, Estilo, Tono, Audience, Response) | — | Estructura base de todos los prompts |
| **RTF** (Role, Task, Format) | — | Rol + tarea + formato literal de salida |
| **CRISPE** (Capacity, Role, Insight, Statement, Personality, Experiment) | — | Bloque *Capacidad* (algoritmos permitidos) + *Statement* (restricciones de dominio: n=41, umbrales) |
| **"A Prompt Pattern Catalog to Enhance Prompt Engineering with ChatGPT"** | arXiv:2302.11382 | Catálogo de patrones reutilizables |
| **"Teach me how to prompt"** | arXiv:2304.09810 | Taxonomía de patrones |
| **Progressive Prompts / Synthetic Prompting** | arXiv:2301.12314 / 2302.00618 | Few-shot sintéticos paraGuy el proyecto |
| **"Utilizing Large Language Models for Machine Learning Explainability"** | arXiv:2510.06912 | **Demuestra que un prompt de ML bien estructurado (dataset format + features + targets + modelos + métricas) genera pipelines con **fidelidad SHAP** comparable a los baselines baselines**. Es la referencia para el prompt 08 |
| **"Enhancing the Interpretability of SHAP Values Using LLMs"** | arXiv:2409.00079 | Prompt que convierte valores SHAP en texto natural: *"explain the importance of the following features in determining the model's prediction"* + lista de features y valores. Base del prompt 11 |

### 1.4 Librerías de prompting en Python (si queréis automatizar)

| Librería | Para qué |
|---|---|
| **`instructor`** | Salida estructurada validada con Pydantic → **el prompt 01 (ingesta) debería devolver JSON validado** |
| **`Outlines`** / **`guidance`** | Generación con gramática restringida (JSON Schema) |
| **`prompthub`** / **`langchain` prompt templates** | Versionado de templates |
| **`promptfoo`** | **Evaluación de prompts** en CI: define casos, compara prompts, mide coste y latencia. Es la opción con mejor relación esfuerzo/valor para un equipo de DS sin producto LLM |
| **`deepeval`** / **`openevals`** / **`betterprompt`** | Alternativas de evaluación |

---

## 2. Datos oficiales y su acceso programático

### 2.1 INE (padrón, precios, renta)

| Recurso | ★ | Detalle |
|---|---|---|
| **[datania/ine-catalog](https://github.com/datania/ine-catalog)** | 5 | Clon con la **referencia completa de la API JSON del INE** (`docs/Referencia de la API.md`, 853 líneas) y los códigos de tablas. Perfecto para tener la referencia **versionada en el repo** |
| **[dani537/extractor_ine](https://github.com/dani537/extractor_ine)** | — | Extractor de series del INE vía API, con `ine_codes.xlsx` como entrada. Patrón simple y reutilizable |
| API JSON del INE | — | `https://servicios.ine.es/wstempus/js/ES/{FUNCIÓN}/{ID}` — funciones `DATOS_TABLA`, `VALORES_VARIABLE`. **Municipios**: `VALORES_VARIABLE/19?clasif=121&det=2` (paginación de 500). OpenAPI/Swagger en `ine.es/OpenAPI` |
| Tablas | — | Padrón municipal: `ine.es/jaxiT3/Tabla.htm?t=68535`; códigos INE de municipios: `ine.es/dyngs/INEbase/es/operacion.htm?c=Estadistica_C&cid=1254734710990` (XSL) |

### 2.2 CKAN Comunidad de Madrid

| Recurso | Detalle |
|---|---|
| **[api-evangelist/datos-comunidad-madrid](https://github.com/api-evangelist/datos-comunidad-madrid)** | Notas de cliente CKAN para el portal Function **(~2.282 datasets)** |
| **[api-evangelist/datos-madrid-es](https://github.com/api-evangelist/datos-madrid-es)** | Ídem para el portal municipal (~667 datasets) |
| API CKAN | `https://datos.comunidad.madrid/api/3/action/datastore_search?resource_id={rid}` y `datastore_search_sql`. `package_search` para buscar datasets |

### 2.3 Códigos municipales y cartografía

| Recurso | ★ | Detalle |
|---|---|---|
| **[inigoflores/ds-municipios-catastro-es](https://github.com/inigoflores/ds-municipios-catastro-es)** | 4 | **Códigos INE + MHAP del Catastro** por municipio. Indispensable para cruzar Catastro con el padrón sin ambigüedad |
| **[regi-es/ds-codigos-postales-ine-es](https://github.com/regi-es/ds-codigos-postales-ine-es)** | 2 | Códigos postales ↔ municipios desde datos abiertos del INE, con actualización automática por GitHub Actions |
| **[rOpenSpain/mapSpain](https://github.com/rOpenSpain/mapSpain)** | 50 | `esp_get_munic_siane()`, `esp_get_comarca()` con **cuatro clasificaciones oficiales** (INE/IGN/AGR/LIV), y `pobmun25` (padrón INE 2025). La rama `sianedata` lleva los shapefiles crudos legibles por geopandas |
| IGN / CNIG | — | `centrodedescargas.cnig.es/CentroDescargas/cartobase-ane` (municipios y comarcas, CC BY 4.0); `ign.es/web/ign/portal/datos-abiertos` |
| **[api-evangelist/oracle-apex](https://github.com/api-evangelist/oracle-apex)** | — | `apis.yml` con el catálogo de APIs de APEX/ORDS y patrones de integración |

### 2.4 GTFS de CRTM — y el problema de su antigüedad

| Feed | Dataset | **Datos actualizados** |
|---|---|---|
| Autobuses Urbanos | `datos.crtm.es/datasets/357e63c2904f43aeb5d8a267a64346d8` | **2025-07-02** |
| Autobuses Interurbanos | `datos.crtm.es/datasets/885399f83408473c8d815e40c5e702b7` | **2025-07-02** |
| Metro | `datos.crtm.es/datasets/5c7f2951962540d69ffe8f640d94c246` | **2025-05-30** |
| Cercanías | `datos.crtm.es/datasets/1a25440bf66f499bae2657ec7fb40144` | **2024-08-27** |
| EMT | `datos.crtm.es/datasets/868df0e58fca47e79b942902dffd7da0` | **2023-04-28** ⚠️ |

> **Hallazgo crítico**: tu "municipio de 30 minutos" es una **foto de accesibilidad 2023-2025**, no en vivo.
> **Decisión obligatoria**: (a) restringirse a Urbanos + Interurbanos + Metro + Cercanías, excluyendo EMT;
> (b) poner una etiqueta visible en la UI con la fecha del feed (*"datos de transporte a 2025-07-02"*);
> (c) archivar el SHA-256 de cada feed con cada ejecución del modelo.

| Recurso | ★ | Detalle |
|---|---|---|
| **[remix/partridge](https://github.com/remix/partridge)** | 185 | `ptg.load_feed(path, view)` → DataFrames; `ptg.read_busiest_date(path)`; poda el feed por grafo de dependencias desde `trips.txt`. **Sin mantenimiento desde dic-2023** |
| **[araichev/gtfs_kit](https://github.com/araichev/gtfs_kit)** | 123 | Toolkit GTFS en memoria con pandas/GeoPandas. **Repo archivado** → ahora en Codeberg y PyPI (`gtfs-kit` 10.1.1). La v10 quitó su propio validador |
| **[MobilityData/gtfs-validator](https://github.com/MobilityData/gtfs-validator)** | 433 | **El validador canónico** de GTFS Schedule. Docker + CLI + UI web. Úsalo como **gate en CI** antes de ingerir |
| **[ChelseaKR/gtfs-scorecard](https://github.com/ChelseaKR/gtfs-scorecard)** | — | Scorecards diarios de calidad del GTFS (Correctness / Freshness / Rider experience) con GitHub Action. **El gate de frescura que necesitas** |
| **[google/transitfeed](https://github.com/google/transitfeed)** | 685 | ⚠️ **Archivado**. Solo si hay que *escribir* un feed |
| **[MobilityData/awesome-transit](https://github.com/MobilityData/awesome-transit)** | ~1.800 | Índice maestro de librerías, validadores, converters y motores de routing GTFS. **El mejor punto de entrada para no volver a buscar** |

---

## 3. Isócronas, accesibilidad y grafos (Modelo 2)

| Recurso | ★ | API concreta | Notas / trampas |
|---|---|---|---|
| **[r5py/r5py](https://github.com/r5py/r5py)** | 194 | `r5py.TransportNetwork(osm_pbf, [gtfs])`; `r5py.Isochrones(net, origins, departure=datetime(...), transport_modes=[TRANSIT, WALK], isochrones=[15,30])` → GeoDataFrame `MULTILINESTRING` + `travel_time`; `TravelTimeMatrix`; `snap_to_network(points, radius=1600, street_mode=WALK)` | **La mejor opción para tu criterio de 30 min**: fusiona GTFS+OSM, maneja transbordos. Necesita el motor R5 (Java) y un **`.osm.pbf` de Geofabrik España**. Las isócronas se calculan sobre una **rejilla de puntos** (`point_grid_resolution`, 100 m por defecto): precisión vs. velocidad. `departure_time_window` debe superar el headway típico |
| **[gboeing/osmnx](https://github.com/gboeing/osmnx)** | 5.882 | `ox.graph_from_polygon(poly, network_type='drive')`; `ox.routing.add_edge_speeds(G)`; `ox.routing.add_edge_travel_times(G)`; **`ox.routing.isochrone(G, node, cutoffs=[1800], weight='travel_time')`**; `ox.io.save_graph_geopackage` | API movida en v2 (`ox.routing.*`, `ox.distance.*`). Settings clave: `settings.use_cache=True`, `settings.cache_folder` (fíjalo para reproducibilidad), `settings.overpass_rate_limit=True`, `settings.requests_timeout=180`, `settings.max_query_area_size=2.5e9`, `settings.bidirectional_network_types=["walk"]`, y **`settings.overpass_settings` con `[date:"…"]` para snapshots OSM históricos**. PyPI 2.0.7 (2025-11-26) |
| **[gboeing/osmnx-examples](https://github.com/gboeing/osmnx-examples)** | 1.899 | `notebooks/13-isolines-isochrones.ipynb` — **el tutorial canónico de isócronas con OSMnx**. Corrible en Colab | Copiar la receta |
| **[opentripplanner/OpenTripPlanner](https://github.com/opentripplanner/OpenTripPlanner)** | 2.765 | `/otp/routers/{id}/isochrone?fromPlace=…&cutoffSec=1800&cutoffSec=3600` → **GeoJSON multipolygons**; OTP2 expone **GraphQL API**. RAPTOR | Necesita JVM + OSM PBF + GTFS. `mvn clean package`. Alternativa a r5py si quieres el endpoint HTTP |
| **[GIScience/openrouteservice-py](https://github.com/GIScience/openrouteservice-py)** | — | `client.isochrones(locations, profile="driving-car", range_type="time", range=[1800], location_type="destination")` | Requiere API key y tiene rate limits: mal para repetir en un datathon |
| **[ustroetz/python-osrm](https://github.com/ustroetz/python-osrm)** | 147 | `osrm.table(coords, ids_origin=[...])`; `osrm.AccessIsochrone((lon,lat), points_grid=450)` + `.render_contour(n_class=8)` | **Servidor local, sin API key** → la opción reproducible para el brazo privado. `pip install osrm-bindings` da OSRM en proceso |
| **[graphfinder/graphfinder](https://github.com/graphfinder/graphfinder.github.io)** | — | A*/Dijkstra instrumentados con heurística **haversine** sobre grafos OSMnx: `osm.route(G, (lat,lon), (lat,lon))`; reporta nodos expandidos | **Coincide exactamente con tu especificación "Dijkstra / A* sobre OpenStreetMap"**. La heurística es admisible (metros vs. metros) → A* sigue siendo óptimo |
| **[connor-makowski/scgraph](https://github.com/connor-makowski/scgraph)** | 52 | `get_shortest_path(origin, destination, algorithm_fn='a_star', algorithm_kwargs={"heuristic_fn": geograph.haversine})`; contraction hierarchies | Requiere compilar/cargar un `.graph` binario |
| **[ai4up/gtfs2nx](https://github.com/ai4up/gtfs2nx)** | — | `gx.transit_graph('feed.zip', time_window=('06:00','08:00'), route_types=[700], walk_transfer_max_distance=400)` → grafo NetworkX con **tiempo de transbordo realista = caminata + headway/2** | El transbordo por caminata en línea recta es una heurística, no un camino routado |
| **[kuanb/peartree](https://github.com/kuanb/peartree)** | 207 | `pt.get_representative_feed(path)`; `pt.load_feed_as_graph(feed, start, end)` → multigrafo dirigido NetworkX | Redes de **un solo día representativo**: sirve para centralidad/estructura, **no** para el test de 30 min |
| **[transnetlab/transit-routing](https://github.com/transnetlab/transit-routing)** | 94 | Time-Expanded Dijkstra, **RAPTOR, rRAPTOR, HypRAPTOR**, Transfer Patterns, **CSA** (bicriterio tiempo × transbordos) | Código de investigación. Si quieres penalizar transbordos en el criterio de 30 min, aquí está el algoritmo |
| **[Esri/public-transit-tools](https://github.com/Esri/public-transit-tools)** | 197 | "Calculate Accessibility Matrix", "Create Percent Access Polygons", "Calculate Travel Time Statistics" | Es ArcGIS Pro, no Python puro. **Léelo por la metodología** y reimplementa: es exactamente el "% de población accesible en X minutos" |
| **[ChelseaKR/gtfs-scorecard](https://github.com/ChelseaKR/gtfs-scorecard)** | — | Gate de frescura | Ver tabla GTFS |
| **[dhaneswaramandrasa/transit-access](https://github.com/dhaneswaramandrasa/transit-access)** | 0 | `download_gtfs.py → download_osm.py → validate_gtfs.py → prepare_network.py (r5py TransportNetwork) → compute_isochrones.py` → parquet, y **clasificación en 4 cuadrantes** (Transit Desert / Transit Ideal / Car Suburb / Over-Served) | **La plantilla de pipeline más cercana a LoDCORE**. Su layout (`src/ingestion → src/processing → src/analysis`, `data/raw → data/processed`) es directamente liftable |
| **[TransformTransport/accessX](https://github.com/TransformTransport/accessX)** | 28 | Accesibilidad tipo "X-minutos-ciudad" sobre GeoPandas/OSMnx/NetworkX/H3; `compute_co_accessibility` | Nuevo (2026), base de usuarios pequeña |
| **[EL-BID/urbanpy](https://github.com/EL-BID/urbanpy)** | 131 | `urbanpy.routing.compute_osrm_dist_matrix`, `isochrone_from_graph`, `start_osrm_server`; `urbanpy.accessibility.travel_times`, `pressure_map` | ⚠️ **GPL-3.0** (copyleft): revisa la licencia antes de embeberlo en un proyecto UPL/Apache |

---

## 4. Índices compuestos, PCA y tipologías territoriales (Modelos 2 y 5)

| Recurso | ★ | Detalle | Trampa metodológica que resuelve |
|---|---|---|---|
| **IEST — Tipología Municipal de la Comunidad de Madrid** | — | *"se ha estudiado el comportamiento de una serie de indicadores parciales, obteniéndose los **factores principales para evitar redundancias y rebajar la dimensión** de los datos, para finalmente establecer una **tipología a través de un análisis de conglomerados (cluster)**. Por último, aprovechando la información derivada del **análisis de factores principales, se han obtenido unos indicadores sintéticos**"* (ediciones 2000, 2006) | **Precedente institucional exacto**: PCA → cluster → indicadores sintéticos. **Cítalo en la memoria**: "la región ya usa esta metodología" |
| **[Mazziotta & Pareto (2024), "PCA for constructing socio-economic composite indicators"](https://link.springer.com/article/10.1007/s43545-024-00920-x)** | — | Paper | **La lectura obligatoria para M2**: un índice PCA exige un *modelo de medición* explícito; en un modelo **formativo** (tus indicadores *causan* "capacidad") PCA puede fallar. Defendible: usar PC1..PC4 como **cuatro sub-índices separados** (que es lo que ya haces) en vez de un score único |
| **[OECD/JRC Handbook on Constructing Composite Indicators (2008)](https://www.oecd.org/content/dam/oecd/en/publications/reports/2005/08/handbook-on-constructing-composite-indicators_g17a16e3/533411815016.pdf)** | — | Workflow de 10 pasos: marco teórico → selección → **imputación → normalización → ponderación (PCA) → agregación → robustez (análisis de sensibilidad e incertidumbre)** | **Min-Max NO es invariante a cambios de escala**: hay que hacer análisis de sensibilidad. Es lo primero que preguntará unjurado técnico |
| **[carlos-mendez.org — PCA for Development Indicators](https://carlos-mendez.org/tutorials/python_pca/)** | — | Tu pipeline M2 en **6 pasos explícitos**: (1) ajuste de polaridad → (2) z-score → (3) matriz de covarianza → (4) autodescomposición → (5) score PC1 → (6) **Min-Max a 0-1**. Código en `cmg777/starter-academic-v501` (`content/post/python_pca/script.py`) | **La implementación más cercana publicada a tu M2** |
| **[carlos-mendez.org — Pooled PCA Across Time](https://carlos-mendez.org/tutorials/python_pca2/)** | — | **PCA por periodo NO es comparable entre años** (cada año reinicia min/max y carga sus eigenvectors). Solución: medias/DE pooled, eigenvectors pooled, bounds pooled. Validado: R²=0,9823 (pooled) vs 0,9750 (per-period) | **Crítico para M3**: sin PCA pooled, los sub-índices de años distintos no son comparables y el trend es arte |
| **[JRC — Tools for Composite Indicators Building (2005)](https://publications.jrc.ec.europa.eu/repository/bitstream/JRC31473/EUR%2021682%20EN.pdf)** | — | La caja de herramientas original: normalización, ponderación, agregación, pruebas de sensibilidad | Referencia canónica |
| **[bluefoxr/COINr](https://github.com/bluefoxr/COINr)** | 31 | R. Entorno completo de indicadores compuestos: normalización, imputación, ponderación (PCA / manual / correlation-optimised), agregación, **análisis global de sensibilidad**, "what-if" | **Anexo obligatorio de robustez** (R, pero la metodología es portable) |
| **[GianmarcoBorrata/Indicator](https://github.com/GianmarcoBorrata/Indicator)** | 1 | R (CRAN). `pca_weighting()` ("performs a PCA on the input data to calculate weights that correct for overlapping information between related indicators"), `min_max()`, MPI / AMPI, imputación | Receta exacta OECD/JRC + Mazziotta-Pareto |
| **[olgnaydn/compindexR](https://github.com/olgnaydn/compindexR)** | — | `calc_compindex(x, avg_type="simple", scaling_method="min-max", vif_based_calc=TRUE)` → **podado de variables por VIF** + índice de sensibilidad de primer orden | Resuelve tu problema de "decenas de variables correlacionadas" |
| **[MohammadGholami-MG/Composite-KPI](https://github.com/MohammadGholami-MG/Composite-KPI)** | 0 | Python: `src/pca_weights.py`, `src/critic.py`, `src/entropy.py`, `src/Normalization.py` | Comparación de ponderaciones PCA vs Entropía vs CRITIC, código reutilizable |
| **[ESRI blog — PCA to determine weights for index indicators](https://www.esri.com/arcgis-blog/products/api-python/analytics/performing-principal-component-analysis-pca-to-determine-weights-for-index-indicators)** | — | Receta Python compacta: `StandardScaler` → `PCA` → `explained_variance_ratio_` → **loadings normalizados a 1** → media ponderada | Ojo: usa `StandardScaler`; tú usas `MinMaxScaler`. Elige uno y justifícalo |
| **[CityScope/CS_Urban_Indicators](https://github.com/CityScope/CS_Urban_Indicators)** | 8 | `CompositeIndicator(np.mean, selected_indicators=[...])`, registro de indicadores enchufable | Arquitectura de agregación (⚠️ GPL-3.0) |
| **[EducationalTestingService/factor_analyzer](https://github.com/EducationalTestingService/factor_analyzer)** | — | `FactorAnalyzer(n_factors=4, rotation="varimax")`, CFA | Cross-check de tus 4 bloques vs. los ejes PCA. ⚠️ **EFA con n=41 es inestable** |
| **[MAPA — Índice Sintético de Desarrollo Territorial de Aragón (ISDT)](https://www.aragon.es/-/indice-sintetico-desarrollo-territorial)** | — | **Precedente español administrativo de índice sintético municipal**: normalización por media/DE, ponderaciones explícitas (variables demográficas = 2; equipamientos y servicios; movilidad), publicado por Orden VMV/1789/2021 | **Metodología oficial española** de un índice territorial municipal. Excelente para citar en la memoria |
| **[MAPA — *Atlas de la España Rural* (2004)](https://www.ign.es/web/catalogo-cartoteca/resources/pdfcards/card027357.pdf)** + **[AgrInfo nº 31 (2021)](https://www.mapa.gob.es/dam/mapa/contenido/ministerio/servicios/servicios-de-informacion/analisis-y-prospectiva/ayp-serie-agrinfo/ayp_demografiaenlapoblacionrural2020.pdf)** | — | Definición legal de "municipio rural" (**Ley 45/2007**: <30.000 hab. **y** <100 hab/km²); 6.671 municipios rurales; clasificación Degurba | **Benchmark natural** contra vuestro umbral de <50.000 hab. |
| **[JARVISLee511/cityscore-livability-index](https://github.com/JarvisLee511/cityscore-livability-index)** | 0 | Índice de vulnerabilidad económica a nivel **municipal** con **tests de sensibilidad y robustez** sobre las decisiones de construcción | El análogo más cercano a "índice municipal + robustez" |
| **[pysal/spopt](https://github.com/pysal/spopt)** | — | **Regionalización espacialmente restringida**: SKATER, max-p-regions | **Alternativa recomendada a K-Means** para tipologías territoriales: garantiza clusters contiguos, defendibles en política |

---

## 5. Modelado estadístico y ML

| Recurso | ★ | Detalle | Uso |
|---|---|---|---|
| **[scikit-learn/scikit-learn](https://github.com/scikit-learn/scikit-learn)** | 67.859 | `PCA`, `KMeans` (**usa `n_init=50`**, el default `10` de versiones antiguas producía clusters inestables), `GaussianMixture` (`bic()`, `aic()`, `predict_proba`, `covariance_type`), `GroupKFold`, `TimeSeriesSplit`, `Pipeline`, `silhouette_score`, `adjusted_rand_score`, `QuantileRegressor`, `HistGradientBoostingRegressor` | Base de M1-M5 |
| **[dmlc/xgboost](https://github.com/dmlc/xgboost)** | 28.901 | `XGBRegressor`, **`monotone_constraints`** (clave para forzar no-compensatoriedad) | **M4** |
| **[microsoft/LightGBM](https://github.com/microsoft/LightGBM)** | ~16.000 | `LGBMRegressor`, `objective="quantile"` para bandas | **M1** (comparado con RF) |
| **[shap/shap](https://github.com/shap/shap)** | 25.825 | `shap.TreeExplainer` (exacto y rápido para XGBoost/LGBM), `shap.plots.beeswarm/waterfall/bar`, `shap.Explainer` para transformers | **M4** y toda la capa de explicabilidad |
| **[scikit-learn-contrib/MAPIE](https://github.com/scikit-learn-contrib/MAPIE)** | 1.607 | `MapieRegressor` (split CP, CV+), `MapieQuantileRegressor` (CQR), `TimeSeriesRegressor`, tests de exchangeability, control de riesgos | **Bandas de predicción al 95 %** de M1 y M4. Es la librería estándar (`scikit-learn-contrib`) |
| **[statsmodels/statsmodels](https://github.com/statsmodels/statsmodels)** | 11.699 | `SARIMAX` con exógenas, `get_forecast().conf_int()`, tests ADF | **M3** |
| **[facebook/prophet](https://github.com/facebook/prophet)** | 20.448 | Forecast aditivo con estacionalidad y holidays | **M3** (solo como contraste; con 10-15 observaciones anuales está sobre-parametrizado) |
| **[MKB-Datalab/time-series-analysis-with-SARIMAX-and-Prophet](https://github.com/MKB-Datalab/time-series-analysis-with-SARIMAX-and-Prophet)** | 21 | Notebooks que comparan SARIMA y Prophet sobre el mismo dataset con diagnóstico de residuos | Referencia de notebook para M3 |
| **[optuna/optuna](https://github.com/optuna/optuna)** | 14.955 | `MedianPruner`, espacios de búsqueda | Tuning de M4 con **espacio acotado** (n=41 no admite búsquedas libres) |
| **[mlflow/mlflow](https://github.com/mlflow/mlflow)** | 28.494 | Tracking de experimentos, Model Registry, **prompt management**, evaluación de LLM | **⚠️ Limitación verificada: MLflow NO soporta Oracle como backend store** (`mlflow/store/db/db_types.py` solo lista POSTGRES, MYSQL, SQLITE, MSSQL). Solución: MLflow local (SQLite/file) + exportar las métricas a Oracle en la capa de publicación (que es justo lo que hace el prompt 13) |
| **[treeverse/dvc](https://github.com/treeverse/dvc)** (antes `iterative/dvc`; **verificado**: la URL antigua redirige) | 15.939 | Versionado de datos y pipelines (`dvc.yaml`, `dvc.lock`, `dvc repro`) | **Reproducibilidad**: `dvc repro` reconstruye dataset y predicciones |
| **[AidanCooper/forecasting](https://github.com/AidanCooper/forecasting)** | — | Notebook benchmark SARIMA vs SARIMAX vs Prophet con **MASE / sMAPE** | **El baseline honesto de M3**: seasonal-naïve. Si SARIMAX no bate MASE, no lo uses |
| **[py-econometrics/pyfixest](https://github.com/py-economometrics/pyfixest)** | — | Regresión de **efectos fijos** de alta dimensional con sintaxis `fixest` (`feols`) | **M3/M4**: panel municipal con FE (municipio y año) |
| **[pysal/spreg](https://github.com/pysal/spreg)** | 90 | `SAR` (spatial lag), `SEM` (spatial error), `SLX`, `PanelOLS`, `Spatial_Hurdle`, `GM_2SLS` | ¿El crecimiento depende de la capacidad **vecina**? Con n=41, la estimación ML de SAR/SEM no converge → usa 2SLS/GMM o panel |
| **[pysal/esda](https://github.com/pysal/esda)** | 261 | `Moran(y, w, permutations=999, two_tailed=True)`, `Moran_Local` (LISA), `Global_Join_Count`, `Geary`, `Getis_Ord` | **Justificar el spatial K-fold** y la coherencia espacial de la tipología |
| **[pysal/libpysal](https://github.com/pysal/libpysal)** | 293 | `Queen.from_dataframe(gdf)`, `weights.KNN`, `weights.DistanceBand` | ⚠️ **Madrid tiene municipios "isla"** (Buitrago del Lozoya, La Cabrera, Valdaracete…): `Queen` los aísla y sesga el Moran/I → usa KNN o DistanceBand como robustez |
| **[pysal/splot](https://github.com/pysal/splot)** | 101 | `plot_moran`, mapas LISA (HH/LL/HL/LH) | El mapa LISA encaja directamente en el coropleta de APEX |
| **[paezha/idealista18](https://github.com/paezha/idealista18)** | 59 | Microdatos **georreferenciados de vivienda**: Madrid (94.815 anuncios), Barcelona (61.486), Valencia (33.622), **enriquecidos con el Catastro español** (calidad de materiales) y distancia a POIs. Paper en *Environment and Planning B* (2024), DOI 10.1177/23978083241242844 | **El mejor dataset público de vivienda para validar tu M1 en Madrid**. ⚠️ son *asking prices* de 2018, no transacciones |
| **[paezha/Reproducible-Research-Workflow](https://github.com/paezha/Reproducible-Research-Workflow)** | — | El workflow reproducible del paper anterior | Plantilla de reproducible research |
| **[MKB-Datalab / MKB]** | — | (ver M3) | |
| **[google-research/scikit-learn-extra](https://github.com/scikit-learn-contrib/scikit-learn-extra)** | 203 | KMeans con `init='k-means++'` y control de `n_init` | M5 |
| **[scikit-learn/scikit-learn · examples/mixture/plot_gmm_selection.py](https://github.com/scikit-learn/scikit-learn/blob/main/examples/mixture/plot_gmm_selection.py)** | — | Selección de GMM por **BIC/AIC** sobre rejilla de `n_components` × `covariance_type` | **M5**: el criterio canónico. ⚠️ BIC penaliza k duro → con n=41 saldrás k=2 o 3 |
| **[dekshinaudayan/kmeans-GMM-clustering-tutorial](https://github.com/dekshinaudayan/kmeans-GMM-clustering-tutorial)** | 0 | Comparativa elbow + silueta + AIC/BIC con **caso de fallo explícito en datos anisotrópicos** | El guion narrativo ideal para el notebook de M5 |
| **[akestoridis/mcdm](https://github.com/akestoridis/mcdm)** | 73 | SAW, MEW, **TOPSIS**, mTOPSIS; ponderación MW, **EM (entropía)**, SD, **CRITIC**, VIC; normalización Linear1/2/3, Vector | **M5**: implementa los métodos MCDM en vez de hacerlo a mano |
| **[quatrope/scikit-criteria](https://github.com/quatrope/scikit-criteria)** | — | (el repo `scikit-criteria/scikit-criteria` **no existe**; el real es este) Framework scikit-learn-compatible de criterios múltiples | M5 |
| **[kotbaton/pymcdm](https://github.com/kotbaton/pymcdm)** | — | TOPSIS, VIKOR, PROMETHEE, ELECTRE, MULTIMOORA, WASPAS | M5 |

---

## 5 bis. AVM, causalidad en panel y validación espacial (búsqueda específica)

### 5 bis.1 Hallazgo negativo importante

> **No existe ningún repositorio de GitHub de calidad que implemente un AVM sobre datos del
> Catastro/INE españoles con metodología reproducible.** Los repos españoles son
> (a) proyectos de estudiante de 1-3 estrellas, (b) reproducciones de artículos en R, o
> (c) envoltorios de acceso a datos.
> **Consecuencia**: el M1 de LoDCORE hay que construirlo con los patrones de `openavmkit` +
> `ccao-data/model-res-avm`, y el acceso a datos con `gisce/pycatastro` + la API Tempus3 del INE.
> **Eso no es un problema, es la aportación metodológica del proyecto** — y hay que
> decirlo así en la memoria.

### 5 bis.2 AVM: implementaciones de referencia

| Recurso | ★ | Qué aporta |
|---|---|---|
| **[ccao-data/model-res-avm](https://github.com/ccao-data/model-res-avm)** | 73 | **El AVM de producción mejor documentado del mundo** (Cook County, IL). Pipeline DVC de **7 etapas**: `Ingest → Train → Assess → Evaluate → Interpret → Finalize → Upload → Export`. Documenta el **rastro de decisión de modelo** (probó Linear, XGBoost, CatBoost, RF, SVM, NN, stacking) y eligió **LightGBM** (ganaba en RMSE, entrenaba 2× más rápido en CPU, **maneja categóricos de forma nativa** sin one-hot). Evalúa **métricas de tasación**: **COD, PRD, PRB, MKI** + desglose geográfico y por clase. ⚠️ AGPL-3.0, R/tidymodels → portar a Python |
| **[larsiusprime/openavmkit](https://github.com/larsiusprime/openavmkit)** | 95 | **Toolkit Python de mass appraisal**, agnosticista de jurisdicción: limpieza → **enriquecimiento** (geo básico, spatial joins, **Overture**, Census, distancia/proximidad, **calles OSM**, **spatial lag**, **spatial inference**) → modelado → **evaluación estadística** → **informes PDF**. Abstracción de **"jurisdicción"** con `settings.json` y DSL de preprocesamiento. **Módulo de ajuste temporal** (indexación por período de mercado) → **justo lo que necesita un AVM sobre 10-20 años de panel**. ⚠️ licencia sin especificar |
| **[ccao-data/model-condo-avm](https://github.com/ccao-data/model-condo-avm)** | 14 | Pipeline hermana para clases multifamiliares → **referencia para segmentar un modelo en sub-modelos por tipo de vivienda** (relevante en municipios rurales con stock heterogéneo) |
| **[AndreaAzabal/proyecto-vivienda](https://github.com/AndreaAzabal/proyecto-vivienda)** | 7 | Único repo que modeliza **precio de vivienda en Madrid** con GBM + Idealista. Aporta el **pipeline de parseo de Idealista** y el uso de **`satscan`** (estadística de barrido espacial) → justo la herramienta para **detectar qué municipios recibieron un choque** (la definición del grupo tratado del M4) |

### 5 bis.3 La metodología de referencia: Rico-Juan & Taltavull (2021)

**Paper**: *"Machine learning with explainability or spatial hedonics tools? An analysis of the asking
prices in the housing market in Alicante, Spain"*, *Expert Systems with Applications* 171:114590.
- DOI (open access, CC BY-NC-ND): https://doi.org/10.1016/j.eswa.2021.114590
- **Manuscrito aceptado (gratis, texto completo)**: https://rua.ua.es/handle/10045/111958
- Revisión crítica complementaria: https://www.mdpi.com/2220-6604/5/2/32 (*Urban Science* 5(2):32)
- **No hay repo público** (buscado por autor y topics). La copia del RUA es el único artefacto citable.

**Método exacto (extraído del manuscrito, §4):**

| Aspecto | Detalle |
|---|---|
| Ámbito / periodo | Alicante, **2004-2012** |
| Fuente | **Tabimed** (empresa de tasación, ya extinta): 1.124.502 observaciones; muestra aleatoria 30 % = 392.412; tras geolocalización → **~56.000** |
| Target | **Log precio** (media 11,52; sd 0,61) → con back-transform y *smearing estimator* |
| Features | **52 características** (vivienda, edificio, entorno) |
| Algoritmos | k-NN (k=1,3,5,7), árbol, **RF con n_trees ∈ {100,200,300,400,500}**, AdaBoost, ANN, Ridge, Lasso |
| **Modelo elegido** | **Random Forest (200)** — *"we use the random forest (200) method, according to the results obtained in Section 4.2.2"* |
| Métricas | **RMSE**, **%RMSE**, **MAE**, **%MAE**, **P** (grado de exactitud explicativa), **R²**. Resultado: *"error of less than 2 %"* |
| Validación | **CV de 10 folds** + **test de significación pareado de Wilcoxon** entre cada par de algoritmos en cada métrica |
| Explicabilidad | **importancia por permutación (Breiman)** *y* **SHAP** (Lundberg & Lee 2017) |
| Hedonic back-check | El **Modelo hedónico (1)** se estima *"using the variables defined in the previous random forest (200)"* → **el RF selecciona el conjunto de regresores** y luego se interpretan los coeficientes |
| Cuantiles | **10 cuantiles por cada 10 % de la distribución de precio** → heterogeneidad del efecto por tramo de precio |
| espacial | Contrasta **SAR / SEM / SDM / SDEM** contra los modelos de ML |

**Lista de features (Tabla 1) — transplantable tal cual al M1**, y es **exactamente el perfil de
"municipio rural de baja oferta"**: edad del barrio, tipo urbano, **crecimiento poblacional**,
urbano/rural, **nivel de ingresos**, **densidad**, **calidad de la red viaria**, **tipo y calidad
del agua**, **tipo y calidad del alcantarillado**, **tipo y calidad de la iluminación**,
**calidad de comercios**, **calidad de centros educativos**, **calidad de centros sanitarios**,
**calidad de instalaciones deportivas y de ocio**, **autobús / tren / metro**, tipo de vivienda,
número de viviendas en el edificio, número de ascensores, edad de la vivienda.

> **Advertencia del propio paper que aplica a LoDCORE**: *"using provincial (municipal) codes,
> postal codes, and latitudes and longitudes as regressors makes no sense from an economic
> perspective even though they capture the spatial differences in housing prices"*
> → o se eliminan los códigos geográficos, o se tratan explícitamente como un
> **bloque de efectos aleatorios espaciales**, nunca como features económicas.

**Sesgos que hay que declarar en la memoria**: (a) *asking prices*, no transacciones (sesgo
sistemático al alza, y el AVM alimenta un ratio de accesibilidad económica);
(b) log-price exige *smearing* al deshacer la transformación; (c) el paper no trata alquiler
ni esfuerzo financiero, que también necesitáis.

### 5 bis.4 Incertidumbre: conformal prediction espacial

| Recurso | ★ | Detalle |
|---|---|---|
| **[adhjort/ConformalPrediction](https://github.com/adhjort/ConformalPrediction)** | 0 | **El código OFICIAL de arXiv:2312.06531** (conformal espacialmente ponderado para AVM). MIT, **R**, 8 commits. Implementa: `TrainModels()` (xgboost/lightgbm/rf), `DataSplit()`, `SplitCP_Wrapper_New()`, `AddCityDistrictInfo()`. Pesos: `modi::weighted.quantile(x = calibration_subset$Ri, w = ww_normalized, prob = alpha_level)`. Métricas: `Coverage`, `CoverageGap`, `M_IntSize`, `M_RelIntSize`. ⚠️ **R, no Python** → reimplementar (es la *especificación*, no una dependencia) |
| **[scikit-learn-contrib/MAPIE](https://github.com/scikit-learn-contrib/MAPIE)** | 1.607 | El sustituto **de producción en Python**: `MapieRegressor` (split-CP), `MapieQuantileRegressor` (CQR), `TimeSeriesRegressor`, control de riesgos. Acepta **cualquier** estimador sklearn-compatible (RF, LGBM, XGB). ⚠️ sus folds internos deben sustituirse por los **espaciales** y el split de calibración debe **agrupar por municipio** |
| **[superlinear-ai/conformal-tights](https://github.com/superlinear-ai/conformal-tights)** | 119 | **Cuantiles coherentes entre horizontes**. Imprescindible: al publicar bandas de **5 y 10 años**, una banda por horizonte puede ser no monótona (P5(5a) > P5(10a)). Esta librería fuerza la coherencia → requisito duro para un fan-chart creíble |
| **[aangelopoulos/conformal-prediction](https://github.com/aangelopoulos/conformal-prediction)** | 1.107 | **Conformal Prediction: A Gentle Introduction** en notebooks: split conformal, **inferencia conformal adaptativa** (recalibración rodante) y conformal **para series temporales**. La adaptativa es el arreglo estándar para la deriva del mercado inmobiliario (COVID 2020, choque de tipos 2022): una banda calibrada en 2015-2020 estará mal calibrada en 2026+ |
| **[henrikbostrom/crepes](https://github.com/henrikbostrom/crepes)** | 585 | `ConformalRegressor` + **`ConformalPredictiveSystem`** (cobertura *anytime-valid* online). → si queréis **monitorizar** que las bandas siguen calibradas cada año que llega el nuevo padrón |
| **[valeman/awesome-conformal-prediction](https://github.com/valeman/awesome-conformal-prediction)** | 1.329 | Índice canónico de la literatura de CP: papers, libros, libs Python+R, e **implementaciones de CP espacial** |

**Método de las 5 variantes de CP del paper** (arXiv:2312.06531) y cómo se traduce a LoDCORE:

| Variante | Paper | LoDCORE | Nota crítica |
|---|---|---|---|
| CP estándar | no ponderado | baseline | Cobertura marginal pero mal calibrada por región |
| **Mondrian CP** | calibrado por distrito | **por municipio** | n=41 → sets de calibración diminutos → **bajo poder estadístico**. Usar solo como híbrido parcial |
| **Spatial CP** | `w_i = exp(−d²/η)`, peso se reduce a la mitad a **800 m** | `d` = distancia entre municipios | ⚠️ **800 m es escala de Oslo**. Vuestros municipios rurales de Madrid están a **10-80 km**: **re-derivar η** para que el peso se reduzca a la mitad a ~15-25 km |
| **NN CP** | peso 1 dentro de **1 km** | → **inutilizable** a la escala municipal | Descartar o ampliar mucho |
| Oracle CP | usa el error real | solo en simulación | Referencia teórica |

**Riesgo metodológico mayor**: el paper simula con **6.000 filas por réplica**; LoDCORE tiene
**41 municipios × 10-20 años = 410-820 filas** para el M4. El split conformal con
`n_cal ≈ 164-328` es **estadísticamente fino** y las garantías marginales se degradan.
**Mitigación**: calibration **agrupada/pooled entre municipios con ponderación espacial**, o
**bootstrap bayesiano conformal**.

### 5 bis.5 Causalidad en panel (el "choque de población" del M4)

| Recurso | ★ | Detalle |
|---|---|---|
| **[pymc-labs/CausalPy](https://github.com/pymc-labs/CausalPy)** | 1.208 | **El mejor encaje**: **Synthetic Difference-in-Differences (SDID)** de Abadie (pesos de control sintéticos → contrafactual por municipio tratado), + `SensitivityAnalyzer` (análisis bayesiano de confusores no observados), + **diferencias en diferencias**, + discontinuidad, + **difusión (serie de tiempo interrumpida)**. Devuelve **distribuciones** del efecto → **bandas de incertidumbre gratis**. ⚠️ stack PyMC pesado |
| **[py-why/dowhy](https://github.com/py-why/dowhy)** | 8.369 | Workflow causal de 4 pasos: **Model** (grafo causal) → **Identify** (`identify_effect`) → **Estimate** (`method_name="drd"` para DiD, `"iv"`, `"forest"`, `"propensity_score"`, `"causal_ensemble"`) → **Refute** (`refute_estimate`: `random_common_cause`, `placebo_treatment`, `random_data`, `data_subset`). La **suite de refutación** es justo lo que pedirá un jurado |
| **[sdfordham/pysyncon](https://github.com/sdfordham/pysyncon)** | 84 | **Synthetic control moderno** con **control sintético aumentado** (Ben-Michael-Feller-Rothstein 2021) → **intervalos válidos para una sola unidad tratada**. Incluye `parity_tests/` que lo **verifica contra el paquete R `Synth`** → argumento de corrección para el jurado. → **es como se define el grupo tratado del M4**: por cada municipio, control sintético + **p-valor placebo-in-space** |
| **[py-econometrics/pyfixest](https://github.com/py-econometrics/pyfixest)** | 358 | FE de alta dimensional con sintaxis `fixest`: `feols(pop_growth ~ shock_post \| municipio + year, cluster=~municipio)`. ⚠️ **NO resuelve el sesgo de TWFE con adopción escalonada** (Goodman-Bacon, de Chaisemartin-D'Haultfœuille) → usa SDID o Callaway-Sant'Anna |
| **[bashtage/linearmodels](https://github.com/bashtage/linearmodels)** | 1.077 | `PanelOLS` con **covarianza Driscoll-Kraay** (la correcta con correlación espacial/serial entre municipios cercanos) — **una de las líneas de código más importantes de la metodología del M4**. + `PanelIV`, `BetweenEstimator`, `FirstDifference`, `FamaMacBeth` |
| **[DoubleML/doubleml-for-py](https://github.com/DoubleML/doubleml-for-py)** | 794 | **DML** con *cross-fitting* y scores ortogonales → para la relación mediada *choque → precio (M1) → capacidad (M4)*, que es no lineal en el mediador |
| **[OscarEngelbrektson/SyntheticControlMethods](https://github.com/OscarEngelbrektson/SyntheticControlMethods)** | 196 | SCM canónico en Python con placebo-in-space. ⚠️ **sin mantener desde 2021** → preferir `pysyncon` |
| **[microsoft/SparseSC](https://github.com/microsoft/SparseSC)** | 91 | Sparse synthetic control **multi-unidad y escalonado** (Chernozhukov et al. 2021) → el caso "muchos municipios con choques en momentos distintos" |
| **[adrian-carro/housing-model-spain](https://github.com/adrian-carro/housing-model-spain)** | 9 | **Modelo basado en agentes (ABM) del mercado inmobiliario español** (Java, MIT, 506 commits), derivado de los ABM de INET@Oxford y del Banco de Inglaterra. → una de las pocas formas de propagar la incertidumbre demográfica hasta el índice de capacidad |

### 5 bis.6 Validación espacial y nested CV (decisión metodológica crítica)

| Recurso | ★ | Detalle |
|---|---|---|
| **[WalidGharianiEAGLE/spatial-kfold](https://github.com/WalidGharianiEAGLE/spatial-kfold)** | 22 | Folds espaciales con **buffer**: mantiene puntos geográficamente cercanos fuera del mismo fold. ⚠️ GPL-3.0. → Con **buffer de 20-30 km** (distancia media entre municipios) |
| **[SamComber/spacv](https://github.com/SamComber/spacv)** | 52 | **Cuatro** esquemas: `SpatialKFold`, **`BufferedCV`**, **`EnvironmentalCV`** (folds estratificados por un gradiente ambiental — **altitud 600-2000 m y contraste Sierra/meseta** en Madrid: un stress test que obliga al AVM a aprender atributos, no a memorizar la elevación) y `GroupCV`. ⚠️ **trampa**: hay que pasar coordenadas en **CRS proyectada** (EPSG:25830, ETRS89 UTM 30N); en EPSG:4326 el buffer no significa nada |
| **[rvalavi/blockCV](https://github.com/rvalavi/blockCV)** | 148 | Referencia R del marco de **Roberts et al. (2017)**; incluye `spatialBlock()`, `foldLOO` (leave-one-out espacial) y el ajuste correcto del buffer **contra el rango de autocorrelación de los RESIDUOS**, no del target |
| **[casper-hansen/Nested-Cross-Validation](https://github.com/casper-hansen/Nested-Cross-Validation)** | 64 | Clase `NestedCV` con refit final. ⚠️ de 2019 → **reimplementar el patrón (~20 líneas)** con `sklearn.cross_validate` + `HalvingRandomSearchCV` y **splitter personalizado** (spatial folds) |
| **[nickkunz/nestedhyperboost](https://github.com/nickkunz/nestedhyperboost)** | 20 | Nested CV con HPO bayesiana en el bucle interno para LightGBM/XGB/CatBoost; reporta el **optimism gap**. ⚠️ GPL-3.0 |
| **[Nixtla/mlforecast](https://github.com/Nixtla/mlforecast)** | 1.291 | Motor de **CV de series temporales en panel** con esquema `unique_id`/`ds`/`y`: folds forward-chaining con `h` y `step_size`. → tus horizontes de **5 y 10 años** son `h=5` y `h=10` directamente |
| **[statsmodels/statsmodels](https://github.com/statsmodels/statsmodels)** | 11.699 | `MixedLM` (**efectos aleatorios con pooling parcial**: con 41 municipios, FE descarta toda la información entre municipios e infla la varianza); `QuantReg` (los **modelos hedónicos de cuantiles** que usó Rico-Juan para el análisis de distributividad); `GEE` con correlación `exchangeable` |

**La decisión metodológica más importante del proyecto**: los 41 municipios de Madrid
son **geográficamente contiguos** (Sierra Oeste, Sierra Norte, Sierra del Este, Las Vegas,
Tajo-Sierra). Con K-fold aleatorio, los **vecinos inmediatos** de un municipio en test están en
train → el modelo memoriza el nivel de precio local → **métricas brutalmente optimistas**.
→ Folds espaciales con buffer + reportar la **dispersión entre folds**, no solo la media.
Con 41 municipios, un 5-fold espacial deja ~8 test por fold → varianza enorme: considera
**LOO con buffer espacial** (41 folds) como estimador principal.

### 5 bis.7 Acceso a los datos específicos del proyecto

| Fuente | Repo | ★ | Detalle |
|---|---|---|---|
| **Catastro (SEC)** | **[gisce/pycatastro](https://github.com/gisce/pycatastro)** | 36 | **Cliente Python de los servicios web libres del Catastro.** *"All the consult services are implemented"*. ⚠️ GPL-3.0. **El repo de acceso a datos más importante para el M1** |
| Catastro (R) | [rOpenSpain/CatastRo](https://github.com/rOpenSpain/CatastRo) | 31 | CRAN v13: parcelas, direcciones, capas municipales, **tiles WMS/WMTS** |
| **INE** | [rOpenSpain/INEbaseR](https://github.com/rOpenSpain/INEbaseR) | 23 | Referencia de cómo llamar la API **Tempus3** (los mismos endpoints valen desde Python) |
| INE | [datania/ine-catalog](https://github.com/datania/ine-catalog) | 5 | Exportación periódica de metadatos y datasets del INE en **Python** → ingesta del padrón (tabla 68535) |
| INE · códigos | [didacrios/municipios-provincias-comunidades-INE-spain](https://github.com/didacrios/municipios-provincias-comunidades-INE-spain) | 9 | **Dumps SQL** `municipios_spain.sql` etc. → **tabla de dimensión de municipios**, cargable directo en Oracle |
| **CNIG / IGN** | [IGN-CNIG/API-CNIG](https://github.com/IGN-CNIG/API-CNIG) | 4 | **API oficial del CNIG** (EUPL-1.2, 3.895 commits): capas de límites administrativos y servicios cartográficos. **Esencial para los pesos espaciales Queen y las matrices de distancia del CP espacial** |
| OSM | [gboeing/osmnx](https://github.com/gboeing/osmnx) | 5.882 | `features_from_place` (amenities, centros educativos, sanitarios, paradas) e **isócronas por tiempo de viaje** → las features de **"calidad de servicios", "Bus/Tren/Metro" y accesibilidad** que el paper muestra decisivas |
| **Madrid (específico)** | [GeiserX/awesome-comunidad-de-madrid](https://github.com/GeiserX/awesome-comunidad-de-madrid) | 6 | Índice específico de la Comunidad de Madrid: `atabel/renfe-api`, **`fitomad/CoreEMT`** (librería de EMT Madrid), **`dieguezz/mcp-madrid-public-transport`**, `300000kms/turistificacion`, `kresp0/madridxml2osm`. **Empieza por aquí para la capa de datos de Madrid** |
| España | [GeiserX/awesome-spain](https://github.com/GeiserX/awesome-spain) | 361 | Índice CC0 con secciones **"Cartografía y Catastro"** y **"Datos Abiertos y Estadísticas"** |
| Proxy de choque turístico | [300000kms/turistificacion](https://github.com/300000kms/turistificacion) | 7 | `grid.csv`: raster de **presión de alojamiento turístico** sobre Madrid → **proxy directo del "choque de población"** para el M4 |
| Segmentación de mercado | [paezha/Machine-learning-for-market-segmentation](https://github.com/paezha/Machine-learning-for-market-segmentation) | 2 | Precedente español de **segmentar mercados heterogéneos antes de modelar** (árboles de clasificación + hedónico espacial). Tus 41 municipios son heterogéneos (Sierra vs. Vegas vs. Henares) → **tiers homogéneos de capacidad de acogida** |
| Asequibilidad | [saraluciaossar/Housing-affordability-spain-project](https://github.com/saraluciaossar/Housing-affordability-spain-project) | 1 | Único repo que operacionaliza la **asequibilidad** (núcleo económico de vuestro "esfuerzo financiero familiar"). Pista de series precio/ingreso |

## 6. Datos, validación y calidad

| Recurso | ★ | Detalle |
|---|---|---|
| **[fivetran/great_expectations](https://github.com/great-expectations/great_expectations)** | 11.890 | ⚠️ **El repo se movió**: ahora es `fivetran/great_expectations` (antes `great-expectations/great_expectations`). Expectations como tests unitarios del dato; integración con **GitHub Actions** para validar pipelines en PRs | **El requisito de procedencia del PDF** se implementa como *Expectation Suites* |
| **[unionai-oss/pandera](https://github.com/unionai-oss/pandera)** | 4.490 | Schemas declarativos para DataFrames, integración por decorador, `pandera-modin-dask`, `pandera-geopandas` | Validación de esquema en la ingesta |
| **[Data-Centric-AI-Community/fg-data-profiling](https://github.com/Data-Centric-AI-Community/fg-data-profiling)** (antes `ydataai/ydata-profiling`; **verificado**: su README dice *"ydata-profiling is now fg-data-profiling"*) | 13.735 | Perfilado EDA en una línea; `ProfileReport.to_expectation_suite()` → **convierte un perfil en una suite de Great Expectations** | EDA + puente a GX |
| **[oracle/python-oracledb](https://github.com/oracle/python-oracledb)** | 449 | `oracledb.connect(dsn, user, password)`, `cursor.fetch_df()` (pandas directo), **`cursor.setinputsizes()` para insertar `SDO_GEOMETRY`**, `outputtypehandler`, `fetch_df_bulk` | **El driver de vuestro stack**. Thin mode (sin Oracle Client) vs thick |
| **[drivendataorg/cookiecutter-data-science](https://github.com/drivendataorg/cookiecutter-data-science)** | — | Estructura reproducible: `data/raw`, `data/processed`, `notebooks/`, `src/`, `tests/`, `Makefile` | Esqueleto del repo |
| **[JoseRZapata/data-science-project-template](https://github.com/JoseRZapata/data-science-project-template)** | — | Plantilla moderna: uv, ruff, pre-commit, pytest, mypy, GitHub Actions, mkdocs | Plantilla alternativa, más "moderna" |
| **[SE-ML/awesome-seml](https://github.com/SE-ML/awesome-seml)** | — | Software engineering for ML: CI/CD para ML, TFDV, Model Card Toolkit, FairLearn, Kubeflow, MLflow | Panorama de herramientas de calidad |
| **[brandonhimpfen/awesome-machine-learning](https://github.com/brandonhimpfen/awesome-machine-learning)** | — | Índice de librerías y tutoriales por bloque | Descubrimiento |

---

## 7. Oracle, APEX y entrega

### 7.1 ⚡ El hallazgo que cambia la arquitectura: **Oracle puntú los modelos dentro de la base de datos**

**Verificado contra la documentación oficial** (`docs.oracle.com/en/database/oracle/oracle-database/26/nfcoa/onnx-support.html`,
HTTP 200, texto literal):

> *"You can import ONNX-format models to Oracle AI Database for the machine learning techniques
> **classification, regression, clustering, and embeddings**. The models will be imported as
> **first-class MINING MODEL objects** in your schema. Inference can be done using the family of
> OML scoring operators, including **PREDICTION, CLUSTER, and VECTOR_EMBEDDING**… Users can
> invoke these models from SQL queries using the same scoring operators as native in-database models."*

Consecuencia para LoDCORE: **no necesitas un microservicio Python en runtime para los 5 modelos**.

```
Python (entrenamiento)  ->  skl2onnx / onnxmltools  ->  model.onnx (bytes)
   ->  DBMS_VECTOR.LOAD_ONNX_MODEL(model_name => 'ICA_MODEL', model_data => :blob)
   ->  SELECT ... PREDICTION(ICA_MODEL, ...) FROM ...
   ->  APEX lee vistas
```

Cero saltos HTTP. El modelo vive dentro de la base de datos, con el mismo límite de seguridad
que los datos. Y la página **"Los 5 Modelos ML"** se puede **generar** desde
`USER_MINING_MODELS` + `USER_MINING_MODEL_ATTRIBUTES` en vez de escribirse a mano: eso es un
diferenciador enorme en la puntuación.

**Lo que queda en Python en runtime** (solo dos cosas, y por buenas razones):
1. **Quiz & Recomendador** — lógica de preferencias por usuario.
2. **Simulador What-If** — lógica contrafactual + recálculo de SHAP.
Ambas se exponen como **FastAPI + REST Data Source de APEX** (tipo "Simple HTTP").

| Recurso | ★ | Detalle |
|---|---|---|
| **[onnx/sklearn-onnx](https://github.com/onnx/sklearn-onnx)** (`skl2onnx`) | 631 | Convierte **pipelines completos** de scikit-learn (ColumnTransformer + imputer + scaler + modelo) en **un** grafo ONNX → sin mantener preprocesamiento en PL/SQL. ⚠️ dtypes estrictos (float64 vs float32): causa habitual de scoring silenciosamente distinto |
| **[onnx/onnxmltools](https://github.com/onnx/onnxmltools)** | 1.174 | Convierte **LightGBM, XGBoost, CatBoost** a ONNX → conversor correcto para M1 (LGBM) y M4 (XGBoost). No conviertas dos veces con ambos conversores |
| **[onnx/onnx](https://github.com/onnx/onnx)** | 21.610 | Especificación y **catálogo de operadores**: cuando `LOAD_ONNX_MODEL` rechaza tu modelo, mira el opset soportado por la versión del runtime de tu BD |
| **[microsoft/onnxruntime](https://github.com/microsoft/onnxruntime)** | 22.145 | El runtime. → **test en CI**: score ONNX vs. score Python, `max abs diff < 1e-6` antes de promover un modelo |
| **[microsoft/onnxruntime-inference-examples](https://github.com/microsoft/onnxruntime-inference-examples)** | 1.698 | Patrones de serving (FastAPI/Flask). Demo, no plantilla de producción |
| **[oracle-samples/oracle-db-examples](https://github.com/oracle-samples/oracle-db-examples)** | 1.446 | **~50 scripts OML4SQL por versión** en `machine-learning/sql/{19c,20c,21c,23ai,26ai}/` (xgboost, random forest, kmeans, feature-extraction SVD/NMF, time-series, survival, anomaly). `machine-learning/oml-services/` con **"SKLearn kMeans and GMM export to ONNX.ipynb"**. `spatial/mvc-map-api/demos/` |
| **[oracle/apex](https://github.com/oracle/apex)** | 661 | **Apps de ejemplo por rama** (21.1…26.2): `sample-apps/sample-maps/` (mapa + Oracle Spatial), `sample-charts/` (**incluye Radar**), `sample-interactive-grids/`, `sample-rest-services/`, `sample-vector-search/` (23ai Vector Search en APEX), `sample-graph-visualizations/`, `plugins/rest-source/`, `blueprints/` (scaffolding AI en 26.2: requisitos funcionales + esquema → app importable), `starter-apps/` |

### 7.2 Talleres oficiales (los labs que siguen el manual paso a paso)

| Recurso | ★ | Contenido verificado |
|---|---|---|
| **[oracle-livelabs/apex](https://github.com/oracle-livelabs/apex)** | 21 | `apex-native-map-regions/` (**es literalmente vuestro lab del Mapa Territorial**: Map Region + Oracle Spatial, tipos de capa, mapeo `SDO_GEOMETRY` ↔ GeoJSON, búsqueda por faceta), `rest-data-source/` (wizard completo hacia FastAPI), `rag-apex-app/`, `ai-interactive-report-lab/`, `cicd-workflow/` |
| **[oracle-livelabs/database](https://github.com/oracle-livelabs/database)** | 35 | `ai-vector-rag/`, `ai-vector-search-fundamentals-container/`, `26ai-duality-views/`, `json-duality/`, `heatwave-machine-learning/` → **servir el payload `apex_json` desde tablas relacionales** (JSON Relational Duality) en vez de construirlo a mano |
| **[oracle-quickstart/fastapi-oracle-database-example](https://github.com/oracle-quickstart/fastapi-oracle-database-example)** | 13 | Esqueleto mínimo FastAPI→Oracle con config por env-var y ejemplo de **connect string de Autonomous Database** (tcps + `ssl_server_dn_match=yes`). Te ahorra días con mTLS |

### 7.3 Gráficas y explicabilidad en APEX

| Recurso | ★ | Detalle |
|---|---|---|
| **APEX native Radar chart** | — | **El Comparador es un chart nativo de APEX** (3 series = 3 municipios). Internamente JET `oj-chart` tipo `line` + `coordinateSystem: polar` + `polygon polarGridShape` (docs `aexjs/chartRegion`). **Capítalo en 7 ejes** — encaja perfecto con vuestras 7 capas del mapa. Sin librería JS |
| **APEX Status Meter Gauge** | — | El **semáforo Holdura/Tensión/Colapso** es un chart type nativo. Resuelve el Cuadro de Mando sin código |
| **[apache/echarts](https://github.com/apache/echarts)** | 67.571 | `series: [{type: 'waterfall'}]` con `itemStyle.color` por item → **el waterfall SHAP** con la misma gramática visual que `shap.plots.waterfall`. Cárgalo en APEX con `require(['echarts'], ...)` (APEX 21+ ya trae RequireJS) |
| **[d3/d3](https://github.com/d3/d3)** | 113.794 | Solo si necesitas control pixel-perfect del waterfall. ⚠️ No mezcles d3 v3 (`shapjs`) y v7 en la misma página APEX |
| **`shap/shap` · carpeta `javascript/`** | 25.825 | `shapjs` (npm) renderiza **force plots**, …**pero NO tiene waterfall** y es d3-v3. → Para el waterfall, ECharts o SVG pre-renderizado en BLOB |
| **[interpretml/interpret](https://github.com/interpretml/interpret)** | 6.966 | EBM (glassbox que **predice y explica**), explicaciones locales y **contrafactuales** → encaje natural para el Simulador What-If |
| **[SeldonIO/alibi](https://github.com/SeldonIO/alibi)** | 2.650 | **Contrafactuales, anchors, prototipos, explicación contrastiva**. *"Qué tendría que cambiar Chinchón para salir de colapso?"* → narrativa ciudadana accionable |

### 7.4 Datos, calidad, linaje y despliegue

| Recurso | ★ | Detalle | Trampa |
|---|---|---|---|
| **[oracle/dbt-oracle](https://github.com/oracle/dbt-oracle)** | 70 | **Adaptador oficial de dbt para Oracle ADB** (desde v1.0.0 lo mantiene Oracle; antes Indicium). Capa de transformación `stg_*` → `int_*` → `fct_*` con **tests SQL** que imponen `ICA ∈ [0,100]`, `tipo_valor ∈ {...}`, `poblacion > 0` | ADB-first; comprueba la matriz de features (incremental, snapshot) antes de depender de él |
| **[fivetran/great_expectations](https://github.com/fivetran/great_expectations)** | 11.890 | Expectation Suites + checkpoints + Data Docs. **En Oracle: usa `add_table` sobre una VISTA (no `add_query_asset`) y `create_temp_table: false`** | ⚠️ **BUG ABIERTO EN ORACLE**: GX inyecta `FROM DUAL` → `ORA-00907` ([#10948](https://github.com/fivetran/great_expectations/issues/10948), [#8618](https://github.com/fivetran/great_expectations/issues/8618)). Mantenimiento: *"unlikely that we'll get around to fixing this issue for Oracle specifically"*. → **GX = opcional; pandera + tests dbt = puerta de calidad principal** |
| **[unionai-oss/pandera](https://github.com/unionai-oss/pandera)** | 4.490 | → **Reglas condicionales de procedencia**: `if tipo_valor=='OBSERVADO' then fuente_id is not null`; `if tipo_valor in ('PROYECTADO','SIMULADO') then escenario_id is not null`. Con `Check` de columna y cross-column | Valida el frame de Python, no lo ya cargado en Oracle: pair con `CHECK` en BD |
| **[Data-Centric-AI-Community/fg-data-quality](https://github.com/Data-Centric-AI-Community/fg-data-quality)** (antes `ydataai/ydata-quality`) | 455 | Diff de calidad entre **dos snapshots** del mismo conjunto de indicadores → detecta regresiones ("este indicador pasó de OBSERVADO a IMPUTADO") | API joven |
| **[OpenLineage/OpenLineage](https://github.com/OpenLineage/OpenLineage)** (la spec vive en `/spec`) | 2.719 | Estándar de linaje: `RunEvent`, `Job`, `Dataset`, `ColumnLineage`, integraciones con **dbt**. → tu página "Fuentes Oficiales" puede pintar un **grafo real**: INE padrón → `stg_poblacion` → `int_ica` → `fct_indice` → página APEX | **No hay conector Oracle de primera clase**: usa el conector SQL/JDBC genérico, un emisor custom (~50 líneas, POST a Marquez) o **dbt (ya emite linaje nativamente)** → lo más barato |
| **[MarquezProject/marquez](https://github.com/MarquezProject/marquez)** | 2.299 | UI de referencia del grafo de linaje + API OpenLineage | Un contenedor Java más. Alternativa: **materializar el linaje en una tabla `LINEAGE_EDGE` de Oracle** y pintarlo con el plug-in `graph-visualization` de `oracle/apex` (todo dentro del stack Oracle) |
| **[oracle/python-oracledb](https://github.com/oracle/python-oracledb)** | 455 | Thin mode, `fetch_df()` a pandas, **BLOB** (bind de `bytes` → modelo ONNX directo), **`VECTOR`** (23ai/26ai), **`JSON`** nativo (21c+), pipelining, DRCP | `cx_Oracle` está obsoleto: SQLAlchemy 2 usa `oracle+oracledb://` de forma nativa |
| **[sqlalchemy/sqlalchemy](https://github.com/sqlalchemy/sqlalchemy)** | 12.252 | Dialecto `oracle+oracledb://`, tipo `VECTOR` + **índices VECTOR (IVF)** en 23ai/26ai, pooling con `creator=oracledb.create_pool(...)` | Soporte de Oracle en SQLAlchemy es "best effort"; `VECTOR` es muy reciente (2.1) → fija versión |
| **[oracle/oci-mlflow](https://github.com/oracle/oci-mlflow)** | 29 | Plugin que mapea MLflow → OCI: `MLFLOW_DEFAULT_ARTIFACT_ROOT=oci://bucket@namespace/folder` | No cambia el *backend* de tracking (sigue siendo SQLAlchemy) |
| **[treeverse/example-get-started](https://github.com/treeverse/example-get-started)** (antes `iterative/...`) | 204 | **El proyecto canónico DVC + MLflow combinado**: `dvc.yaml`, `params.yaml`, `train.py`/`evaluate.py` con `mlflow.log_param/log_metric/log_artifact`, `mlruns/` | De 2023: drifts de API. Copia la **estructura**, no las llamadas |
| **[martgnz/es-atlas](https://github.com/martgnz/es-atlas)** | 67 | **TopoJSON desde el Equipamiento Geográfico de Referencia Nacional del IGN**, con **código INE y nombre por municipio** → tu clave de unión con el padrón. Proyección `geoConicConformalSpain` | ⚠️ **Atribución obligatoria CC BY 4.0** (Orden FOM/2807/2015) → ponla en "Fuentes Oficiales". Es TopoJSON: una conversión a GeoJSON |
| **[FMullor/TopoJson](https://github.com/FMullor/TopoJson)** | 10 | `MadridMunicipios.geojson` — geometría lista de los municipios de Madrid | ⚠️ 2022, 10★: **semilla de prototipo**, no fuente de producción. Sustituye por IGN antes de que se gradee "Fuentes Oficiales" |
| **[codeforgermany/click_that_hood](https://github.com/codeforgermany/click_that_hood)** | 490 | GeoJSON limpio de divisiones administrativas españolas | Solo CCAA, **no municipios** → sirve como referencia de calidad o capa de contexto |
| **[Dani3lSun/awesome-orclapex](https://github.com/Dani3lSun/awesome-orclapex)** | 194 | Mapa del ecosistema APEX | Rancio (2020): máquina de mapa, no fuente técnica |

### 7.5 Geometría: cómo meter IGN dentro de Oracle

Verificado en la documentación oficial de Oracle Spatial:
- `SDO_UTIL.FROM_GEOJSON` / `SDO_UTIL.TO_GEOJSON` / `SDO_UTIL.TO_JSON` / `SDO_UTIL.FROM_JSON`
- `JSON_VALUE(geojson_col, '$.a' RETURNING SDO_GEOMETRY)` y **índice espacial sobre una columna JSON** (`INDEXTYPE IS MDSYS.SPATIAL_INDEX_V2`)
- `SDO_WITHIN_DISTANCE`, `MDSYS.SPATIAL_INDEX`, Spatial Studio

**Pipeline resultante**:
```
IGN GeoJSON / TopoJSON  ->  TopoJSON->GeoJSON (topojson-client)
   ->  SDO_UTIL.FROM_GEOJSON  ->  columna SDO_GEOMETRY (SRID 4326) + índice espacial
   ->  APEX Map Region (7 capas)
```
**SRID**: por defecto 4326 (WGS84). El dato del IGN/CartoBase está en **ETRS89**; para España es
prácticamente WGS84, pero **verifícalo capa a capa** y usa `SDO_UTIL.TRANSFORM` si difieren.

### 7.6 Catálogo base (recursos ya citados en la búsqueda inicial)


| Recurso | ★ | Detalle |
|---|---|---|
| **[oracle/apex](https://github.com/oracle/apex)** | 661 | Repositorio oficial con **apps de ejemplo y starters por versión** (26.2 → 21.1). Datos clave: el **Map region** acepta `SDO_GEOMETRY` (BD local o REST Data Source), **GeoJSON como VARCHAR2/CLOB**, o pares lon/lat; fondos con **Oracle Elocation (sin API key)** y **capas vectoriales de OSM** (22.2+); JS API `apex.region.mapRegion` | **El entregable**. Cuidado: el Map region alimentado por **REST Enabled SQL no soporta `SDO_GEOMETRY`** → usa GeoJSON ahí |
| **[RonnyWeiss/APEX-Oracle-and-OSM-Maps](https://github.com/RonnyWeiss/APEX-Oracle-and-OSM-Maps)** | 7 | Plugin de región que dibuja **SDO_GEOMETRY o OSM** dentro de APEX. DB 18c-23ai, APEX 21.1-24.2 | Si el Map nativo se queda corto |
| **[RonnyWeiss/APEX-Material-BI-Dashboard](https://github.com/RonnyWeiss/APEX-Material-BI-Dashboard)** | 22 | Dashboards **D3 dentro de APEX** (JSON-driven) | Para dashboards D3 a medida. ⚠️ **Corrección**: APEX **sí tiene chart Radar nativo** (ver §7.3) → no lo necesitis para el Comparador |
| **[apex-plugins/Geo-Chart](https://github.com/apex-plugins/Geo-Chart)** | 6 | Plugin GeoChart (Google Maps) | Fallback; requiere API key |
| **[andre-simplifica/oracle-apex-ai-skills](https://github.com/andre-simplifica/oracle-apex-ai-skills)** | 20 | Skills de IA para APEX 24.2+: desarrollo, locks, exports | **Instalar en el repo del frontend** |
| **[malek-al-edresi/oracle-apex-llm-chatbot-plugin](https://github.com/malek-al-edresi/oracle-apex-llm-chatbot-plugin)** | — | Integración APEX ↔ LLM con `APEX_WEB_SERVICE`, `apex_json`, Web Credentials y **RAG con vectores de Oracle 23ai** (`DBMS_VECTOR`) | Si queréis añadir un chat explicativo sobre los datos del panel |
| **[onnx/sklearn-onnx](https://github.com/onnx/sklearn-onnx)** | 631 | `skl2onnx` para convertir scikit-learn/XGBoost/LightGBM a **ONNX** | **La pieza clave del modelo en base de datos** (ver §7.1). Ojo: para XGBoost/LightGBM el conversor correcto es `onnxmltools` |
| **[microsoft/onnxruntime](https://github.com/microsoft/onnxruntime)** | 22.145 | Inferencia ONNX | Para puntuar desde Oracle o desde un servicio |
| Blog Oracle: *OML + APEX* | — | Entrenar y desplegar con Oracle Machine Learning y servir predicciones a APEX (`PREDICTION(<MODEL> USING *)`, `PREDICTION_PROBABILITY(...)`) y **desplegar el modelo como endpoint REST** desde la AutoML UI | La vía "todo dentro de Oracle" (opción C de la arquitectura) |
| Blog Oracle: *REST-Enabling Oracle ML Models* | — | Habilitar ORDS desde APEX, registrar el schema, exponer el modelo vía API y consumirlo **desde Python con `requests`** | El puente ORDS ↔ Python |
| **APEX 26.1 — Introduction** | — | APEXlang (generar/editar apps de forma validable por agentes), **Blueprints** (scaffolding desde especificación + modelo de datos) | Alinea APEX con el flujo "spec → app" |
| **spatialthoughts/courses** | 381 | `python-dataviz.Rmd`, Streamlit, mapas Folium multicapa, **componente bidireccional `st_folium`** (mapa → eventos de la app) | Patrón de interacción del mapa con la APP |

---

## 8. Las 8 trampas metodológicas que esta búsqueda ha destapado

1. **El GTFS de CRTM está rancio** (EMT 2023, Cercanías 2024). Tu isócrona de 30 min es una foto de 2023-2025. **Documéntalo en la UI** y archiva el SHA-256 de cada feed.
2. **Min-Max + PCA no es invariante a escala** y el **signo de las componentes PCA es arbitrario**. Fija el signo determinísticamente y persiste la convención, o tu índice se da la vuelta entre ejecuciones y la APP se rompe.
3. **PCA por periodo no es comparable entre años.** Si vas a mostrar trends de sub-índices, necesitas **PCA pooled**.
4. **Un modelo de medición formativo** (tus indicadores *causan* "capacidad") es un problema real para PCA. Mazziotta & Pareto (2024) lo explica; tu salida (4 sub-índices separados) es la defendible.
5. **GMM con `covariance_type='full'` con n=41 ajusta ruido**: k=3 y d=4 → 39 parámetros para 41 observaciones. Usa `diag` o `tied`.
6. **Moran/I con `Queen` sesga en Madrid** por los municipios "isla". Usa KNN o DistanceBand como robustez.
7. **Las isócronas de `r5py` son una rejilla de puntos** (100 m por defecto) y los feeds necesitan `departure_time_window` mayor que el headway. Y el brazo privado con OSRM/ORS usa velocidad **en flujo libre** por defecto: inyecta un factor de congestión o el coche parecerá siempre infinitamente mejor.
8. **MLflow no soporta Oracle como backend store** (verificado en `mlflow/store/db/db_types.py`). Usa MLflow local + export a Oracle en la capa de publicación.

---

## 9. Gaps detectados (no hay repo público usable)

| Gap | Impacto | Fallback |
|---|---|---|
| **Canal de Isabel II** (red de abastecimiento) | Variable del bloque de sostenibilidad ambiental | MITECO BDN (cuerpos de agua) o **eliminar la variable** del índice — decisión antes de fijar la lista de variables |
| **GTFS de Renfe interurbano** | El criterio de 30 min puede infravalorar algunos municipios | Confirmar cobertura; si no, declarar el alcance en el informe |
| **Tipologías tipo "Ayuntamiento tipo"** en repos | Solo el documento del IEST y las tipologías MAPA/INE | Citar el IEST + adaptar; no es bloqueante |
| **`spatial-validate`**, `pyfixest`, `dowhy` con esos nombres exactos | Hmm — `pyfixest` real: `py-econometrics/pyfixest`; DoWhy real: `py-why/dowhy`; validación espacial: `scikit-learn-contrib/spatial-validate` no existe → usa `scikit-learn-contrib/sklearn-explain` y `scikit-learn-contrib/inspection` | Verificar nombre antes de clonar |

---

## 10. Cómo repetir esta búsqueda

```bash
# La API sin token: 10/min (search) y 60/h (core). Con token: 30/min y 5000/h.
export GITHUB_TOKEN=ghp_xxx

# Búsquedas por tema (las que mejor funcionan; las frases largas devuelven 0 porque GitHub hace AND)
curl -s "https://api.github.com/search/repositories?q=topic:gtfs+language:python&sort=stars&per_page=20" \
  -H "Authorization: Bearer $GITHUB_TOKEN" | jq '.items[] | {full_name, stargazers_count, description}'

# Múltiples repos en una sola llamada (OR implícito)
curl -s "https://api.github.com/search/repositories?q=repo:a/b+repo:c/d" -H "Authorization: Bearer $GITHUB_TOKEN"

# Ficheros sin límite de API
curl -s https://raw.githubusercontent.com/<owner>/<repo>/<branch>/<path>
```

**Trampa**: la búsqueda por frase larga (`"conformal prediction regression uncertainty"`) devuelve **0 resultados**
porque GitHub exige todos los términos. Usa `topic:`, `language:`, `stars:>N` y nombres de fichero.
