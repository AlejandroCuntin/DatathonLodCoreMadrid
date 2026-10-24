---
description: 'Publica resultados y SHAP en Oracle Database y genera las vistas y el export del workspace APEX (Mapa, Comparador, Escenarios)'
agent: 'agent'
tools: ['search/codebase', 'edit/editFiles', 'runCommands']
argument-hint: '[entorno=dev|prod]'
---

# Publicación en Oracle Database y capa de servicio APEX

## Misión

Publicar en **Oracle Database** todo lo que la APP necesita (predicciones, SHAP, sub-índices,
bandas, procedencia) y crear las **vistas** y el **export del workspace APEX** que consumen las
9 páginas del prototipo, respetando la regla: **Python calcula, Oracle almacena, APEX narra**.

## Alcance y precondiciones

- Precondición: al menos un modelo entrenado con artefactos versionados; credenciales en
  variables de entorno (`ORACLE_USER`, `ORACLE_PASSWORD`, `ORACLE_DSN`); `oracledb` instalado.
- Alcance: `src/lodcore/publish/`, `oracle/ddl/`, `oracle/apex_export/`.
- **Nunca** escribas credenciales en el repo. Lee de entorno o de un gestor de secretos.

## Inputs

- `${input:entorno}` — `dev` | `prod` (por defecto `dev`).

## Workflow

### 1. Modelo de datos (DDL versionado en `oracle/ddl/`)
Tablas:
```sql
-- Cabecera del dataset por municipio
CREATE TABLE lodcore.municipio (
  municipio_ine      CHAR(5) PRIMARY KEY,
  nombre             VARCHAR2(120) NOT NULL,
  comarca            VARCHAR2(80),
  corona             VARCHAR2(80),
  poblacion_padron   NUMBER,
  anio_padron        NUMBER(4),
  lat                NUMBER(9,6),
  lon                NUMBER(9,6)
);

-- Panel de variables: una fila por (municipio, año, variable)
CREATE TABLE lodcore.variable_panel (
  municipio_ine   CHAR(5) NOT NULL REFERENCES lodcore.municipio,
  anio            NUMBER(4) NOT NULL,
  variable_id     VARCHAR2(64) NOT NULL,
  valor           NUMBER,
  unidad          VARCHAR2(32),
  origen          VARCHAR2(20) NOT NULL CHECK (origen IN
                     ('OBSERVADO','IMPUTADO','ESTIMADO','PROYECTADO','SIMULADO')),
  metodo          VARCHAR2(200),
  confianza_95_lo NUMBER,
  confianza_95_hi NUMBER,
  fuente_url      VARCHAR2(500),
  dataset_version VARCHAR2(40),
  PRIMARY KEY (municipio_ine, anio, variable_id)
);

-- Predicciones por modelo
CREATE TABLE lodcore.prediccion (
  modelo_id       VARCHAR2(40) NOT NULL,
  municipio_ine   CHAR(5) NOT NULL REFERENCES lodcore.municipio,
  anio_objetivo  NUMBER(4) NOT NULL,
  valor_predicho  NUMBER,
  valor_lo_95     NUMBER,
  valor_hi_95     NUMBER,
  escenario       VARCHAR2(20) DEFAULT 'BASE',
  base_value      NUMBER,
  dataset_version VARCHAR2(40),
  generado_at     TIMESTAMP DEFAULT SYSTIMESTAMP,
  PRIMARY KEY (modelo_id, municipio_ine, anio_objetivo, escenario)
);

-- Explicabilidad SHAP
CREATE TABLE lodcore.shap (
  modelo_id      VARCHAR2(40) NOT NULL,
  municipio_ine  CHAR(5) NOT NULL REFERENCES lodcore.municipio,
  anio_objetivo  NUMBER(4) NOT NULL,
  var_id         VARCHAR2(64) NOT NULL,
  valor_observado NUMBER,
  shap_value     NUMBER,
  direccion      VARCHAR2(12) CHECK (direccion IN ('favorable','adverso')),
  es_cuello_botella CHAR(1) CHECK (es_cuello_botella IN ('0','1')),
  PRIMARY KEY (modelo_id, municipio_ine, anio_objetivo, var_id)
);
```
**Reglas**: PK compuestas que incluyan `dataset_version` en tablas de hechos; índices en
`(municipio_ine, anio)` y `(modelo_id, anio_objetivo)`; `CHECK` en `origen` (obligatorio);
comentarios `COMMENT ON TABLE/COLUMN` en español.

### 1 bis. Serving de los 5 modelos: dentro de Oracle (preferido) o FastAPI

**Opción A — el modelo vive dentro de la base de datos (preferida).**
1. Exporta el pipeline completo a ONNX: `skl2onnx` para scikit-learn, `onnxmltools` para
   XGBoost/LightGBM. Convierte el **pipeline entero** (imputer + scaler + modelo), no solo el estimador.
