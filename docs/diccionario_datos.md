# Diccionario de Datos — Panel Municipal LoDCORE Madrid
## II Datathon LoDCOREMadrid 2026 · `dataset_version = v1.0.0-F2`

**Dimensiones:** 20 municipios × 88 variables · **Población total:** 200.267 hab. · **Comarcas:** 8

> `origen` a nivel de fila: `OBSERVADO+SIMULADO`. El desglose por variable está en la columna **Origen** de este diccionario y en `docs/matriz_procedencia_variables.md`.

> **Nota de honestidad:** solo `poblacion_actual`, `anio_padron`, `num_centros_salud` y `num_centros_educativos` proceden de fuentes oficiales ingeridas. El resto son estimaciones, calibraciones o referencias curadas, y así se declara.

## Variables observadas (ingeridas de fuente oficial)

| Variable | Tipo | Unidad | Origen | Descripción |
|---|---|---|---|---|
| `codigo_ine` | entero | código INE | OBSERVADO | Código oficial INE de 5 dígitos (28xxx). |
| `nombre` | texto | — | OBSERVADO | Nombre oficial del municipio (nomenclátor INE). |
| `poblacion_actual` | entero | habitantes | OBSERVADO | Población padronal a 1-ene-2025 (INE, tabla 2881). |
| `anio_padron` | entero | año | OBSERVADO | Año de referencia del padrón (2025). |
| `num_centros_salud` | entero | centros | OBSERVADO | Centros de salud + consultorios locales (CKAN CAM, 2024). |
| `num_centros_educativos` | entero | centros | OBSERVADO | Centros de enseñanza reglada en situación ALTA (CKAN CAM). |

## Variables calibradas sintéticamente (seed 2026)

| Variable | Tipo | Unidad | Origen | Descripción |
|---|---|---|---|---|
| `precio_m2_compra` | decimal | €/m² | SIMULADO | Precio de compra calibrado (seed 2026); no es precio escriturado. |
| `precio_m2_alquiler` | decimal | €/m²/mes | SIMULADO | Alquiler calibrado (seed 2026); no es precio de mercado observado. |
| `num_medicos_ap` | entero | médicos | SIMULADO | Dotación de médicos de AP calibrada (seed 2026). |
| `num_plazas_escolares` | entero | plazas | SIMULADO | Plazas escolares calibradas (seed 2026). |
| `num_alumnos_matriculados` | entero | alumnos | SIMULADO | Alumnado calibrado (seed 2026). |
| `num_viviendas_totales_est` | entero | viviendas | SIMULADO | Parque residencial estimado (seed 2026). |
| `stock_vivienda_vacia_est` | entero | viviendas | SIMULADO | Vivienda vacía movilizable estimada (seed 2026). |
| `suelo_urbano_disponible_m2` | decimal | m² | SIMULADO | Suelo urbano disponible calibrado (seed 2026). |

## Variables de referencia curada (no ingeridas en el MVP)

| Variable | Tipo | Unidad | Origen | Descripción |
|---|---|---|---|---|
| `comarca` | texto | — | REFERENCIA CURADA | Comarca de planificación de la Comunidad de Madrid. |
| `superficie_km2` | decimal | km² | REFERENCIA CURADA | Superficie municipal; no se descarga de IGN en el MVP. |
| `latitud` | decimal | grados WGS84 | REFERENCIA CURADA | Latitud del núcleo urbano principal. |
| `longitud` | decimal | grados WGS84 | REFERENCIA CURADA | Longitud del núcleo urbano principal. |
| `hospital_referencia` | texto | — | REFERENCIA CURADA | Hospital público de referencia asignado al área sanitaria. |
| `camas_hospitalarias_cercanas` | entero | camas | REFERENCIA CURADA | Camas del hospital de referencia (referencia curada, no ingerida). |
| `restriccion_ambiental` | texto | S/N | REFERENCIA CURADA | Afección a espacios protegidos (referencia curada). |
| `paradas_transporte_publico` | entero | paradas | REFERENCIA CURADA | Paradas de autobús interurbano y Cercanías (referencia curada). |
| `img_local` | texto | ruta | REFERENCIA CURADA | Imagen del municipio usada por el portal. |
| `altitud_m` | entero | m | REFERENCIA CURADA | Altitud del núcleo urbano. |
| `carretera_acceso` | texto | — | REFERENCIA CURADA | Vías principales de acceso. |
| `zona_crtm` | texto | — | REFERENCIA CURADA | Zona tarifaria del CRTM. |
| `transporte_detalle` | texto | — | REFERENCIA CURADA | Descripción textual del transporte público. |
| `sanidad_detalle` | texto | — | REFERENCIA CURADA | Descripción textual de la dotación sanitaria. |
| `camas_hospital` | entero | camas | REFERENCIA CURADA | Camas del hospital de referencia (columna heredada; ver nota de conciliación). |
| `educacion_detalle` | texto | — | REFERENCIA CURADA | Descripción textual de la dotación educativa. |
| `vivienda_detalle` | texto | — | REFERENCIA CURADA | Descripción textual del parque de vivienda. |
| `patrimonio_entorno` | texto | — | REFERENCIA CURADA | Patrimonio y entorno del municipio. |

