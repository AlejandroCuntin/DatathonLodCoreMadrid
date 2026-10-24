# Matriz de Procedencia y Linaje por Variable (Fase F1 / F2)
## Proyecto LoDCORE Madrid • II Datathon 2026

> **Regla de Metrología y Transparencia**: Para garantizar el cumplimiento de las bases del Datathon y resistir la auditoría del jurado (UC3M / Comunidad de Madrid), ninguna variable se presenta como dato real sin respaldo oficial. Las variables sintéticas de calibración se declaran explícitamente.

---

### 1. Taxonomía de Linaje (Nivel de Columna)

| Variable en el Panel | Tipo de Origen | Fuente Oficial / Método | Descripción / Justificación |
|---|---|---|---|
| `codigo_ine` | **OBSERVADO** | INE (Instituto Nacional de Estadística) | Código oficial de 5 dígitos (`28xxx`). |
| `nombre` | **OBSERVADO** | INE / Nomenclátor oficial de la CAM | Toponimia oficial normalizada. |
| `comarca` | **OBSERVADO** | Comunidad de Madrid (D.G. Reequilibrio Territorial) | División comarcal oficial de la CAM (8 comarcas piloto). |
| `tipologia` | **OBSERVADO** | Clasificación por umbrales de población | RURAL ($<5.000$), SEMIURBANO ($5.000-20.000$), URBANO ($>20.000$). |
| `poblacion_actual` | **OBSERVADO** | INE Padrón Municipal continuo (1-ene-2025) | API JSON oficial tabla 2881 (`servicios.ine.es/wstempus`). |
| `anio_padron` | **OBSERVADO** | INE (Año 2025) | Año oficial de referencia del dato padronal. |
| `superficie_km2` | **OBSERVADO** | IGN (Instituto Geográfico Nacional) | Medición cartográfica oficial del término municipal. |
| `latitud`, `longitud` | **OBSERVADO** | IGN / CNIG | Coordenadas WGS84 del núcleo urbano principal. |
| `tiempo_medio_madrid_minutos` | **ESTIMADO** | Heurística sobre red de carreteras principales | Tiempo medio estimado en vehículo privado en hora valle a Madrid centro. |
| `precio_m2_compra`, `precio_m2_alquiler` | **ESTIMADO** | Portales inmobiliarios y estadísticas de referencia | Precio de mercado aproximado por m² de vivienda en el municipio. |
| `hospital_referencia` | **OBSERVADO** | SERMAS (Servicio Madrileño de Salud) | Hospital público de la red asistencial asignado al área sanitaria. |
| `camas_hospitalarias_cercanas` | **OBSERVADO** | Catálogo Nacional de Hospitales (Ministerio de Sanidad) | Número de camas instaladas en el hospital de referencia. |
| `restriccion_ambiental` | **OBSERVADO** | Red Natura 2000 / Espacios Naturales Protegidos CAM | Indicador binario ('S'/'N') de afección a parques regionales o cuencas protegidas. |
| `num_centros_salud` | **OBSERVADO** | CKAN Comunidad de Madrid (Sanidad) | Recuento oficial de equipamientos de Atención Primaria (Centros de Salud + Consultorios Locales). |
| `num_medicos_ap` | **SIMULADO** | Generador calibrado (semilla 2026) | Estimación sintética calibrada por tipología según cupos medios del SERMAS. |
| `num_plazas_escolares` | **SIMULADO** | Generador calibrado (semilla 2026) | Estimación sintética calibrada según ratios de escolarización comarcales. |
| `num_alumnos_matriculados` | **SIMULADO** | Generador calibrado (semilla 2026) | Estimación sintética calibrada por perfil demográfico. |
| `num_centros_educativos` | **OBSERVADO** | CKAN Comunidad de Madrid (Educación) | Directorio oficial de centros de enseñanza escolar reglada en situación de ALTA. |
| `paradas_transporte_publico` | **OBSERVADO** | CRTM (Consorcio Regional de Transportes de Madrid) | Red de paradas de autobús interurbano y estaciones de Cercanías Renfe. |
| `cobertura_fibra_pct` | **ESTIMADO** | CNMC / Ministerio de Transformación Digital | Porcentaje estimado de cobertura FTTH en el municipio. |
| `num_viviendas_totales_est` | **SIMULADO** | Estimación basada en Catastro y tamaño de hogar | Parque estimado de viviendas residenciales. |
| `stock_vivienda_vacia_est` | **SIMULADO** | Censo de Vivienda INE / Calibración municipal | Estimación del parque desocupado movilizable a medio plazo. |
| `suelo_urbano_disponible_m2` | **ESTIMADO** | SIT Madrid / Planeamiento municipal | Superficie de suelo vacante clasificado como urbano o urbanizable residencial. |
| `densidad` | **OBSERVADO** | Calculado: `poblacion / superficie` | Densidad demográfica en hab/km². |
| `medicos_x1000`, `hab_por_medico` | **SIMULADO** | Ratios sanitarios derivados | Ratios auditados contra el umbral crítico ($1.500\text{ hab/médico}$). |
| `ocupacion_escolar_pct` | **SIMULADO** | Ratio educativo derivado | Ratio auditado contra el umbral crítico ($95\%$). |
| `score_sanidad`, `score_educacion` | **ESTIMADO** | Sub-índices Min-Max con Winsorización p5-p95 | Escala relativa 0-100 para la comparación intermunicipal. |
| `score_conectividad`, `score_vivienda` | **ESTIMADO** | Sub-índices Min-Max con Winsorización p5-p95 | Escala relativa 0-100 para la comparación intermunicipal. |
| `indice_capacidad_global` (ICA) | **ESTIMADO** | Combinación determinista de sub-índices + reglas duras | Puntuación sintética de idoneidad con salvaguarda no compensatoria. |
| `nivel_idoneidad` | **ESTIMADO** | Semáforo tripartito (ALTA, MEDIA, BAJA) | Clasificación de planificación territorial. |

---

### 2. Declaración de Nivel de Fila en el Panel (`origen`)

Dado que el panel municipal combina **datos reales observados** (Población 2025, centros sanitarios y colegios oficiales de la CAM, cartografía IGN) con **variables calibradas sintéticamente** (médicos asignados, plazas escolares y viviendas vacías), la columna `origen` de cada registro se define como:

```text
origen = "OBSERVADO+SIMULADO"
```

Esta etiqueta compuesta garantiza ante el jurado que no se está ocultando la existencia de variables calibradas, preservando la máxima integridad académica y técnica.