2. Carga en Oracle: `DBMS_VECTOR.LOAD_ONNX_MODEL(model_name => 'ICA_MODEL', model_data => :blob)`.
   Disponible en Oracle AI Database 23ai/26ai (funciones: clasificación, regresión, clustering,
   embeddings). Si tu BD es 19c/21c, salta a la opción B.
3. Puntú en SQL: `SELECT municipio_ine, PREDICTION(ICA_MODEL, ...) AS ica FROM ...` y envuélvelo
   en una vista. APEX lee la vista. **Cero saltos HTTP.**
4. **Test de equivalencia en CI**: error relativo < 1e-6 y absoluto < 1e-3 (ONNX devuelve float32;
   a escala de ~2.000 €/m², un error absoluto < 1e-6 no es representable). Los fallos típicos son
   dtypes (float64 vs float32) y operadores no soportados por la versión del runtime.
5. Genera el contenido de la página "Los 5 Modelos ML" desde `USER_MINING_MODELS` y
   `USER_MINING_MODEL_ATTRIBUTES` (o desde el espejo del registro de MLflow): **nada escrito a mano**.

**Opción B — FastAPI (si la BD no soporta ONNX, o para las funciones por usuario).**
- Solo los endpoints por usuario: `POST /recomendar` (cuerpo = perfil del ciudadano; respuesta = ranking con
  `rationale` por municipio) y `POST /whatif` (cuerpo = municipio + Δ de inversión; respuesta =
  ICA antes/después + waterfall SHAP).
- APEX los consume con un **REST Data Source de tipo "Simple HTTP"**.
- Patrón de conexión: env-var + connect string de ADB con `tcps` y `ssl_server_dn_match=yes`
  (ver `oracle-quickstart/fastapi-oracle-database-example`).

**Gráficas: prioriza lo nativo de APEX.**
| Necesidad | Solución | Notas |
|---|---|---|
| Comparador de 3 municipios | **Chart Radar nativo** | 3 series, 7 ejes = tus 7 capas del mapa. Sin JS |
| Semáforo Holdura/Tensión/Colapso | **Chart "Status Meter Gauge" nativo** | Sin CSS a medida |
| Waterfall SHAP | **ECharts** (`series:[{type:'waterfall'}]`) en una región | O renderiza el SVG en Python y guárdalo como BLOB |
| Mapa con 7 capas | **Map Region** con `SDO_GEOMETRY` + índice espacial | Geometría con `SDO_UTIL.FROM_GEOJSON` desde IGN |
| "Fuentes Oficiales" con búsqueda | **Vector Search nativo** (23ai): `DBMS_VECTOR.LOAD_ONNX_MODEL` con MiniLM, columnas `VECTOR` + HNSW | Patrón en `oracle/apex → sample-apps/sample-vector-search` |

### 2. Publicación idempotente
- Usa `oracledb` en **thin mode**. Conexión con `pool` (no abrir/cerrar por fila).
- **Upsert** (`MERGE`) por clave primaria: republicar no duplica.
- Publica en **transacción por modelo**: si falla una fila, no se deja el dataset a medias.
- **Registra** el `dataset_version` (tag DVC) en cada publicación: sin eso, una predicción
  antigua es indistinguible de una nueva.
- Elimina/reemplaza las filas de la versión anterior **solo** de los modelos republicados, no
  de toda la tabla.

### 3. Vistas para APEX
Crea vistas para cada página del prototipo:
| Vista | Contenido | Notas |
|---|---|---|
| `vw_mapa_ica` | municipio, geometría, ICA, semáforo, cuello de botella dominante, etiquetas de capa | geometría: `SDO_GEOMETRY` (Oracle Spatial) o `GeoJSON` (23ai `oracle.geojson`) |
| `vw_ficha_shap` | municipio + variables + SHAP + dirección + flag cuello de botella | para la ficha y el waterfall |
| `vw_radar_municipios` | 6 ejes normalizados por municipio (para comparar 3) | normalización común |
| `vw_cuadro_mando` | agregados por comarca y corona | servicios, inversión, alertas |
| `vw_matriz_saturacion` | escenario +5 %/+10 %: ratio sanitario y ocupación proyectados | con estado |
| `vw_modelos` | metadatos de los 5 modelos: métricas, fecha, versión, dataset | desde MLflow |
| `vw_fuentes` | fuentes oficiales con última fecha de carga y nº de registros | desde `variable_panel` |
| `vw_ranking_recomendador` | score por perfil y municipio | con `excluido` y `motivo_exclusion` |

**Requisito transversal**: **todas** las vistas de datos predictivos incluyen `origen`,
`metodo`, `dataset_version` y la banda. Sin esto, la APP puede mostrar un dato sin auditar.

### 4. Geometría municipal
- Descarga las geometrías desde **CNIG/IGN** o `datos.gob.es`, o del repositorio `inigoflores/
  ds-municipios-catastro-es` (códigos INE + MHAP del Catastro).
