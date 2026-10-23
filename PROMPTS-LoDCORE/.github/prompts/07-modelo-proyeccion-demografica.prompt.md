---
description: 'Construye el Modelo 3: proyección demográfica a 5 y 10 años con SARIMAX/Prophet, exógenas y bandas de incertidumbre'
agent: 'agent'
tools: ['search/codebase', 'edit/editFiles', 'runCommands']
argument-hint: '[horizonte=5|10|ambos]'
---

# Modelo 3 — Proyección Demográfica con bandas de incertidumbre

## Misión

Proyectar la **población de cada municipio a 5 y 10 años** con **SARIMAX** (o Prophet)
incorporando **variables exógenas** (precio de la vivienda en Madrid capital, presupuesto de
inversión en infraestructuras del municipio, saldo migratorio, tendencia regional), y producir
**bandas de incertidumbre cuantificadas** (80 % y 95 %).

Requisito del proyecto: *"la capacidad predictiva de los modelos de series temporales en proyectar
el futuro a partir del pasado"* y que *"cambios bruscos como la aprobación de un gran proyecto
de vivienda no alteren la trayectoria previa"*.

## Alcance y precondiciones

- Precondición: serie histórica del Padrón Municipal (INE/IECM) por municipio, pirámide de edad,
  saldos migratorios, proyecciones oficiales.
- Alcance: `src/lodcore/models/m3_demography/`.
- Restricción dura: **41 municipios × ~10-20 años** ⇒ series muy cortas. SARIMAX con
  estacionalidad anual `(1,1,1,12)` puede no ser identificable en series de 10 puntos.

## Inputs

- `${input:horizonte}` — `5` | `10` | `ambos` (por defecto `ambos`).

## Workflow

### 1. Diagnóstico de cada serie (OBLIGATORIO antes de modelar)
Para cada municipio, con la serie real:
- Longitud, frecuencia anual, valores faltantes, saltos administrativos (cambios de padrón, fusiones).
- **Test de estacionariedad**: ADF y KPSS. Reporta ambos (ADF solo puede ser poco sensible).
- **ACF y PACF** de la serie y de su primera diferencia.
- **Descomposición**: tendencia, estacionalidad, residuo.
- **Outliers**: el Padrón tiene revisiones (el INE revisa cifras). Marca los saltos grandes y
  decide: ¿son reales, o artefacto de revisión? Esto **cambia la proyección**.

**Diagnóstico de identificabilidad** (decisión clave):
| Longitud serie | Veredicto |
|---|---|
| < 12 años | No modelar SARIMAX. Usar un modelo **estructural** (drift + regresión sobre exógenas) o shrinkage a la tendencia regional. |
| 12–19 años | Solo SARIMAX **sin** componente estacional (`order=(p,d,q)`, `seasonal_order=(0,0,0,0)`). |
| ≥ 20 años | SARIMAX con estacionalidad anual `(0,1,1,12)` admisible. |

### 2. Modelo de referencia: *drift + región* (OBLIGATORIO como baseline)
El benchmark más importante no es ARIMA, es:
```
pob_hat(t+h) = pob(t) + h * (tasa_media_crecimiento_últimos_k_años) * ajuste_regional
```
con `k` = 3, 5 y 10 años. Si el SARIMAX no bate a este baseline, **no lo uses**: la simplicity
gana en auditoría. Reporta también el **Random Walk with Drift** puro.

### 3. SARIMAX con exógenas
- **Exógenas (elegidas por disponibilidad y causalidad plausible):**
  - `precio_vivienda_madrid_capital` (efecto demigration/atracción regional).
  - `inversion_infraestructuras_per_capita` del municipio (la variable que la propia app simula).
  - `saldo_migratorio` (nivel ymedia móvil).
  - `tasa_crecimiento_comunidad` (efecto regional).
  - `tasa_desempleo_comarca` (atractividad económica).
  - `poblacion_65_mas_share` (efecto generacional sobre natalidad).
- **Crítico**: las exógenas futuras **no se conocen**. Para una proyección a 5-10 años debes
  **explicitar los escenarios**:
  - *Escenario base*: exógenas según trayectoria media reciente.
  - *Escenario alto*: exógenas favorables (más inversión, precios más altos).
  - *Escenario bajo*: exógenas desfavorables.
  - Proyecta las exógenas con un modelo simple y **documenta el supuesto**.
