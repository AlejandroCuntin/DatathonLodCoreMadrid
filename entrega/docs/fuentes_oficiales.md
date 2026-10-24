# Catálogo de Fuentes Oficiales del Dataset
## Proyecto LoDCORE Madrid · II Datathon 2026

> **Regla:** solo las fuentes marcadas como **CONECTADAS** se han descargado y utilizado
> para construir el panel. Las demás aparecen como **pendientes/roadmap** y sus variables
> asociadas son estimaciones o referencias curadas, nunca datos oficiales.
> Fecha de descarga de los snapshots: **24 de octubre de 2026**.

---

## 1. Fuentes conectadas (datos observados)

### 1.1. INE — Padrón Municipal continuo (tabla 2881)

| Campo | Detalle |
|---|---|
| Organismo | Instituto Nacional de Estadística (INE) |
| Conjunto | Cifras oficiales de población por municipios (Padrón, 1 de enero de 2025) |
| Endpoint | `https://servicios.ine.es/wstempus/js/ES/DATOS_TABLA/2881?nult=1&tip=AM` |
| Snapshot | `data/raw/ine/ine_padron_2881_snapshot_20261024.json` |
| Variables usadas | `poblacion_actual`, `anio_padron` |
| Cobertura | 179 municipios de la Comunidad de Madrid (se usan 20 en el piloto) |
| Licencia / condiciones | Reutilización de información del sector público con **atribución** (Ley 37/2007 y RD 1495/2011). Consultar el aviso legal del INE. |
| Atribución sugerida | «Fuente: Instituto Nacional de Estadística (INE), Padrón Municipal continuo, tabla 2881, 2025.» |

### 1.2. CKAN Comunidad de Madrid — Sanidad (centros por tipo)

| Campo | Detalle |
|---|---|
| Organismo | Comunidad de Madrid · Instituto de Estadística |
| Conjunto | «Recursos y asistencia sanitaria. Centros por tipo de centro. Municipios» |
| Package ID | `6dc2b24b-ebfd-4ad6-bde0-eb4edca6f860` |
| Resource ID | `631ebd15-c19f-4984-9ad5-bb4b8554b5e0` |
| Endpoint | `https://datos.comunidad.madrid/api/3/action/datastore_search` |
| Snapshot | `data/raw/ckan/ckan_madrid_sanidad_snapshot_20261024.json` (17.190 registros, paginado completo) |
| Variables usadas | `num_centros_salud` = centros de salud + consultorios locales del **año más reciente (2024)** |
| Licencia | **CC BY 4.0** (`license_id: cc-by`, `https://creativecommons.org/licenses/by/4.0/legalcode.es`) |
| Atribución sugerida | «Fuente: Comunidad de Madrid, Datos Abiertos, *Recursos y asistencia sanitaria. Centros por tipo de centro*, CC BY 4.0.» |

### 1.3. CKAN Comunidad de Madrid — Educación (directorio de centros)

| Campo | Detalle |
|---|---|
| Organismo | Comunidad de Madrid |
| Conjunto | «Centros educativos de la Comunidad de Madrid» |
| Package ID | `c750856d-3166-4dac-8e80-d1b824c968b5` |
| Resource ID | `28d60557-1d73-4281-ab08-6cfd3b2f5f83` |
| Endpoint | `https://datos.comunidad.madrid/api/3/action/datastore_search` |
| Snapshot | `data/raw/ckan/ckan_madrid_educacion_snapshot_20261024.json` (7.757 registros) |
| Variables usadas | `num_centros_educativos` = centros de **enseñanza reglada** en situación **ALTA** (excluye BAJA, INACTIVO, ANULACIÓN y EN TRÁMITE) |
| Licencia | **CC BY 4.0** (`license_id: cc-by`, `https://creativecommons.org/licenses/by/4.0/legalcode.es`) |
| Atribución sugerida | «Fuente: Comunidad de Madrid, Datos Abiertos, *Centros educativos de la Comunidad de Madrid*, CC BY 4.0.» |

### 1.4. IGN / CNIG — Fondo cartográfico del mapa (solo visualización)

| Campo | Detalle |
|---|---|
| Uso | Teselas de mapa del frontend (`lodcore-mapa.js`), no alimentan el panel |
| Licencia | CC BY 4.0 (atribución ya incluida en el mapa: «IGN España / CNIG») |

---

## 2. Fuentes previstas pero NO conectadas (roadmap)

| Fuente | Variable que aportaría | Estado en el MVP |
|---|---|---|
| **SERMAS** (detalle de cupos médicos) | `num_medicos_ap` real | **No conectada** → `num_medicos_ap` es calibración sintética |
| **Consejería de Educación** (plazas y alumnado) | `num_plazas_escolares`, `num_alumnos_matriculados` | **No conectada** → calibración sintética |
| **Catastro** (parcelario, vivienda vacía) | `stock_vivienda_vacia_est`, `suelo_urbano_disponible_m2` | **No conectada** → calibración sintética |
| **CRTM** (GTFS, paradas, frecuencias) | `paradas_transporte_publico`, tiempos reales | **No conectada** → referencia curada; isócronas heurísticas |
| **Colegio de Notarios** (precios escriturados) | `precio_m2_compra`, `precio_m2_alquiler` | **No conectada** → calibración sintética |
| **IGN/CNIG** (superficie y geometría) | `superficie_km2`, `latitud`, `longitud` | **No conectada** → referencia curada |
| **MITECO** (agua, calidad del aire) | sostenibilidad ambiental | **No conectada** |
| **Renfe / Canal Isabel II** | movilidad y agua | **No conectada** |

> Estas variables aparecen en el panel con `origen` distinto de `OBSERVADO` y se detallan
> en `docs/matriz_procedencia_variables.md`.

---

## 3. Texto de atribución para el paquete de entrega

> «Dataset elaborado por el equipo LoDCORE Madrid para el II Datathon LoDCOREMadrid 2026.
> Población: Instituto Nacional de Estadística (Padrón Municipal continuo, tabla 2881, 2025).
> Recuentos de centros sanitarios y educativos: Comunidad de Madrid, Datos Abiertos (CC BY 4.0).
> El resto de variables son estimaciones calibradas o referencias curadas declaradas en la
> matriz de procedencia. Este dataset no es una fuente oficial: es una elaboración propia
> sobre fuentes oficiales.»
