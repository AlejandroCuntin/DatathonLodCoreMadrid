---
description: 'Construye el Modelo 4: XGBoost Regressor + SHAP para el Índice de Capacidad de Acogida, con simulación de inversiones'
agent: 'agent'
tools: ['search/codebase', 'edit/editFiles', 'runCommands']
argument-hint: '[horizonte=5|10]'
---

# Modelo 4 — Índice de Capacidad de Acogida (XGBoost + SHAP)

## Misión

Entrenar el modelo supervisado que **predice el Índice de Capacidad de Acogida (ICA) futuro**
de cada municipio, cruza la **demanda proyectada** (M3) contra la **oferta de vivienda** (M1),
**servicios** (M2), **transporte**, **medioambiente** y **presupuestos**, y que:

1. **Simule** qué pasa si un ayuntamiento invierte más en transporte o construye un centro educativo.
2. **Identifique automáticamente** fortalezas y cuellos de botella de cada municipio.

Todo con **explicabilidad SHAP** que se pueda mostrar en la ficha municipal.

## Alcance y precondiciones

- Precondición: M1, M2, M3 disponibles con sus artefactos y versiones; dataset panel construido.
- Alcance: `src/lodcore/models/m4_hosting_capacity/`.

## Inputs

- `${input:horizonte}` — `5` | `10` (por defecto `5`).

## Workflow

### 1. Definición del target: esto es lo más importante
El ICA **no es una variable observada**: hay que **construirlo** como etiqueta a partir de los
sub-índices de M2 y de M1. Sin una definición explícita, el modelo no tiene sentido.

**Target recomendado (interpretable y accionable):**
```
ICA(m, t+h) = media ponderada de sub-índices de M2 en (t+h)
              × penalización por saturación de servicios (ver prompt 09)
```
- **Pesos**: publícalos y justifícalos (p. ej. servicios 0,30, conectividad 0,25,
  sostenibilidad 0,20, músculo presupuestario 0,25). Alternativa: derivarlos por PCA sobre los
  sub-índices (compara ambas y elige con criterio, no por defecto).
- **El target debe ser construible con datos disponibles en t** (los sub-índices de M2 en t+h
  se calculan con M3 proyectado y M1 estimado).
- Documenta la fórmula exacta en `model_card.md` y en la página "Los 5 Modelos ML" de la APP.

