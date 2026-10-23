---
description: 'Construye el Modelo 1 (AVM) con Random Forest / LightGBM, esfuerzo financiero familiar y bandas de incertidumbre'
agent: 'agent'
tools: ['search/codebase', 'edit/editFiles', 'runCommands']
argument-hint: '[modo=compra|alquiler|ambos]'
---

# Modelo 1 — AVM (Automated Valuation Model) y Asequibilidad

## Misión

Implementar el **Módulo AVM**: estimar el precio justo por m² (compra y alquiler) y la **tasa de
esfuerzo financiero familiar** en municipios con baja densidad de oferta comercial, con
**bandas de incertidumbre al 95 %** y validación temporal + agrupada por municipio.

El objetivo no es "acertar el precio": es que un ciudadano vea *cuánto le va a costar vivir ahí*
y que lasdreamFish the app lo muestre con honestidad sobre su precisión.

## Alcance y precondiciones

- Precondición: dataset con precio por m² y variables de contexto (Catastro, población, servicios,
  conectividad, presupuesto municipal); `AGENTS.md` leído.
- Alcance: `src/lodcore/models/m1_avm/` (entrenamiento, features, conformal, métricas).
- Fuera de alcance: M2–M5 y la capa Oracle.

## Inputs

- `${input:modo}` — `compra` | `alquiler` | `ambos` (por defecto `ambos`).

## Workflow

### 1. Features (no las inventes: derívalas del dataset)
- **Catastro**: valor catastral, superficie construida/parcela, año de construcción, uso
  (residencial/…), numéro de isi, tipo de suelo, distancia al centroide del municipio.
- **Contexto municipal**: población, densidad, edad media, tasa de variación demográfica.
- **Conectividad** (de M2, si ya existe; si no, marca la dependencia): tiempo a empleo/hospital
  por transporte público y privado, nº de paradas.
- **Servicios**: hab/médico, plazas de colegio, ratio de plazas de secundaria, zonas verdes per cápita.
- **Oferta**: nº de inmuebles en venta/renta, nº de anuncios, **meses desde la fecha del anuncio**
  (clave para modelos de *asking price*: el precioasked sube con el tiempo en el mercado).
- **Presupuesto**: inversión per cápita, deuda municipal.

**Regla dura**: toda feature debe existir en el momento de *scoring* para un municipio nuevo.

**Plantilla de features probada** (Rico-Juan & Taltavull 2021, Tabla 1, 52 variables): el bloque de
**infraestructura y calidad de servicios** es el que más pesa en municipios rurales de baja
oferta — edad del barrio, tipo urbano, **crecimiento poblacional**, densidad, **nivel de ingresos**,
**calidad de la red viaria**, **tipo y calidad del agua**, **tipo y calidad del alcantarillado**,
**tipo y calidad de la iluminación**, **calidad de comercios**, **calidad de centros educativos**,
**calidad de centros sanitarios**, **calidad de instalaciones deportivas y de ocio**,
**autobús / tren / metro**, tipo de vivienda, nº de viviendas por edificio, nº de ascensores,
edad de la vivienda.

> ⚠️ **El propio paper advierte**: usar *códigos de municipio, códigos postales y lat/lon como
> regresores* "no tiene sentido económico aunque capturen las diferencias espaciales". →
> **O eliminas los códigos geográficos, o los tratas explícitamente como un bloque de efectos
> aleatorios espaciales. Nunca como features económicas.**

**Acceso a los datos**: Catastro vía **`gisce/pycatastro`** (cliente Python de los servicios web
libres del SEC, GPL-3.0) + INE vía la API Tempus3 + OSM vía **`gboeing/osmnx`**
(`features_from_place` para servicios y `ox.routing.isochrone` para accesibilidad) + CRTM vía GTFS.

**Ajustes temporales**: si el panel cubre 10-20 años, el precio de venta de cada año **no** es
comparable con el de hoy. Implementa un **índice de ajuste temporal** (indexación por periodo de
mercado) al estilo del módulo *time-adjustment* de **`larsiusprime/openavmkit`**, y documenta el
índice aplicado.

### 2. Target y métrica
- Target: **precio €/m²** (no precio absoluto): los municipios tienen escalas muy distintas.
- Si el precio asked (no de venta cerrada), dilo en el informe: los asked prices están sesgados
  al alza y sobreestiman el valor.
- **Métrica principal: MAE en €/m²** (interpretable por la ciudadanía) + RMSE + R² fuera de muestra.
- **Métrica de negocio: MAPE** por municipio, y especialmente el error en los municipios con
  **menos observaciones** (es donde el AVM se degrada).

