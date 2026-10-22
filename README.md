# ICA · Índice de Capacidad de Acogida — II Datathon LoDCOREMadrid

Herramienta de diagnóstico para identificar qué municipios de la Comunidad de Madrid
de **menos de 50.000 habitantes** pueden acoger nueva población sin saturar sus
servicios públicos.

## Estructura

```
DATATHON/
├── requirements.txt
├── etl/
│   └── etl_pipeline.py          # Ingesta + generador sintético + algoritmo ICA + exportadores
├── sql/
│   ├── 01_ddl_schema.sql        # DDL Oracle (tablas, PK/FK, CHECK, índices, comentarios)
│   └── 02_dml_inserts.sql       # GENERADO por el ETL (INSERT Oracle)
└── data/
    ├── raw/                     # (opcional) CSV con datos reales para --entrada-csv
    └── output/                  # GENERADO: municipios_ica.csv/.json + 1 CSV por tabla
```

## Ejecución

```powershell
pip install -r requirements.txt
python etl/etl_pipeline.py                 # INE online (tabla 2881) con fallback offline
python etl/etl_pipeline.py --fuente offline
python etl/etl_pipeline.py --entrada-csv data/raw/datos_reales.csv
```

Después, en Oracle (SQL Developer, SQLcl o APEX › SQL Workshop › SQL Scripts):

1. `sql/01_ddl_schema.sql`
2. `sql/02_dml_inserts.sql`

> SQLcl/SQL*Plus: usar `NLS_LANG=SPANISH_SPAIN.AL32UTF8` para que las tildes se carguen bien.

## Procedencia de los datos

| Bloque | Origen | Estado |
|---|---|---|
| Población | INE, Padrón 1-ene-2025, tabla 2881 (API JSON) | **Real** |
| Código INE, comarca, superficie, coordenadas | Referencia embebida (aprox.) | Sustituir por IGN / NOMECALLES |
| Tiempo a Madrid, precios €/m² | Referencia embebida (aprox.) | Sustituir por CRTM / portales / MITMA |
| Hospital de referencia y camas | Referencia embebida (aprox.) | Sustituir por Catálogo Nacional de Hospitales |
| Médicos AP, centros, plazas/alumnos, paradas, fibra, viviendas, suelo | **Sintético** calibrado por tipología (seed 2026) | Sustituir por SERMAS, Educación, CRTM, CNMC, Censo 2021 |

Para sustituir datos sintéticos por reales, crea un CSV con `codigo_ine` + cualquiera de las
columnas de `COLS_SOBRESCRIBIBLES` (en `etl_pipeline.py`) y pásalo con `--entrada-csv`.
El campo `MUNICIPIOS.FUENTE_DATOS` registra en cada fila qué parte es real y qué parte es sintética.

## Modelo ICA (v1.0.0)

$$ICA = 0{,}30\,V + 0{,}30\,\tfrac{S+E}{2} + 0{,}25\,C + 0{,}15\,H$$

- Indicadores per cápita → winsorización p5–p95 → Min-Max 0–100 (invertido si «menos es mejor»).
- **Umbrales de absorción** (habitantes adicionales):
  - Sanidad = médicos × 1.500 − población
  - Educación = (plazas × 0,95 − alumnos) / 0,17
  - Vivienda = (vacías × 0,30 + viviendas edificables en suelo vacante) × 2,5
  - *Sin colapso* = mín(Sanidad, Educación) · *Efectiva* = mín(las tres) · *factor limitante* = argmín
- **Coste de ampliación** = médicos adicionales × 450.000 € + plazas adicionales × 12.000 €
  para ocupar todo el potencial residencial.

Todos los parámetros están en `ParametrosModelo` y se cargan en la tabla `PARAMETROS_MODELO`.
