# Estructura del repositorio LoDCORE Madrid

Árbol de directorios y justificación de cada carpeta y archivo clave.
Proyecto: **Datathon LoDCORE Madrid** — dataset municipal integrado, 5 modelos (AVM, indicadores, demografía, capacidad de acogida, recomendador), publicación en Oracle/APEX y serving mínimo en FastAPI.

> **Aviso (23 oct 2026):** este documento es el **mapa objetivo** del repositorio,
> no un inventario de lo ya implementado. El estado real, los comandos y las
> limitaciones están en `README.md`. Carpetas como `src/lodcore/ingest/`,
> `mlruns/` o `.github/prompts/` pueden no existir todavía; las descripciones de
> algoritmos en el árbol pueden corresponder al prompt original y no al código
> actual. La tabla de la sección 2 es la referencia corregida.

---

## 1. Árbol de directorios

```text
.
├── .github/
│   └── prompts/                 # 14 prompts operativos ya existentes (etapas del pipeline)
│       ├── 01-ingestion.md
│       ├── 02-calidad.md
│       ├── 03-features.md
│       ├── 04-m1-avm.md
│       ├── 05-m2-indicadores.md
│       ├── 06-m3-demografia.md
│       ├── 07-m4-capacidad.md
│       ├── 08-m5-recomendador.md
│       ├── 09-validacion.md
│       ├── 10-oracle-apex.md
│       ├── 11-auditoria.md
│       ├── 12-ci-cd.md
│       ├── 13-documentacion.md
│       └── 14-presentacion.md
├── data/
│   ├── raw/                     # INMUTABLE, versionado con DVC. Nunca editar a mano.
│   │   ├── ine/                 # Padrón, Tempus3, renta, pirámide, saldos migratorios
│   │   ├── ckan_madrid/         # datos.comunidad.madrid (sanidad, educación, servicios sociales, residuos, calidad aire, presupuestos)
│   │   ├── catastro/            # Estadísticas catastrales, SECAccDescargaDatos
│   │   ├── crtm_gtfs/           # GTFS CRTM (EMT, Cercanías, interurbanos)
│   │   ├── osm/                 # Red viaria OSM / Geofabrik
│   │   ├── ign_cnig/            # CartoBase, límites municipales (CC BY 4.0)
│   │   ├── miteco/              # SNCZI agua, calidad aire
│   │   ├── renfe/               # Datos abiertos Renfe
│   │   ├── notariado/           # Precios vivienda (notariado.org)
│   │   └── canal_isabel_ii/     # Datos agua
│   ├── interim/                 # Datos tras ingestión cruda, antes de validar (punto-en-tiempo)
│   ├── processed/               # Dataset municipal integrado y versionado (F2)
│   ├── external/                # Referencias externas estáticas (códigos INE, comarcas, EPSG)
│   └── validated/               # Dataset listo para modelado (pandera aprobado)
├── docs/
│   ├── ADR/                     # Decision Records (por qué cada fuente, umbral, modelo)
│   ├── diccionario_datos.md     # Todas las variables: origen, método, tipo, licencia, atribución
│   ├── fuentes_oficiales.md     # Catálogo de ~30 fuentes públicas con URL y licencia
│   ├── metrologia.md            # Definición operativa de capacidad de acogida (PENDIENTE de tu validación)
│   ├── limite_no_compensatorio.md# Reglas duras de colapso (semáforo ICA, umbrales)
│   └── cambios.md               # Changelog de municipios/etiquetado (no silencioso)
├── notebooks/
│   ├── 00-exploratorio-raw.ipynb
│   ├── 01-eda-por-fuente.ipynb
│   └── 02-prototipo-visual.ipynb   # Solo exploración; nada entra al pipeline sin pasar por src/
├── oracle/
│   ├── ddl/                     # Fuente de verdad: tablas, índices, vistas, SDO_GEOMETRY
│   │   ├── 01-tablas_raw.sql
│   │   ├── 02-tablas_procesadas.sql
│   │   ├── 03-vistas_apex.sql    # Vistas con origen, metodo, dataset_version
│   │   ├── 04-indices_espaciales.sql
│   │   ├── 05-modelos_onnx.sql   # DBMS_VECTOR.LOAD_ONNX_MODEL + PREDICTION()
│   │   └── 06-dataset_completo_APEX.sql  # EN REVISIÓN: duplica municipios_procesados del 02
│   ├── apex_export/             # Export del workspace APEX (3 páginas MVP; 9 como roadmap)
│   ├── onnx/                    # Modelos exportados a ONNX listos para Oracle
│   └── sql/
│       ├── queries_ciudadano.sql
│       └── queries_institucion.sql
├── src/lodcore/
│   ├── __init__.py
│   ├── config/                  # thresholds.py, weights.py, params.yaml (raíz + copia sincronizada idéntica)
│   ├── ingest/                  # Conectores: INE, CKAN Madrid, Catastro, GTFS/CRTM, OSM, IGN/CNIG, MITECO, Renfe, Notariado
│   │   ├── __init__.py
│   │   ├── base.py
│   │   ├── ine_client.py
│   │   ├── ckan_madrid_client.py
│   │   ├── catastro_client.py
│   │   ├── crtm_gtfs_client.py
│   │   ├── osm_client.py
│   │   ├── ign_cnig_client.py
│   │   ├── miteco_client.py
│   │   ├── renfe_client.py
│   │   ├── notariado_client.py
│   │   └── canal_isabel_ii_client.py
│   ├── data/                    # Esquemas pandera, procedencia, quality checks, punto-en-tiempo
│   │   ├── __init__.py
│   │   ├── schemas.py           # pandera schemas por fuente y por fase
│   │   ├── provenance.py        # Origen/metodo en cada celda
│   │   ├── quality_gates.py     # Puertas de calidad (no Great Expectations en Oracle)
│   │   └── pointintime.py       # fecha_disponible por fila
│   ├── features/                # Panel municipal, joins point-in-time, 7 bloques de factores
│   │   ├── __init__.py
│   │   ├── panel_municipal.py
│   │   ├── bloque_1_demografia.py
│   │   ├── bloque_2_vivienda.py
│   │   ├── bloque_3_transporte.py
│   │   ├── bloque_4_sanidad_educacion.py
│   │   ├── bloque_5_necesidades_ciudadanas.py
│   │   ├── bloque_6_sostenibilidad.py
│   │   ├── bloque_7_presupuestos.py
│   │   └── subindices.py        # MinMaxScaler 0-100: 4 sub-índices
│   ├── models/
│   │   ├── __init__.py
│   │   ├── base.py              # Interfaz común: train, predict, uncertainty_95, to_onnx
│   │   ├── m1_avm/              # Random Forest / LightGBM: precio m² + esfuerzo familiar
│   │   │   ├── train.py
│   │   │   ├── predict.py
│   │   │   ├── model.onnx
│   │   │   └── metrics.json
│   │   ├── m2_indicadores/      # PCA + grafos/isócronas (Dijkstra/A* OSM + GTFS)
│   │   │   ├── train.py
│   │   │   ├── isocronas.py
│   │   │   ├── pca_subindices.py
│   │   │   └── metrics.json
│   │   ├── m3_demografia/       # Extrapolación geométrica calibrada: proyección 5/10 años, bandas 95%
│   │   │   ├── train.py
│   │   │   ├── project.py
│   │   │   └── metrics.json
│   │   ├── m4_capacidad/        # Gradient Boosting + atribuciones aditivas + no-compensatoriedad
│   │   │   ├── train.py
│   │   │   ├── predict.py
│   │   │   ├── shap_background.json  # Fijado y persistido (auditable)
│   │   │   ├── reglas_no_compensatorias.py
│   │   │   └── metrics.json
│   │   └── m5_recomendador/     # K-Means / GMM + MCDM similitud coseno ponderada
│   │       ├── train.py
│   │       ├── recommend.py
│   │       ├── clustering.json
│   │       └── metrics.json
│   ├── explain/                 # SHAP → JSON + redacción en lenguaje natural (español)
│   │   ├── shap_to_json.py
│   │   ├── redaccion_natural.py # Sin causalidad ("el modelo asocia", no "causa")
│   │   └── plantillas_es.md
│   ├── publish/                 # Escritura a Oracle (oracledb thin mode)
│   │   ├── __init__.py
│   │   ├── oracle_writer.py
│   │   ├── to_views.py
│   │   └── uncertainty_band.py  # Ninguna predicción sin origen y sin banda 95%
│   └── serving/
│       └── fastapi/             # N3: /recomendar, /whatif y /optimizar-presupuesto
│           ├── app.py
│           ├── recomendar.py    # Preferencias por usuario (ciudadano)
│           └── whatif.py        # Contrafactual + recálculo SHAP (institución)
├── tests/
│   ├── __init__.py
│   ├── unit/
│   │   ├── test_ingest.py
│   │   ├── test_schemas.py
│   │   ├── test_features.py
│   │   └── test_models.py
│   ├── integration/
│   │   ├── test_onnx_equivalence.py   # |score_ONNX − score_Python|: rel < 1e-6, abs < 1e-3
│   │   ├── test_pointintime.py
│   │   └── test_no_leakage.py         # Temporal, espacial, entre fases
│   └── fixtures/                # Datos de prueba sintéticos (nunca PII real)
├── mlruns/                      # MLflow tracking local (backend Postgres si se usa Oracle no soportado)
├── config/
│   ├── thresholds.py            # Umbrales hard-coded únicos (1.500, 95%, ICA, 30 min, +5/+10)
│   ├── weights.py               # Pesos MCDM y sub-índices
│   └── params.yaml              # Hiperparámetros fijos (registrados en MLflow)
├── dvc.yaml                     # Pipeline reproducible: dvc pull && dvc repro
├── params.yaml
├── pyproject.toml               # Python 3.11+, uv, ruff, mypy, pytest
├── README.md                    # Solo para humanos; AGENTS.md es la fuente de verdad para IA
├── AGENTS.md                    # Vive en PROMPTS-LoDCORE/AGENTS.md (kit de la cátedra; no hay copia en raíz)
└── LICENSE
```

