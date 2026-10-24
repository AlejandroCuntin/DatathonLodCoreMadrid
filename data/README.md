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
| `raw/**` | `ingest/ine_padron.py`, `ckan_madrid.py`, `ckan_vivienda_migracion.py` | `pipeline_ingesta.py`, `pipeline_datos_reales.py` |
| `validated/*.csv` | `pipeline_ingesta.py`, `pipeline_datos_reales.py` y `scripts/run_all_models_n1_n2_n3.py` | tests, M1–M5, FastAPI |
| `output/*.json` | `pipeline_ingesta.py`, `pipeline_datos_reales.py` | `scripts/run_all_models_n1_n2_n3.py` |

## Qué contiene el panel (importante)

De las 92 columnas, **8 son datos observados** (Etapa 1, v1.1.0-F2):

- `poblacion_actual`, `anio_padron` → INE padrón 2881
- `num_centros_salud` → CKAN sanidad (centros en ALTA)
- `num_centros_educativos` → CKAN educación (reglada en ALTA)
- `valor_catastral_residencial_eur_m2`, `anio_valor_catastral` → DG Catastro vía CKAN CAM (2026)
- `migracion_neta_externa` → INE Variaciones Residenciales vía CKAN CAM (media 2017-2021; solo flujos externos)
- `crecimiento_pob_pct_2020_2025` → INE padrón 2881 (nult=6)

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

## Limitaciones conocidas (actualizado tras la Etapa 1)

- La antigua divergencia de precisión entre el CSV y el JSON en `paradas_x1000`,
  `vacias_x1000` y `suelo_m2_x_hab` **está resuelta**: la Etapa 1 regeneró ambos
  desde el mismo DataFrame y ahora coinciden columna a columna.
- `migracion_neta_externa` no incluye flujos intra-Comunidad de Madrid (el dataset
  oficial los publica agregados sin separar dirección) ni salidas al extranjero.
- `precio_m2_compra` sigue siendo calibrado: no existe fuente pública y gratuita
  de precios de mercado por municipio. El valor catastral real (2026) se añade
  como columna independiente en vez de disfrazar el precio calibrado.