- Impórtalas a Oracle Spatial (`SDO_GEOMETRY`, SRID 4326). Índice espacial:
  `CREATE INDEX ... ON ... (geom) INDEXTYPE IS MDSYS.SPATIAL_INDEX`.
- **Verifica** que los 41 municipios tienen geometría válida: si falta una, la APP muestra un
  hueco. Repórtalo explícitamente.

### 4 bis. Calidad: qué usar y qué NO
- **Puerta de calidad principal**: `pandera` (esquema Python con reglas **condicionales** de
  procedencia) + **tests de `dbt-oracle`** (SQL). Aplica la misma lógica en los tres sitios:
  pandera (pre-carga), test dbt (post-carga) y `CHECK` constraint (siempre).
- **Great Expectations**: **no usarlo como puerta principal en Oracle** — inyecta `FROM DUAL` y
  provoca `ORA-00907` (issues #10948, #8618). Si lo usas como extra: `add_table` sobre una **vista**
  (no `add_query_asset`) y `create_temp_table: false`.
- **Linaje**: emite eventos OpenLineage desde dbt (ya lo hace nativamente) y materialízalos en una
  tabla `LINEAGE_EDGE` de Oracle, o renderízalos con el plug-in `graph-visualization` de `oracle/apex`.
- **Atribución**: cada fuente lleva `organismo`, `url`, `licencia`, `atribucion` y `fecha_descarga`.
  El IGN/CartoBase es **CC BY 4.0 con atribución obligatoria**.

### 5. Export del workspace APEX
- Genera `oracle/apex_export/f_<app_id>_ddl.sql` con `wwv_flow_export` (APEX 21c+:
  `apex.export` / `APEX_APPLICATION_EXPORT`).
- Versiona el export en Git y añade un **checksum** del DDL para detectar cambios no revisados.
- Documenta en `oracle/apex_export/README.md` cómo importar el export en un entorno limpio y
  cómo aplicar los cambios de DDL antes de importar.

### 6. Seguridad y mínimos permisos
- El usuario de la APP es de **solo lectura** sobre las vistas (`GRANT SELECT`), nunca sobre las
  tablas base ni sobre `oracledb`.
- La publicación usa un usuario distinto con permisos de escritura.
- No expongas la conexión a la APP.

### 7. Verificación post-publicación
- Compara el recuento de filas publicado con el del dataset en Python.
- Compara una muestra de 10 valores predichos entre Python y Oracle.
- Comprueba que **toda** fila tiene `origen` y `dataset_version` no nulos.
- Ejecuta la APP en modo dev y recorre las 9 páginas con datos reales.

## Output Expectations

1. `oracle/ddl/` con los DDL numerados (`001_municipio.sql`, `002_variable_panel.sql`, …),
   cada uno idempotente y comentado en español.
2. `src/lodcore/publish/publish.py` con: conexión thin mode, pool, upsert, transacción por
   modelo, registro de `dataset_version`, y **logs estructurados**.
3. `oracle/apex_export/` con el export y su README.
4. `reports/publicacion_oracle.md`:
```
# Publicación a Oracle
## Entorno: <dsn> | Usuario: <user> | Tablas: <n>
## Filas publicadas por tabla y modelo
## Verificación: <comparación Python vs Oracle>
## Cobertura de procedencia: % filas con origen + dataset_version
## Geometrías: 41/41 | faltantes: <lista>
## Vistas creadas: <n> (lista)
## Export APEX: <app_id> | checksum <sha256> | fecha
## Permisos: <lista de grants>
## Incidencias: <lista>
```

## Quality Assurance

- [ ] Cada modelo está importado en Oracle como `MINING_MODEL` (o tiene endpoint documentado si la
      BD no soporta ONNX) y el test de equivalencia pasa con error relativo < 1e-6 y absoluto < 1e-3 (float32).
- [ ] La página "Los 5 Modelos ML" se **genera** desde `USER_MINING_MODELS` / MLflow, no a mano.
- [ ] El Comparador usa el chart **Radar nativo** de APEX (7 ejes) y el semáforo un **Status Meter Gauge**.
- [ ] La geometría está en `SDO_GEOMETRY` con índice espacial y el SRID verificado (IGN = ETRS89).
- [ ] La publicación es **idempotente**: ejecutarla dos veces no cambia el número de filas.
- [ ] Uso `oracledb` thin mode, sin Oracle Client.
- [ ] Cada escritura va en transacción y se hace rollback si falla.
- [ ] `dataset_version` está en todas las tablas de hechos y vistas.
- [ ] `origen` tiene `NOT NULL` y `CHECK` en la base de datos (no solo en Python).
- [ ] El usuario de la APP solo tiene `SELECT` sobre vistas.
- [ ] Las 41 geometrías están cargadas o los huecos están documentados.
- [ ] No hay ninguna credencial en el repositorio.
- [ ] `uv run pytest -q` pasa.