## Variables estimadas (modelos o calibración F2)

| Variable | Tipo | Unidad | Origen | Descripción |
|---|---|---|---|---|
| `tiempo_medio_madrid_minutos` | entero | minutos | ESTIMADO | Tiempo estimado a Madrid en vehículo privado, hora valle. |
| `cobertura_fibra_pct` | decimal | % | ESTIMADO | Cobertura FTTH estimada; no ingerida en el MVP. |
| `score_sanidad` | decimal | 0–100 | ESTIMADO | Subíndice calibrado de sanidad (Min-Max winsorizado). |
| `score_educacion` | decimal | 0–100 | ESTIMADO | Subíndice calibrado de educación. |
| `score_servicios` | decimal | 0–100 | ESTIMADO | Subíndice agregado de servicios (auditoría; no entra en el ICA). |
| `score_conectividad` | decimal | 0–100 | ESTIMADO | Subíndice calibrado de conectividad. |
| `score_vivienda` | decimal | 0–100 | ESTIMADO | Subíndice calibrado de vivienda. |
| `score_holgura` | decimal | 0–100 | ESTIMADO | Subíndice calibrado de holgura global. |
| `indice_capacidad_global` | decimal | 0–100 | ESTIMADO | ICA = 0,30 vivienda + 0,30 (sanidad+educación)/2 + 0,25 conectividad + 0,15 holgura. |
| `precio_predicho_avm_m2` | decimal | €/m² | ESTIMADO | Precio de referencia del estimador M1 (no es tasación). |
| `gap_mercado_pct` | decimal | % | ESTIMADO | Diferencia entre precio y estimación M1. |
| `diagnostico_mercado` | texto | — | ESTIMADO | OPORTUNIDAD_ASEQUIBLE / PRECIO_EQUILIBRADO / ZONA_TENSIONADA. |
| `cluster_id` | entero | 0–3 | ESTIMADO | Cluster M5 asignado al municipio. |
| `arquetipo_codigo` | texto | — | ESTIMADO | Código del arquetipo M5. |
| `arquetipo_nombre` | texto | — | ESTIMADO | Nombre del arquetipo M5. |
| `observaciones_acogida` | texto | — | ESTIMADO | Comentario de acogida generado a partir de los datos. |

## Variables derivadas (calculadas a partir de las anteriores)

| Variable | Tipo | Unidad | Origen | Descripción |
|---|---|---|---|---|
| `tipologia` | texto | — | DERIVADO | RURAL <5.000; SEMIURBANO 5.000–20.000; URBANO >20.000. |
| `densidad` | decimal | hab/km² | DERIVADO | poblacion_actual / superficie_km2. |
| `medicos_x1000` | decimal | médicos/1.000 hab | DERIVADO | num_medicos_ap / población × 1.000. |
| `hab_por_medico` | decimal | hab/médico | DERIVADO | población / num_medicos_ap; umbral crítico 1.500. |
| `centros_salud_x10k` | decimal | centros/10.000 hab | DERIVADO | num_centros_salud / población × 10.000. |
| `ocupacion_escolar_pct` | decimal | % | DERIVADO | alumnos / plazas × 100; umbral crítico 95 %. |
| `tasa_holgura_escolar` | decimal | fracción 0–1 | DERIVADO | 1 − alumnos/plazas. |
| `centros_edu_x1000_alumnos` | decimal | centros/1.000 alumnos | DERIVADO | num_centros_educativos / alumnos × 1.000. |
| `paradas_x1000` | decimal | paradas/1.000 hab | DERIVADO | paradas / población × 1.000. |
| `vacias_x1000` | decimal | viviendas vacías/1.000 hab | DERIVADO | stock vacío / población × 1.000. |
| `suelo_m2_x_hab` | decimal | m²/hab | DERIVADO | suelo disponible / población. |
| `tasa_vivienda_vacia_pct` | decimal | % | DERIVADO | vivienda vacía / parque total × 100. |
| `rentabilidad_bruta_alquiler_pct` | decimal | % | DERIVADO | Alquiler anual / precio de compra × 100. |
| `personas_absorb_sanidad` | entero | personas | DERIVADO | max(0, médicos×1.500 − población). |
| `personas_absorb_educacion` | entero | personas | DERIVADO | max(0, (plazas×0,95 − alumnos)/0,17). |
| `personas_absorb_vivienda` | entero | personas | DERIVADO | 0,75×viviendas vacías + 0,00375×suelo (m²). |
| `personas_absorbibles_sin_colapso` | entero | personas | DERIVADO | min(sanidad, educación). |
| `personas_acogida_efectiva` | entero | personas | DERIVADO | min(sanidad, educación, vivienda). |
| `factor_limitante` | texto | — | DERIVADO | SANIDAD / EDUCACION / VIVIENDA (el mínimo de los tres). |
| `medicos_adicionales_necesarios` | entero | médicos | DERIVADO | Déficit para bajar de 1.500 hab/médico. |
| `plazas_escolares_adicionales_nec` | entero | plazas | DERIVADO | Déficit para bajar del 95 % de ocupación. |
| `coste_estimado_ampliacion_servicios` | decimal | € | DERIVADO | médicos×450.000 € + plazas×12.000 €. |
| `holgura_relativa_pct` | decimal | % | DERIVADO | Holgura relativa del factor limitante. |
| `nivel_idoneidad` | texto | — | DERIVADO | ALTA ≥60; MEDIA 40–59; BAJA <40 (o regla dura). |
| `ranking_ica` | entero | posición | DERIVADO | Orden del municipio por ICA (1 = mejor). |

