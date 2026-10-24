# Matriz de Procedencia y Linaje por Variable (Fase F1 / F2)
## Proyecto LoDCORE Madrid — II Datathon 2026

> **Regla de transparencia**: solo se presentan como `OBSERVADO` las variables
> que el pipeline F1 descarga de una fuente oficial. El resto son referencias
> curadas, estimaciones, calibraciones sintéticas o variables derivadas, y así
> se declara. Ninguna variable sin conector oficial se atribuye a IGN, SERMAS,
> CRTM, CNMC, Catastro o Catálogo Nacional de Hospitales.

---

### 1. Variables ingestadas de fuentes oficiales en F1

| Variable | Origen | ¿Ingerida en F1? | Fuente / método |
|---|---|---|---|
| `codigo_ine` | **OBSERVADO** | Sí | INE; código oficial de 5 dígitos (`28xxx`) |
| `nombre` | **OBSERVADO** | Sí | INE; nomenclátor oficial |
| `poblacion_actual` | **OBSERVADO** | Sí | INE; Padrón Municipal continuo 2025, tabla 2881 |
| `anio_padron` | **OBSERVADO** | Sí | INE; año de referencia del padrón |
| `num_centros_salud` | **OBSERVADO** | Sí | CKAN CAM; centros de salud + consultorios locales |
| `num_centros_educativos` | **OBSERVADO** | Sí | CKAN CAM; enseñanza reglada en situación `ALTA` |

---

### 2. Variables de referencia curada (no ingestadas en F1)

| Variable | Origen | ¿Ingerida en F1? | Método / nota |
|---|---|---|---|
| `comarca` | **REFERENCIA CURADA** | No | División comarcal de planificación de la CAM; valor fijo del piloto |
| `tipologia` | **DERIVADO** | No | Umbral de población: RURAL <5.000; SEMIURBANO 5.000–20.000; URBANO >20.000 |
| `superficie_km2`, `latitud`, `longitud` | **REFERENCIA CURADA** | No | Cartografía de referencia; no se descarga de IGN en este MVP |
| `hospital_referencia`, `camas_hospitalarias_cercanas` | **REFERENCIA CURADA** | No | Catálogo de referencia; no se descarga de SERMAS en este MVP |
| `paradas_transporte_publico` | **REFERENCIA CURADA** | No | Red de transporte de referencia; no se descarga de CRTM en este MVP |
| `restriccion_ambiental` | **REFERENCIA CURADA** | No | Espacios protegidos de referencia; no se descarga de Red Natura 2000 en este MVP |
| `tiempo_medio_madrid_minutos` | **ESTIMADO** | No | Heurística sobre la red de carreteras; vehículo privado en hora valle |
| `cobertura_fibra_pct` | **ESTIMADO** | No | Referencia CNMC; no ingestada en este MVP |

---

### 3. Variables calibradas sintéticamente (`seed=2026`)

| Variable | Origen | ¿Ingerida en F1? | Método / nota |
|---|---|---|---|
| `num_medicos_ap` | **SIMULADO** | No | Generador calibrado por tipología y cupos medios del SERMAS |
| `num_plazas_escolares` | **SIMULADO** | No | Generador calibrado según ratios de escolarización comarcales |
| `num_alumnos_matriculados` | **SIMULADO** | No | Generador calibrado por perfil demográfico |
| `num_viviendas_totales_est` | **SIMULADO** | No | Estimación basada en Catastro y tamaño de hogar |
| `stock_vivienda_vacia_est` | **SIMULADO** | No | Calibración municipal del parque desocupado movilizable |
| `suelo_urbano_disponible_m2` | **SIMULADO** | No | Calibración del suelo vacante disponible |
| `precio_m2_compra`, `precio_m2_alquiler` | **SIMULADO** | No | Calibración de precios de mercado (`seed=2026`) |

---

### 4. Variables derivadas

Se calculan a partir de las anteriores y **heredan la fuente más débil**; no se
presentan como observadas:

- `densidad`, `medicos_x1000`, `hab_por_medico`, `centros_salud_x10k`
- `ocupacion_escolar_pct`, `tasa_holgura_escolar`, `centros_edu_x1000_alumnos`
- `paradas_x1000`, `vacias_x1000`, `suelo_m2_x_hab`, `tasa_vivienda_vacia_pct`
- `rentabilidad_bruta_alquiler_pct`, `holgura_relativa_pct`
- `personas_absorb_sanidad`, `personas_absorb_educacion`, `personas_absorb_vivienda`
- `personas_absorbibles_sin_colapso`, `personas_acogida_efectiva`
- `factor_limitante`, `medicos_adicionales_necesarios`
- `plazas_escolares_adicionales_nec`, `coste_estimado_ampliacion_servicios`

---

### 5. Scores, ICA y salidas de modelos

| Variable | Origen | Método / nota |
|---|---|---|
| `score_sanidad`, `score_educacion`, `score_servicios`, `score_conectividad`, `score_vivienda`, `score_holgura` | **ESTIMADO** | Subíndices Min-Max con winsorización p5–p95; calibración F2 |
| `indice_capacidad_global` (ICA) | **ESTIMADO** | Combinación determinista de subíndices + reglas duras no compensatorias |
| `nivel_idoneidad`, `ranking_ica` | **DERIVADO** | Semáforo tripartito (ALTA, MEDIA, BAJA) y orden relativo |
| `cluster_id`, `arquetipo_codigo`, `arquetipo_nombre` | **ESTIMADO** | Salida del clustering M5 |
| `precio_predicho_avm_m2`, `gap_mercado_pct`, `diagnostico_mercado` | **ESTIMADO** | Salida del modelo M1 (estimador de referencia, no tasación comercial) |
| `poblacion_2027`, `poblacion_2029`, `poblacion_2031`, `anio_estimado_saturacion` | **PROYECTADO** | Proyección demográfica M3 |
| Textos descriptivos (`*_detalle`, `observaciones_acogida`, etc.) | **ESTIMADO** | Redacción asistida a partir de los datos anteriores |

**Importante**: los `score_*` y el ICA son la base calibrada del MVP y **no se
recalculan automáticamente** al actualizar los recuentos oficiales de centros en
F1. M2 sí recalcula sus propios subíndices PCA a partir de los ratios. Esta
distinción debe explicarse si el jurado pregunta por la evolución de los scores.

---

### 6. Declaración de fila en el panel

El panel combina variables observadas y calibradas, por lo que cada registro
declara:

```text
origen = "OBSERVADO+SIMULADO"
fuente_datos = "Población: INE Padrón continuo 2025 (tabla 2881 API) |
                Equipamientos: CKAN CAM (Sanidad/Educación en ALTA) |
                Dotación servicios, vivienda y precios: SINTÉTICO calibrado (seed=2026)"
```

En resumen: **solo la población y los recuentos de centros son datos oficiales
observados**. Todo lo demás es referencia curada, estimación, calibración
sintética, variable derivada o salida de modelo, y se declara como tal.