---

## 2. Justificación detallada por carpeta y archivo clave

| Ruta | Contenido | Justificación (ciudadanos / instituciones / rigor) |
|---|---|---|
| `.github/prompts/` | 14 prompts operativos | Cada prompt es una etapa del pipeline. Garantiza que cualquier agente o persona reproduzca exactamente los mismos pasos. Registro de decisiones ya verificadas. |
| `data/raw/` | Datos inmutables (DVC) | Rigor: nunca se edita a mano. Proveniencia total. Si un dato se corrompe, se recupera desde DVC. |
| `data/raw/ine/` … `canal_isabel_ii/` | Una subcarpeta por fuente pública | Trazabilidad: cada fuente de *Fuentes de datos.pdf* tiene su propio contenedor. Facilita auditoría y reposición individual si una URL pública cambia. |
| `data/interim/` | Datos tras ingestión, antes de validar | Separa lo crudo de lo validado. Permite depurar ETL sin tocar `raw/`. |
| `data/processed/` | Dataset integrado y versionado | Objetivo del PDF: «Dataset municipal integrado y versionado que consolida los siete bloques de factores». Una sola fuente de verdad para los 5 modelos. |
| `data/external/` | Códigos INE, comarcas, EPSG:25830 | Referencias estáticas necesarias para joins espaciales y administrativos. |
| `data/validated/` | Dataset aprobado por pandera | Puerta de calidad: ningún modelo consume datos que no pasen `validated/`. |
| `docs/ADR/` | Decision Records | Rigor máximo: queda constancia de por qué se eligió cada fuente, umbral o algoritmo. Evita decisiones ocultas. |
| `docs/diccionario_datos.md` | Todas las variables con origen/método/licencia | Cumple la regla de `AGENTS.md`: «Toda variable lleva procedencia». Imprescindible para instituciones que auditen el sistema. |
| `docs/fuentes_oficiales.md` | Catálogo de ~30 fuentes públicas con URL | Demuestra «no me creas nada»: cada dato se puede rastrear a su origen oficial. |
| `docs/metrologia.md` | Definición operativa de capacidad de acogida | Pendiente de validación (ver preguntas al final). Aquí se define exactamente el target de M4. |
| `docs/limite_no_compensatorio.md` | Reglas duras de colapso | Implementa la hipótesis central: carencia severa no compensable. Semáforo ICA, umbrales 1.500 hab/médico, 95 % aulas. |
| `docs/cambios.md` | Changelog de municipios/etiquetado | Rigor: no se elimina ni reetiqueta ningún municipio silenciosamente. |
| `notebooks/` | Exploratorios (no parte del pipeline) | Permite análisis ad hoc sin contaminar el código reproducible. Regla de `AGENTS.md`: nada entra a `src/` sin ejecutarse y verificarse. |
| `oracle/ddl/` | DDL versionado (tablas, vistas, índices espaciales) | Fuente de verdad para Oracle. APEX consume, no redefine. Geometría con `SDO_UTIL.FROM_GEOJSON` + SRID ETRS89. |
| `oracle/apex_export/` | Export workspace APEX (9 páginas) | Captura el prototipo de interfaz: portal ciudadano + panel institucional. Permite reimportar en cualquier entorno APEX. |
| `oracle/onnx/` | Modelos ONNX para Oracle | N2: scoring dentro de Oracle con `DBMS_VECTOR.LOAD_ONNX_MODEL` + `PREDICTION()`. Evita entrenar en APEX. |
| `oracle/sql/queries_ciudadano.sql` | Consultas para portal ciudadano | Separación clara: consultas optimizadas para el perfil ciudadano (ranking, fichas municipales). |
| `oracle/sql/queries_institucion.sql` | Consultas para panel institucional | Consultas agregadas por comarca, matriz de diagnóstico, simulador de inversiones. |
| `src/lodcore/config/` | `thresholds.py`, `weights.py`, `params.yaml` | Fuente de pesos y umbrales. Hay dos copias idénticas de `params.yaml` (raíz y este paquete); `cargar_params()` prefiere la raíz. Mantenerlas sincronizadas. |
| `src/lodcore/ingest/` | Conectores por fuente | Uno por fuente oficial (INE, CKAN Madrid, Catastro, CRTM GTFS, OSM, IGN/CNIG, MITECO, Renfe, Notariado, Canal Isabel II). Fácil de mantener si una API cambia. |
| `src/lodcore/data/` | Esquemas pandera, procedencia, punto-en-tiempo | Cada celda lleva `origen` y `metodo`. `fecha_disponible` evita fuga temporal. Puertas de calidad con pandera (no Great Expectations en Oracle, que falla con `FROM DUAL`). |
| `src/lodcore/features/` | Panel municipal + 7 bloques de factores | Implementa exactamente los 7 factores del PDF: demografía, vivienda, transporte, sanidad/educación, necesidades ciudadanas, sostenibilidad, presupuestos. Joins point-in-time. |
| `src/lodcore/features/subindices.py` | 4 sub-índices 0–100 (MinMaxScaler) | Capacidad Sanitaria/Educativa, Conectividad y Movilidad, Sostenibilidad Ambiental, Músculo Presupuestario. Sin multicolinealidad gracias a PCA. |
| `src/lodcore/models/m1_avm/` | Random Forest (AVM) | Estima precio de referencia por m² y esfuerzo financiero familiar. Features reales del panel F2: tiempo a Madrid, densidad, fibra, paradas, viviendas vacías, médicos/1.000 hab y holgura escolar. Con n=20 el R² fuera de muestra es negativo: módulo ilustrativo, no AVM validado. |
| `src/lodcore/models/m2_indicadores/` | PCA + heurística de tiempos | Isócronas 30 min (público vs privado) estimadas a partir del tiempo a Madrid y de la densidad de paradas; no es un cálculo de rutas sobre OSM/GTFS. |
| `src/lodcore/models/m3_demografia/` | Extrapolación geométrica calibrada | Proyección 5 y 10 años con bandas de incertidumbre 95 %, calibrada con la proyección padronal intermedia de 2031. |
| `src/lodcore/models/m4_capacidad/` | Gradient Boosting + atribuciones aditivas + no-compensatoriedad | Core del proyecto. Predice el índice de capacidad de acogida. Las atribuciones (aproximación de 2 órdenes, no Shapley exacto) explican por municipio, sin causalidad. Reglas duras impiden que un servicio colapsado se compense con otros. |
| `src/lodcore/models/m5_recomendador/` | K-Means + MCDM | Segmenta municipios en 4 tipologías y genera un ranking personalizado por preferencias del ciudadano. |
| `src/lodcore/explain/` | Atribuciones → JSON + redacción español | Las atribuciones describen el modelo, no la realidad. Redacción en español de España, sin palabras causales. JSON se publica en Oracle para que APEX lo dibuje. |
| `src/lodcore/publish/` | Escritura Oracle (`oracledb` thin) | Ninguna predicción se publica sin origen y sin banda 95 %. Thin mode = no depende de Oracle Client thick. |
| `src/lodcore/serving/fastapi/` | N3: `/health`, `/recomendar`, `/whatif`, `/optimizar-presupuesto` | Runtime Python mínimo. Todo lo demás se puntúa en Oracle (N2). Menor superficie de ataque y mantenimiento. |
| `tests/unit/` | Pruebas unitarias por capa | Cada componente probado aisladamente. |
| `tests/integration/test_onnx_equivalence.py` | Equivalencia ONNX (rel < 1e-6, abs < 1e-3) | Obligatorio en CI antes de promover. Detecta fallos de dtype (float64 vs float32) y operadores no soportados. |
| `tests/integration/test_no_leakage.py` | Sin fuga espacial/fase | Sobre el panel de 20 municipios: valida `GroupKFold` por comarca (train/test sin solapamiento) y que M4 no usa proyecciones futuras de M3. El buffer espacial 20–30 km queda como objetivo. |
| `tests/fixtures/` | Datos sintéticos sin PII | Pruebas reales nunca usan datos personales. |
| `mlruns/` | MLflow tracking | Experimentos y métricas registrados. Backend Postgres (no Oracle, issue #15195). |
| `config/thresholds.py` | Umbrales únicos | 1.500 hab/médico, 95 % aulas, ICA <40 / 40-59 / ≥60, isócrona 30 min, estrés +5 % / +10 %. Único módulo, actualizado junto con la tabla de la UI. |
| `dvc.yaml`, `params.yaml` | Reproducibilidad | `dvc pull && dvc repro` reconstruye dataset y predicciones desde cero. |
| `pyproject.toml` | Dependencias Python 3.11+ | uv + ruff + mypy + pytest. Sin dependencias sin justificar en PR. |

---

## 3. Notas

- **Regla de oro:** `data/raw/` es inmutable; todo cambio de datos se refleja en `docs/cambios.md` y en el `dataset_version`.
- **Procedencia obligatoria:** ninguna variable ni predicción se publica sin `origen`, `metodo` y banda de incertidumbre al 95 %.
- **Pendiente de validación:** `docs/metrologia.md` (definición operativa de capacidad de acogida, target de M4).
- **Fuente de verdad para agentes:** `PROMPTS-LoDCORE/AGENTS.md` (kit de la cátedra); el estado real del MVP está en `README.md` y `project_context.md`.