### 3. Modelos a comparar (obligatorio, en este orden)
1. `DummyRegressor` (media y mediana) → baseline.
2. Regresión ridge/ElasticNet con variables transformadas (log del precio) → baseline interpretable.
3. `RandomForestRegressor` con **`n_estimators` entre 100 y 500**. La literatura española
   (Alicante, *Expert Systems with Applications* 2021) encuentra **RF(200)** óptimo:error < 2 %
   y tiempo/espacio mínimos frente a 300/400/500 equivalentes. Empieza por 200 y justifica.
4. `LGBMRegressor` (LightGBM) → captura mejor los efectos no lineales y las interacciones.
5. `HistGradientBoostingRegressor` de scikit-learn → alternativa sin dependencia extra.
6. **Stacking**: RF + LGBM + Ridge con un meta-modelo ridge.

**No uses `GradientBoostingRegressor` clásico** si LGBM está disponible: es más lento y peor.

### 4. Validación (obligatorio, ver prompt 04)
- Expanding window temporal + `GroupKFold` por municipio + **spatial K-fold** por comarca.
- **No** `KFold` aleatorio.
- Toda la preprocessing (`SimpleImputer`, `OneHotEncoder`, `StandardScaler`) **dentro** del
  `Pipeline` para que se re-ajuste en cada fold.

**Folds espaciales con buffer — obligatorio aquí.** Los 41 municipios son geográficamente
contiguos: con K-fold aleatorio, los vecinos inmediatos de un municipio en test están en train y
el modelo memoriza el nivel de precio local.
- Implementa **buffered spatial K-fold**: un municipio y sus vecinos a menos de **D km** no pueden
  estar en folds distintos. Elige `D` contra el **rango de autocorrelación de los RESIDUOS**
  (no del target) — el marco de Roberts et al. (2017), implementado en `rvalavi/blockCV`.
- Calcula las distancias en **CRS proyectada** (Madrid: **EPSG:25830**, ETRS89 UTM 30N). En
  EPSG:4326 un buffer en grados no significa nada.
- Referencia Python: `WalidGharianiEAGLE/spatial-kfold` y `SamComber/spacv` (este último trae
  además `EnvironmentalCV`, útil como stress test: folds adyacentes pero con altitud muy distinta,
  la Sierra frente a la meseta).
- Con 41 municipios, un 5-fold espacial deja ~8 municipios de test por fold → **varianza enorme**.
  Considera **leave-one-municipality-out con buffer** (41 folds) como estimador principal y
  **reporta la dispersión entre folds**, no solo la media.
- **Nested CV**: con n=41, una única estimación de CV es optimistamente sesgada (~10 % según
  Varoquaux 2018). El RMSE que publiques debe salir de **nested CV** (bucle interno para los
  hiperparámetros, externo para la evaluación) o no es defendible.

**Métricas adicionales de tasación** (no son estándar de ML, pero un evaluador técnico las
reconoce): **COD** (coefficient of dispersion), **PRD**, **PRB** y **MKI**, más desglose por
municipio y por estrato de tamaño. Implementadas en `ccao-data/model-res-avm`.

### 5. Bandas de incertidumbre (requisito del proyecto)

**Cuidado con la escala del conformal espacial.** El paper de referencia (arXiv:2312.06531, código
oficial en `adhjort/ConformalPrediction`, **en R**) usa pesos `w_i = exp(−d²/η)` con **η elegido
para que el peso se reduzca a la mitad a 800 m** — escala de Oslo, con Districts contiguos.
**Vuestros municipios rurales están a 10-80 km**: si copies el η, todos los pesos valen casi lo
mismo y el conformal espacial deja de hacer nada. **Re-deriva η** para que el peso se reduzca a
la mitad a ~15-25 km, y **justifica el valor** en la memoria.
**La variante "nearest neighbour" (radio 1 km) es inútil a escala municipal**: descártala.
**La variante Mondrian (calibración por municipio) queda infra-potenciada** con n=41: calibra
agrupando (pooled) entre municipios con la ponderación espacial.

**Y recuerda la restricción de tamaño**: el paper simula con 6.000 filas por réplica; el panel del
M1 tiene **41 municipios × 10-20 años = 410-820 filas**. Split conformal con `n_cal ≈ 164-328` es
estadísticamente fino. **Mitiga con calibración agrupada + ponderación espacial**, o con
bootstrap bayesiano conformal, y dilo en la memoria.

**Coherencia entre horizontes**: si también publicas bandas de la proyección demográfica a 5 y 10
años, deben ser **monótonas** (P5(5 años) ≤ P5(10 años)). Una banda por horizonte suelta puede
invertirse y hace el fan-chart incoherente.
Implementa **predicción conformal** (`split` o `CP+`) sobre el intervalo:
- **Usa `MAPIE` (`scikit-learn-contrib/MAPIE`, 1.6k★)**: `MapieRegressor` (split CP),
  `MapieQuantileRegressor` (CQR, Romano et al. 2019) y `TimeSeriesRegressor` para el caso
  temporal. Es la librería canónica del ecosistema `scikit-learn-contrib` y trae tests de
  exchangeability y control de riesgos.
