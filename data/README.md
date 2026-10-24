# `data/` — estructura del dataset

Este directorio tiene **dos cosas**: las descargas originales y el dataset.
Todo lo demás que aparezca aquí es una copia y debe eliminarse.

## Contenido

```text
data/
├── raw/                                      # descargas originales (no editar)
│   ├── ine/ine_padron_2881_snapshot_*.json   # padrón municipal (INE)
│   └── ckan/ckan_madrid_*_snapshot_*.json    # sanidad y educación (CKAN CAM)
├── validated/
│   └── municipios_panel_validado.csv         # EL DATASET (20 municipios × 88 columnas)
└── output/
    └── municipios_comunidad_madrid_completo.json   # el mismo panel serializado (payload)
```

## Regla única

**El dataset canónico es `validated/municipios_panel_validado.csv`.**
Es lo que leen los tests, los cinco modelos M1–M5 y la API FastAPI.
Si dudas, usa ese fichero y olvida el resto.

## Quién escribe qué

| Fichero | Lo escribe | Lo lee |
|---|---|---|
| `raw/**` | `src/lodcore/ingest/ine_padron.py`, `ckan_madrid.py` | `pipeline_ingesta.py` |
| `validated/*.csv` | `pipeline_ingesta.py` y `scripts/run_all_models_n1_n2_n3.py` | tests, M1–M5, FastAPI |
| `output/*.json` | `pipeline_ingesta.py` | `scripts/run_all_models_n1_n2_n3.py` |

## Qué contiene el panel (importante)

De las 88 columnas, solo **4 son datos observados**:

- `poblacion_actual`, `anio_padron` → INE padrón 2881
- `num_centros_salud` → CKAN sanidad (centros en ALTA)
- `num_centros_educativos` → CKAN educación (reglada en ALTA)

El resto — precios, vivienda, suelo, fibra, transporte, camas, plazas, scores,
arquetipos y proyecciones — son **valores sintéticos calibrados con `seed=2026`**.
Por eso la columna `origen` vale `OBSERVADO+SIMULADO`, nunca `OBSERVADO`.
La columna `fuente_datos` de cada fila lo declara explícitamente.

## Carpetas eliminadas

- `data/processed/` y `data/output/municipios_completo_ml.csv`: eran copias
  byte a byte del panel validado. Se retiraron para no tener 4 fuentes de verdad.
- `data/output/_legado/`: prototipo anterior; dos de sus ficheros contradecían
  los datos vigentes.

`docs/estructura.md` y `fases.md` describen el plan objetivo (10 fuentes de datos,
41 municipios, carpetas `interim/` y `external/`). **Ese plan no está implementado**:
este README refleja lo que existe realmente.

## Limitación conocida

`validated/*.csv` y `output/*.json` no son perfectamente idénticos: difieren en
la precisión decimal de `paradas_x1000`, `vacias_x1000` y `suelo_m2_x_hab`.
Ejecutar `scripts/run_all_models_n1_n2_n3.py` reescribe el CSV a partir del JSON
y por tanto redondea esas tres columnas. Es un efecto secundario preexistente.
