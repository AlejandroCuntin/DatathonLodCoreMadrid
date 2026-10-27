# M6 · Predicción de tendencia de población

Predicción **simple de tendencias**: a partir de la evolución histórica de la población de cada municipio, el modelo ONNX
estima hacia dónde va su población en un año objetivo (`?target_year=2030`, hasta 2040).

> No es el simulador. No calcula el ICA, no modela inversiones ni cambios en sanidad, educación o vivienda, y no explica
> causas: extrapola la tendencia observada. El ICA y los escenarios con parámetros son una fase posterior (simulador completo).

## Cómo se usa el resultado

```
h                  = año_objetivo - anio_origen            (1 .. 15)
población_objetivo = población_actual * EXP( PREDICCION(m6_proyeccion USING ln_pob, g1, g3, g5, vol5, h) )
banda 95 %         = población_actual * EXP( predicción + [lo_h, hi_h] )     -- bandas_residuo_log_95 del metadata
```

Entradas (en este orden, definidas en `oracle/onnx/m6_proyeccion.metadata.json`):
`ln_pob` (log de la población en el año de origen), `g1` (log-crecimiento del último año), `g3` y `g5` (crecimiento medio
anual a 3 y 5 años), `vol5` (desviación típica de los 5 últimos crecimientos anuales) y `h`.
Los valores actuales de cada municipio están en `data/validated/m6_entradas_actuales.csv`.

## Pipeline

```powershell
.\scripts\run_pipeline_proyeccion.ps1                 # descarga 30 años del INE, valida, entrena y genera el ONNX
.\scripts\run_pipeline_proyeccion.ps1 -SinDescarga    # reutiliza data\raw\AAAA_raw_ine_padron.csv
.\scripts\run_pipeline_proyeccion.ps1 -DesdeSnapshot data\raw\ine\ine_padron_2881_30y_snapshot_AAAAMMDD.json   # sin red
```

| Paso | Código | Resultado |
|---|---|---|
| Descarga INE (tabla 2881) | `src/lodcore/ingest/descarga_historica.py` | `data/raw/AAAA_raw_ine_padron.csv` (uno por año) + snapshot JSON en `data/raw/ine/` |
| Validación y panel | `src/lodcore/data/panel_proyeccion.py` | puertas de calidad; pares (municipio, año de origen, h) |
| Entrenamiento, backtest, bandas, ONNX | `src/lodcore/models/m6_proyeccion/train.py` | `oracle/onnx/m6_proyeccion.onnx` y `.metadata.json`, `data/output/m6_metricas.json` |
| Orquestación | `scripts/run_pipeline_proyeccion.py` / `.ps1` | códigos de salida 0, 1 (datos), 2 (dependencias), 3 (otro) |
| Pruebas | `tests/unit/test_m6_proyeccion.py` | sin red ni Oracle |

El INE no publica el Padrón de 1997: si la serie tiene huecos, el entrenamiento usa solo el tramo contiguo más reciente
(1998-2025) y avisa; no se inventan los años que faltan.

Si el parseo del INE falla, el error lista los nombres de las series recibidas; `descarga_historica.py --inspeccionar <json>`
muestra lo mismo sin repetir la descarga.

## Parámetros (añadir a `params.yaml`, opcional)

```yaml
m6_proyeccion:
  h_max: 15
  n_estimators: 300
  max_depth: 3
  learning_rate: 0.05
  subsample: 0.8
  seed: 2026
  anios_backtest: 5
  min_anios: 12
  min_municipios: 100
  target_opset: 15   # igual que el que use src/lodcore/models/base.py
```

## Qué es real y qué no (regla de honestidad)

- Se entrena con la serie histórica de población del Padrón de **todos** los municipios de la tabla (no solo los 20 del panel).
- **Es una tendencia, no una simulación:** supone que los factores que movieron la población en el pasado siguen
  actuando igual. No incorpora inversiones, políticas ni cambios en los servicios.
- El backtest compara el modelo con "sin cambio" y con la extrapolación geométrica a 5 años (la lógica de M3).
  Si no mejora a CAGR5, el pipeline lo avisa y debe declararse.
- `r2_cv_oof` deja municipios fuera pero **no es temporal**; la métrica honesta es el MAPE del backtest.
- Las bandas del 95 % salen de los residuos fuera de muestra por horizonte.
- Procedencia del resultado: `origen = PROYECTADO`, `metodo` y `dataset_version` en el metadata.