- El conjunto de **calibración** se obtiene **en un periodo temporal posterior** al
  entrenamiento, nunca sobre el test.
- Alternativas a comparar: **quantile regression** (`LGBMRegressor(objective="quantile")` o
  `GradientBoostingRegressor(loss="quantile")` con `alpha=0.025` y `0.975`), **NGBoost**, y
  **conformal espacialmente ponderada**
  (paper: *Uncertainty quantification in automated valuation models with spatially weighted
  conformal prediction*, arXiv:2312.06531) — esta última es la más adecuada porque el error
  del AVM **depende de la ubicación**.
- **Valida el ancho**: el ejemplo oficial de scikit-learn
  (`plot_gradient_boosting_quantile`) muestra que con quantile regression la cobertura medida
  puede ser ~0,80 cuando el 90 % nominal: **mide la cobertura real y calibra si hace falta**.
- Reporta: **cobertura empírica** (% de predicciones dentro del intervalo; debe acercarse a 95 %)
  y **longitud media del intervalo** (cuanto menor, mejor, a igual cobertura).

### 6. Esfuerzo financiero familiar (output de negocio, no de modelo)
```
esfuerzo_anual = cuota_hipoteca(principal = precio_m2 * superficie_mediana,
                                 tipo_interés, plazo)
esfuerzo_pct   = esfuerzo_anual / renta_media_hogar_municipio
```
- Usa la **renta media por hogar del INE** del municipio (mismo año).
- **Escenario de tipo**: acquisition vs alquiler. El alquiler NO genera un esfuerzo financiero directo
  sino **coste de oportunidad** (diferencia entre cuota y alquiler) — trátalo como tal y explica
  la diferencia en la ficha municipal, no como el mismo número.
- Segmenta el resultado por quintil de renta del hogar para que la app pueda mostrar
  "esfuerzo para renta baja / media / alta".

### 7. Sesgo de mercado y robustez
- ¿El modelo aprende el "precio del mes" en vez del valor? Test: **time-split robustness**.
- Comprueba la **estabilidad** de las importancias entre folds (top-10 features).
- Detecta municipios donde el modelo **extrapola** (predicciones fuera del rango observado de
  ese municipio) y márcalos: el AVM **debe ser interpolación, nunca extrapolación** entre
  municipios muy diferentes. Para ello, añade el municipio como feature categórica o usa
  **target encoding con CV** (no con el target completo).

## Output Expectations

1. `src/lodcore/models/m1_avm/` con: `features.py`, `train.py`, `conformal.py`,
   `evaluate.py`, `effort.py`, `model_card.md`.
2. `reports/m1_avm_validacion.md` con la tabla de modelos × métricas × bandas.
3. `model_card.md`: propósito, datos, features, hiperparámetros, métricas con banda, cobertura
   conformal, supuestos, límites conocidos, fecha de entrenamiento.
4. Salida en formato:

```
M1 AVM — compra | alquiler
DATOS: n_train / n_test / n_municipios / rango años
MEJOR MODELO: <modelo> (<justificación>)
MÉTRICAS (test temporal): MAE <x> €/m² | RMSE <y> | R² <z>  [IC95: ...]
COBERTURA CONFORMAL: <p>% (objetivo 95%) | longitud media: <q> €/m²
MAPE POR MUNICIPIO: mediana <a>% | peor municipio: <nombre> (<b>%)
ESFUERZO FINANCIERO (renta mediana): <c>% del ingreso | rango entre municipios: <d>–<e>%
RENDIMIENTO EN MUNICIPIOS PEQUEÑOS (n<10 obs): <comparativa vs. grandes>
PENDIENTES: <lista>
```

## Quality Assurance

- [ ] `n_estimators` justificado con evidencia (curva de error vs. tiempo), no por defecto.
- [ ] El RMSE publicado sale de **nested CV** con folds **espaciales con buffer**, no de un K-fold simple.
- [ ] Las distancias del buffer se calculan en **EPSG:25830** (no en grados).
- [ ] η del conformal espacial **re-derivado** a la escala de Madrid y justificado.
- [ ] Los códigos geográficos (municipio, CP, lat/lon) **no** se usan como features económicas.
- [ ] Preprocessing dentro del `Pipeline`; `fit` solo con datos de train.
- [ ] Validación temporal + agrupada + espacial ejecutadas y reportadas.
- [ ] Banda al 95 % implementada y **cobertura verificada empíricamente**.
- [ ] Los naive baselines están comparados.
- [ ] `R²` fuera de muestra reportado (no solo train).
- [ ] El esfuerzo financiero usa renta media **del municipio y del año**, no nacional.
- [ ] `model_card.md` incluye fecha de entrenamiento y versión del dataset.
