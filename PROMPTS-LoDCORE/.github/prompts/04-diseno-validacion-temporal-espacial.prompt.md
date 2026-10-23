---
description: 'Diseña la estrategia de validación cruzada temporal y espacial para un panel de solo 41 municipios, con métricas y bandas honestas'
agent: 'agent'
tools: ['search/codebase', 'edit/editFiles', 'runCommands']
argument-hint: '[modelo=m1|m2|m3|m4|m5]'
---

# Diseño de validación temporal y espacial (n = 41)

## Misión

Diseñar y ejecutar un protocolo de validación **estadísticamente defendible** para un modelo
entrenado sobre un panel de **41 municipios** y ~10-20 años, y producir la tabla de métricas
con **bandas de incertidumbre** que la interfaz publica.

Con n tan pequeño, el error estándar de la métrica es grande. Publicar un único R² sin banda
es técnicamente incorrecto y un jurado lo detectará.

## Alcance y precondiciones

- Precondición: dataset panel listo, variable objetivo identificada, `AGENTS.md` leído.
- Alcance: scripts de evaluación en `src/lodcore/models/{modelo}/evaluate.py` + notebook de apoyo.
- No reescribas el entrenamiento; **envuelve** el pipeline existente en el protocolo.

## Inputs

- `${input:modelo}` — `m1` | `m2` | `m3` | `m4` | `m5` (obligatorio).
- `${input:objetivo}` — variable objetivo (ej. `precio_m2_venta`, `ica_global`, `poblacion_2030`).
- `${input:anios_test}` — años de test (por defecto: los 3 últimos disponibles).

## Workflow

### 1. Diagnóstico de la estructura del panel
- Nº de municipios, nº de filas, nº de años, densidad del panel (¿hay panel balanceado?).
- Nº de filas efectivas por fold.
- **Autocorrelación espacial**: calcula el I de Moran de la variable objetivo entre municipios
  (vecinos por proximidad del centroide o por adyacencia de la comarca). Si Moran's I es
  significativo, la CV aleatoria está **invalidada**.
- **Autocorrelación temporal**: ACF de la serie por municipio.

### 2. El protocolo: tres niveles, todos obligatorios
**Nivel A — Temporal (obligatorio).** Expanding window:
```
fold 1: train ≤ t0        test t0+1
fold 2: train ≤ t0+1      test t0+2
...
```
Con `n` años y 41 municipios, el **nº de folds es pequeño**: reporta el nº de observaciones
de test por fold. Si alguna fold tiene < 30 observaciones, dilo y justifica.

**Nivel B — Grupado por municipio (obligatorio).** `GroupKFold` con `groups = municipio_ine`.
Esto simula "qué pasa si este municipio no estuviera en el panel", que es la pregunta que
hace el usuario final.

**Nivel C — Spatial (obligatorio si Moran's I es significativo).** Agrupa municipios por
**comarca** (o por k-medias sobre coordenadas + variables estructurales) y usa
`GroupKFold` sobre esos grupos. Reporta ambos niveles.

### 3. Métricas con banda
- Para regresión: **MAE** (interpretable en €/m² o en puntos de índice), **RMSE**, **R²**.
  Añade **MAPE** solo si el denominador no se acerca a cero.
- Para ranking (M5): **NDCG@5**, **Recall@5**, y **hit-rate@3**.
- **Banda de confianza**: bootstrap **por municipio** (no por fila) con B = 1000 para el 95 %
  de confianza del intervalo de la métrica. Justifica el choix: las filas de un municipio no
  son independientes.
- Si el objetivo es un **índice 0-100**, reporta además MAE en puntos de índice: "el modelo
  falla por ±3,2 puntos en un índice de 100".

### 4. Baselines obligatorios
Un modelo no vale sin referencia. Compara contra, como mínimo:
1. **Media (naive)**: predecir la media histórica del municipio.
2. **Persistencia (naive)**: predecir el último valor observado.
3. **Regresión lineal** con las mismas features.
4. **DummyRegressor** de scikit-learn (media y mediana).
Tu modelo solo se declara útil si gana **de forma consistente** en el nivel A **y** en el B.

### 5. Sensibilidad
- ¿El resultado depende de la semilla? Reporta desviación estándar sobre ≥ 5 semillas.
- ¿Depende de incluir/excluir los municipios más atípicos? Reporta el leave-one-municipality-out
  de los 5 municipios más extremos y su efecto en la métrica.

### 6. Validación de la lógica de negocio
- ¿Las predicciones violan los umbrales (1.500 hab/médico, 95 % aulas) de forma absurda?
- ¿El modelo predice valores fuera del rango físico (p. ej. población negativa)?
  Añade un clip explícito y reporta cuántos puntos se recortan.

## Output Expectations

1. `src/lodcore/models/{modelo}/evaluate.py` reutilizable, con semilla fija y salida en JSON.
2. `reports/{modelo}_validacion.md` con:

```
# Validación — <modelo> — <objetivo>
## 1. Estructura del panel
## 2. Diagnóstico espacial y temporal (Moran I, ACF)
## 3. Protocolo A/B/C: descripción y nº de observaciones por fold
## 4. Métricas con banda de 95 % (bootstrap por municipio, B=1000)
## 5. Tabla de baselines
## 6. Sensibilidad (semillas, leave-one-out)
## 7. Cumplimiento de reglas de negocio y recorte de valores no físicos
## 8. Dictamen: ¿el modelo supera a los naive? ¿con qué margen y con qué banda?
## 9. Limitaciones declaradas (obligatorio: máx. 5, cada una con su impacto)
```

## Quality Assurance

- [ ] He calculado Moran's I y lo he usado para **justificar** el nivel C, no para ejecutarlo por trámite.
- [ ] El bootstrap es **por municipio**, no por fila.
- [ ] He reportado los baselines naive; si el modelo no gana, lo digo.
- [ ] He reportado el nº de observaciones por fold y he señalado folds TFTs (< 30).
- [ ] No he hecho CV aleatorio en ningún resultado reportado.
- [ ] Las bandas son de 95 % y están calculadas, no estimated.