**Alternativa si el equipo no se cierra una fórmula**: define el target como el **cambio
relativo** en el sub-índice (ICA en t+h − ICA en t) o como un **índice de degradación de
servicios** (que es literalmente lo que dice el documento: *"si sus ratios de servicios por
habitante mejoraron o se degradaron"*). Compara ambas definiciones.

### 2. Construcción del dataset de entrenamiento (panel histórico)
El documento dice: *"entrenamos sobre datos históricos en panel, evaluando cómo evolucionaron
en los últimos años los municipios que recibieron choques de población"*.

- Target por (municipio, año): el ICA (o su delta) en `t+h`.
- Features: todo lo de M1, M2, M3 **más** las variables del propio municipio en `t`.
- **Variables de "shock"**: `delta_poblacion`, `poblacion_2024` (control de tamaño),
  `dummy_choque` (¿el municipio recibió un choque en t?).
- **Identifica los municipios que recibieron choques** con un criterio explícito y auditable.
  Tres opciones, de más simple a más rigurosa:
  1. **Descriptiva**: crecimiento anual > p90 nacional en algún año. Rápida, pero no causal.
  2. **Barrido espacial** (`satscan`, como en `AndreaAzabal/proyecto-vivienda`): detecta racimos
     espaciales de crecimiento anómalo → define la geografía del choque.
  3. **Control sintético por municipio** (**recomendada**): `sdfordham/pysyncon` con **control
     sintético aumentado** (Ben-Michael-Feller-Rothstein 2021), que da **intervalos válidos para
     una sola unidad tratada** y un **p-valor placebo-in-space**. Para cada municipio construyes
     su versión sintética con los otros 40 + outcomes pre-shock, y lees el efecto. El p-valor es
     el test honesto de *"¿este municipio realmente recibió un choque?"*.
     `pysyncon` incluye `parity_tests/` que lo verifica contra el paquete R `Synth`: es tu
     argumento de corrección ante el jurado.
  Documenta cuántos son (probablemente pocos: con 41 municipios el subgrupo tratado será **muy
  pequeño**, y eso es un riesgo de causalidad).
- **Target leakage**: la feature `poblacion_t` y `delta_poblacion_t` son contemporáneas al target
  futuro, **no** el target. Verifica que ninguna feature contenga información de `t+h`.

### 3. Modelo y validación
- `XGBRegressor` con `objective='reg:squarederror'`. Alternativas: `RandomForestRegressor`
  (más interpretable en SHAP, peor en no linealidad) y `LGBMRegressor`.
- **Validación**: expanding window temporal (obligatorio) + `GroupKFold` por municipio +
  espacial por comarca (ver prompt 04).
- **Hiperparámetros**: Optuna con **pruning** (`MedianPruner`) y **espacio de búsqueda
  acotado** (n=41 no admite búsquedas libres). Registra todo en MLflow con el `dataset_version`.
- **Banda de incertidumbre** al 95 % (conformal sobre residuales de validación temporal).
- **Comparar contra baselines**: (a) el ICA actual sin cambio (persistencia), (b) la media de
  los subtítulos, (c) la proyección de M3 sin ajuste por capacidad. Si XGBoost no bate a la
  **persistencia** de forma consistente, reevalúa el planteamiento.

### 3 bis. Si el grupo tratado tiene choques escalonados: no uses TWFE
Si los choques llegaron **en momentos distintos**, la regresión de efectos fijos bidireccional
(`feols(y ~ shock_post | municipio + year)`) está **sesgada** (Goodman-Bacon; de Chaisemartin &
D'Haultfœuille). Opciones correctas:
- **SDID** (`pymc-labs/CausalPy`): pesos de control sintético por municipio tratado → contrafactual
  que respeta el desequilibrio de covariates y el confounding por factor común, y **devuelve una
  distribución** del efecto (bandas de incertidumbre de regalo).
- **Callaway–Sant'Anna / `drd`** (`py-why/dowhy`): agregación group-time ATT + **suite de refutación**
  (`random_common_cause`, `placebo_treatment`, `random_data`, `data_subset`) — es exactamente lo que
  pedirá un jurado.
- **Control sintético** (`sdfordham/pysyncon`) si el tratamiento es de una sola unidad.
- **Sintético disperso multi-unidad** (`microsoft/SparseSC`) si son muchas unidades escalonadas.
Para el panel, los errores estándar correctos con correlación espacial son los de
**Driscoll-Kraay** (`bashtage/linearmodels`), no los cluster-robust ingenuos. Con 41 clusters,
inferencia cluster-robust es débil: usa **wild cluster bootstrap**.
Si además quieres estimar el canal mediado *choque → precio (M1) → capacidad (M4)*, usa
**Double ML** (`DoubleML/doubleml-for-py`): estimador parcialmente lineal con funciones de
nuisance no lineales (LightGBM), que es la forma estadísticamente honesta de combinar M1 con M4.

### 4. SHAP: la parte que la APP consume
- `shap.TreeExplainer` (exacto y rápido para XGBoost/LGBM).
- ⚠️ **NO incluyas `municipio_ine` como feature.** Con 41 municipios, SHAP quedaría dominado por el
  identificador, que no explica nada. Úsalo solo como clave de agrupación.
- Fija el **conjunto de background** (`shap.Explainer(model, X_bg)`) y persiste su hash junto a
  cada fila de explicación: sin eso, los valores SHAP no son reproducibles.
- En panel, calcula SHAP por fold y promedia; no atribuyas sobre un modelo pooled sin preservar
  la estructura de folds.
- Calcula **SHAP global** (beeswarm, barra de importancias) y **SHAP local** por municipio.
- **Criterio de "cuello de botella"**: una variable es cuello de botella de un municipio si su
  valor está en el **peor quintil** de su distribución **y** su contribución SHAP es negativa.
  Un variable con SHAP negativo pero valor normal **no** es un cuello de botella: es ruido.
  Documenta este criterio y aplícalo de forma uniforme a los 41 municipios.
- **Ranking de fortalezas**: simmetricamente, SHAP positivo + valor en el mejor quintil.
- Persiste, por municipio: `var_id`, `valor_observado`, `shap_value`, `base_value`,
  `prediccion`, `cuello_botella` (bool), `direccion` (`favorable`/`adverso`),
  `esfuerzo_financiero_impacto` (para M1), `cuartil_valor`.

### 5. Simulación de inversiones (What-If)
Requisito: *"si un ayuntamiento aumenta su presupuesto de inversión en transporte o construye
un nuevo centro educativo, ¿cuánto aumenta la capacidad de acogida predicha?"*.

- **Simulación en el espacio de features**: copia el vector de features del municipio,
  incrementa `inversion_transporte_per_capita` en Δ (o `nuevos_centros_educativos` en +1),
  y recalcula la predicción. **Reporta el delta absoluto y en puntos de ICA**.
- **Advertencia crítica que la APP debe mostrar**: el modelo **no conoce** la forma funcional
  del efecto de una inversión (no sabe si 1 M€ en transporte o en educación rinde lo mismo).
  La simulación solo es válida **dentro del rango observado** en los datos de entrenamiento.
  Si el Δ cae fuera de ese rango, marca la simulación como **extrapolación no fiable**.
- **Interpretabilidad de la simulación**: muestra el waterfall SHAP **antes/después**, para que el
  usuario vea *por qué* cambió el score y no solo cuánto.
- **Simulación de escenario demográfico**:opulation +5 % / +10 % → recalcula
  `hab/por_médico`, `ocupación_aulas` y el ICA resultante.

### 6. Endurecimiento
- **Test de monotonía**: si `inversion_per_capita` sube, ¿el ICA sube siempre? XGBoost **no
  garantiza** monotonía. Entrena con `XGBRegressor(monotone_constraints={...})` si el dominio
  lo exige, o implementa un **post-proceso isotónico/monotónico** y documenta la decisión.
- **Test de sensibilidad al umbral**: ¿el ranking de municipios es estable a los umbrales
  (1500 hab/médico, 95 % aulas)?
- **Fairness territorial**: ¿el modelo penaliza a los municipios pequeños por tener menos datos?
  Compara el error por estrato de población. Si el error es muy asimétrico, el modelo puede estar
  **sobreajustado a municipios grandes** → añade features de interacción con `log(poblacion)`.

## Output Expectations

1. `src/lodcore/models/m4_hosting_capacity/` (`target.py`, `features.py`, `train.py`,
   `shap_export.py`, `simulate.py`, `evaluate.py`, `model_card.md`).
2. `reports/m4_hosting_capacity.md`:
```
# M4 — Capacidad de Acogida
## Definición del target: <fórmula exacta> + justificación + alternativa comparada
## Dataset: n_train/n_test | n municipios | n obs por municipio (chocantes vs no)
## Métricas (test temporal + agrupado + espacial): MAE <x> puntos de ICA | R² <z> [IC95]
## Baselines: persistencia / media / M3-ajustado → ¿bate XGBoost? <sí/no>
## Banda 95 %: cobertura <p>%
## Monotonía: <resultado del test>
## Errores por estrato de población
## SHAP global: top-10 variables con |SHAP| medio
## Cuellos de botella detectados: <n municipios × n variables> (criterio documentado)
## Simulación What-If: ejemplo de Chinchón con Δ inversión → Δ ICA (+ advertencia de extrapolación)
## Escenario +5 %/+10 %: tabla deStressCollapse
```
3. `model_card.md` de M4 con la fórmula del target, los pesos, el dataset y las limitaciones
   (especialmente: **el modelo no conoce la estructura causal de la inversión**).

## Quality Assurance

- [ ] El target ICA está **definido con una fórmula explícita** y documentada.
- [ ] He verificado que **ninguna feature** contiene información de `t+h`.
- [ ] Validación temporal + agrupada + espacial ejecutadas.
- [ ] He comparado contra la **persistencia** (el baseline más duro aquí).
- [ ] El criterio de "cuello de botella" combina valor (quintil) **y** signo SHAP.
- [ ] `municipio_ine` **no** es una feature del modelo; y el background de SHAP está fijado y hashiado.
- [ ] La simulación What-If marca la extrapolación fuera de rango.
- [ ] He ejecutado el test de monotonía y he documentado el resultado.
- [ ] Cada predicción lleva banda al 95 %.
- [ ] `model_card.md` declara explícitamente que el modelo **no es causal**.