- **Riesgo de sobreajuste**: con 41 municipios y series cortas, SARIMAX con exógenas puede
  tener más parámetros que observaciones. Regulariza: `enforce_stationarity=False`,
  `enforce_invertibility=False`, y limita `order` a ≤ 2.

### 4. Prophet como contraste
Implementa Prophet **solo como benchmark**: es más robusto a seasonality y missing, pero con
10-15 observaciones anuales es claramente sobre-parametrizado (sus parámetros por defecto
asumen seasonalidad semanal). Si lo incluyes, desactiva `weekly_seasonality` y
`daily_seasonality`, y reporta el resultado **con bandages**. Conclude si aporta o no.

### 5. Bandas de incertidumbre (requisito)
- **Bandas analíticas** de SARIMAX: `get_forecast().conf_int()` al 80 % y 95 %.
- **Bandas empíricas (preferibles)**: **bootstrap por bloques** sobre los residuos, o
  **simulación bootstrap de la serie completa** (resamplear bloques de residuos y re-estimar
  el modelo B=500 veces) → percentiles 2,5 / 97,5. Es la forma más honesta con n pequeño.
- **Backtesting con cobertura**: para cada municipio, simula el origen del pronóstico (origen
  en t, horizonte h) y mide la **cobertura empírica** del intervalo. Si la banda al 95 %
  cubre el 70 %, la banda es **demasiado estrecha** y miente. Ajusta (esto se llama
  "calibración de bandas") y repórtalo.
- **Métrica principal: WAPE y MAE por horizonte** (1, 3, 5, 10 años).

### 6. Robustez ante "shocks" (requisito explícito del documento)
Test de resiliencia: simula que en `t0` se aprueba un gran proyecto de vivienda
(+X población en `t0+2`). Comprueba:
- ¿El SARIMAX **absorbe** el shock en la trayectoria (aparece como nivel, no como cambio
  estructural permanente)?
- ¿El intervalo se ensancha lo suficiente?
Reporta el resultado: es un **resultado de investigación** del proyecto, no un detalle.

### 7. Validación
- Rolling-origin backtesting (origen en t, predice t+1..t+h) para cada municipio.
- Compara con baseline drift y con la **proyección oficial** del INE/IECM (si existe):
  reporta el error de la proyección oficial como referencia Honesta.
- Reporta por **comarca**: ¿el error es homogéneo o concentrado en municipios pequeños?

### 8. Salida al panel
Variables de salida por municipio × año × escenario:
`poblacion_proy_<h>_base`, `..._alto`, `..._bajo`,
`poblacion_proy_<h>_lo80`, `..._hi80`, `..._lo95`, `..._hi95`,
`tasa_crecimiento_anual_<h>`, `metodo` (p. ej. `"SARIMAX(1,1,1) exogenas=5, B=500"`),
`origen='PROYECTADO'`.

## Output Expectations

1. `src/lodcore/models/m3_demography/` (`diagnose.py`, `sarimax.py`, `bootstrap.py`,
   `backtest.py`, `scenarios.py`, `model_card.md`).
2. `reports/m3_demography.md`:
```
# M3 — Proyección demográfica
## Diagnóstico por municipio (longitud, ADF, KPSS, ACF, outliers) + veredicto de identificabilidad
## Baseline drift vs SARIMAX vs Prophet (MASE y WAPE por horizonte)
## Bandas: cobertura empírica por horizonte y por municipio (objetivo 95%)
## Escenarios alto/base/bajo: tabla de población 2030/2035 por municipio
## Test de shock (proyecto de vivienda): comportamiento del modelo
## Comparación con proyección oficial INE/IECM
## Errores por comarca
## Municipios con banda > ±X%: <lista y explicación>
```
3. `model_card.md` de M3 con supuestos de exógenas_future y su justificación.

## Quality Assurance

- [ ] He ejecutado ADF **y** KPSS en todas las series.
- [ ] He justificado, municipio a municipio, si SARIMAX es identificable.
- [ ] El baseline drift está implementado y comparado.
- [ ] Las bandas tienen **cobertura empírica verificada**, no solo la fórmula analítica.
- [ ] Los escenarios de exógenas están **explícitamente nombrados** y documentados.
- [ ] He probado el comportamiento ante un shock de proyecto de vivienda.
- [ ] Todas las salidas llevan `origen='PROYECTADO'` y `metodo` descriptivo.
- [ ] Ningún intervalo se presenta como "certainty" en el texto de cara al usuario.