## Variables proyectadas (modelo M3)

| Variable | Tipo | Unidad | Origen | Descripción |
|---|---|---|---|---|
| `poblacion_2027` | entero | habitantes | PROYECTADO | Proyección M3 a 2027 (escenario base). |
| `poblacion_2029` | entero | habitantes | PROYECTADO | Proyección M3 a 2029 (escenario base). |
| `poblacion_2031` | entero | habitantes | PROYECTADO | Proyección M3 a 2031 (escenario base). |
| `anio_estimado_saturacion` | entero | año | PROYECTADO | Año en que se satura el factor limitante sin inversión. |
| `alerta_planificacion` | texto | — | PROYECTADO | URGENTE_REFUERZO / ATENCION_MEDIA / ESTABLE. |

## Identificadores propios

| Variable | Tipo | Unidad | Origen | Descripción |
|---|---|---|---|---|
| `id_municipio` | entero | identificador | PROPIO | Clave interna del municipio en el panel (1–20). |

## Metadatos de procedencia y fechas

| Variable | Tipo | Unidad | Origen | Descripción |
|---|---|---|---|---|
| `fuente_datos` | texto | — | METADATO | Declaración textual de fuentes y calibración. |
| `fecha_carga` | texto | fecha ISO | METADATO | Fecha de captura/ carga del snapshot. |
| `fecha_referencia` | texto | fecha ISO | METADATO | Fecha de referencia del panel. |
| `fecha_calculo` | texto | fecha-hora ISO | METADATO | Timestamp real de ejecución del pipeline (varía en cada run). |
| `version_modelo` | texto | — | METADATO | Versión del cálculo del ICA (ICA-1.0.0). |
| `fecha_disponible` | texto | fecha ISO | METADATO | Fecha de disponibilidad de los datos (punto-en-tiempo). |
| `origen` | texto | — | METADATO | OBSERVADO+SIMULADO (procedencia mixta declarada). |
| `metodo` | texto | — | METADATO | PANEL_MUNICIPAL_INTEGRADO_F2. |
| `dataset_version` | texto | — | METADATO | v1.0.0-F2. |

## Notas de calidad conocidas

1. **`camas_hospitalarias_cercanas` vs `camas_hospital`**: son dos columnas heredadas del mismo concepto y difieren en 19 de 20 municipios (hasta 140 camas). No entra en el ICA ni en los modelos; se recomienda conciliar antes de usarlas en una decisión.
2. **`arquetipo_nombre` del panel** usa nombres de visualización; `clustering.json` (salida vigente de M5) usa otra nomenclatura. No afecta al ICA; conviene unificarlo.
3. **Proyecciones**: el panel trae `poblacion_2027/2029/2031`; `metrics.json` de M3 resume 2030/2035. Son horizontes distintos del mismo modelo; no deben mezclarse en una misma frase.
4. **`fecha_calculo`** es el timestamp real de ejecución: cambia en cada run y no forma parte del contenido del dataset.
5. **`codigo_ine`** se entrega como entero de 5 dígitos (28xxx); no tiene ceros a la izquierda que se puedan perder.
