---
description: 'Ingesta una fuente de datos oficial española (INE, CKAN Madrid, Catastro, GTFS, OSM) con procedencia obligatoria por celda'
agent: 'agent'
tools: ['search/codebase', 'edit/editFiles', 'runCommands']
argument-hint: 'fuente=ine|ckan_madrid|catastro|gtfs|osm ; objetivo=<qué variable se quiere obtener>'
---

# Ingesta de fuente oficial con procedencia por celda

## Misión

Añadir un **conector** nuevo en `src/lodcore/ingest/` que descargue datos de una fuente oficial
pública española y los deposite en el panel municipal **marcando el origen de cada celda**
(`OBSERVADO` por defecto), de forma idempotente, versionable y reproducible.

No escribas datos a mano. El conector descarga; una función de **transformación** convierte a
formato largo; una de **validación** verifica el esquema.

## Alcance y precondiciones

- Precondición: `AGENTS.md` leído; existe `src/lodcore/data/schemas.py` con el esquema del panel.
- Alcance: **solo** `src/lodcore/ingest/`, el esquema de validación y `dvc.yaml`.
- Fuera de alcance: feature engineering, modelos, publicación en Oracle.

## Inputs

- `${input:fuente}` — `ine` | `ckan_madrid` | `catastro` | `gtfs` | `osm` (obligatorio).
- `${input:objetivo}` — variable concreta a obtener (ej. "población residente por municipio y año",
  "ratio hab/médico", "horarios GTFS CRTM") (obligatorio).
- `${input:periodo}` — rango de años. Si falta, usa el máximo disponible en la fuente.

## Workflow

1. **Localiza la fuente exacta.** Para `ine`: `https://servicios.ine.es/wstempus/js/ES/DATOS_TABLA/{id}`
   o `VALORES_VARIABLE/{id}`; para `ckan_madrid`:
   `https://datos.comunidad.madrid/api/3/action/datastore_search?resource_id={rid}` (+ `datastore_search_sql`).
   **Documenta el identificador exacto** (id de tabla INE o `resource_id` CKAN) en el docstring.
2. **Implementa el cliente** en `src/lodcore/ingest/{fuente}.py`:
   - `requests.Session` con `timeout`, `retry` con backoff exponencial y respeto de `Retry-After`.
   - **Cachea la descarga en `data/raw/{fuente}/`** con nombre que incluya la fecha del snapshot
     (`{dataset}_{YYYYMMDD}.csv`). `data/raw/` es inmutable: si el fichero existe, no se re-descarga.
   - Parsea a **formato largo canónico**:
     `municipio_ine (CHAR5) | anio | variable_id | valor | unidad | origen | metodo | fuente_url`.
   - `municipio_ine` es el **código INE de 5 dígitos** (2 provincia + 3 municipio). Nunca uses el
     nombre como clave: los nombres cambian, los códigos no.
3. **Declara la procedencia.** `origen='OBSERVADO'`, `metodo` = descripción literal de la tabla y
   el indicador (ej. `"INE tabla 68535, indicador: población residente a 1/1"`),
   `fuente_url` = URL exacta consultada. Si algún valor viene con marca de imputación en la propia
   fuente (INE las publica), respétala: no lo degrades a `OBSERVADO`.
4. **Valida** con `pandera`: tipo, rangos, unicidad de `(municipio_ine, anio, variable_id)`,
   `municipio_ine` dentro del catálogo de municipios vigente, sin nulos en `valor` salvo que la
   variable lo declare así.
5. **Detecta cambios de esquema**: si la fuente devuelve columnas nuevas o deja de devolver
   alguna, **falla en vez de adaptarte en silencio**. Registra el diff en el log.
6. **Registra la etapa en `dvc.yaml`** con `deps` (ficheros raw) y `outs` (parquet),
   y añade el snapshot a `.gitignore` vía DVC, no al repo.

## Output Expectations

1. `src/lodcore/ingest/{fuente}.py` — conector con docstring Google:
   qué hace, entradas, salidas, supuestos, fallos posibles.
2. Actualización de `src/lodcore/data/schemas.py` con el esquema de la nueva variable.
3. Bloque nuevo en `dvc.yaml`.
4. Un bloque de salida con **este formato exacto**:

```
FUENTE: <nombre> | IDENTIFICADOR: <tabla INE / resource_id / URL>
VARIABLE: <variable_id> | UNIDAD: <unidad> | COBERTURA: <años y n municipios>
FILAS: <n> | NULOS: <n> | DUPLICADOS: <n>
ORIGEN: OBSERVADO (<n> celdas)
SNAPSHOT: data/raw/<ruta>/<fichero>
RUTAS USADAS: <urls exactas>
RIESGOS: <lista>
```

## Quality Assurance

- [ ] `uv run pytest -q` pasa, incluida la prueba de idempotencia (dos ejecuciones ⇒ mismo hash).
- [ ] `uv run ruff check .` y `uv run mypy src` limpios.
- [ ] El 100 % de las filas nuevas tienen `origen`, `metodo` y `fuente_url` no nulos.
- [ ] Reejecutar el conector dos veces no cambia el resultado ni duplica filas.
- [ ] He comprobado que el `resource_id`/id de tabla es el **correcto y no un placeholder**.
- [ ] No he introducido `municipio_ine` inventado ni mapeado por nombre.
