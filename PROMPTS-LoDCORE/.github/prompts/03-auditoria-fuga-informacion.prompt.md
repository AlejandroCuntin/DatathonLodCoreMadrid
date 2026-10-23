---
description: 'Audita el pipeline de ML en busca de fuga de información temporal, espacial y entre fases de los 5 modelos'
agent: 'agent'
tools: ['search/codebase', 'edit/editFiles', 'runCommands']
argument-hint: '[modelo=m1|m2|m3|m4|m5]'
---

# Auditoría de fuga de información (data leakage)

## Misión

Determinar, con evidencia ejecutable, si el pipeline del modelo seleccionado **puede usar
información que no estaría disponible en el momento de la decisión**, y clasificar cada caso como leakage o no.

Este es el riesgo número uno del proyecto: **n = 41 municipios** hace que cualquier fuga
inflate las métricas hasta hacerlas inservibles para un evaluador externo.

## Alcance y precondiciones

- Precondición: existe el código de entrenamiento y el dataset del modelo.
- Alcance: lectura del código + ejecución de experimentos de prueba. **No modifiques el
  entrenamiento** salvo que se te pida el *fix*.
- No evalúes la calidad del modelo; evalúas su **validez metodológica**.

## Inputs

- `${input:modelo}` — `m1` | `m2` | `m3` | `m4` | `m5` (obligatorio).

## Workflow

### Fase 1 — Reconstruye la línea temporal del dato
Para cada variable que entra al modelo, responde con evidencia:
1. ¿De qué fuente y de qué tabla viene?
2. ¿En qué fecha se **publicó** ese dato (no la fecha a la que se mide)?
3. ¿En qué fecha estará disponible un valor equivalente para un municipio **nuevo** (el que
   el usuario final quiere puntuar)?
4. Por tanto, ¿puede la variable estar en el modelo en el momento del *scoring*?

Construye una **tabla de disponibilidad (as-of date)** y marca cada variable como:
`DISPONIBLE` | `SOLO HISTÓRICO` | `REQUIERE PROYECCIÓN` | `IMPOSIBLE EN PRODUCCIÓN`.

### Fase 2 — Las 7 fugas que buscamos
| # | Fuga | Test concreto |
|---|---|---|
| L1 | **CV aleatorio sobre el panel** | ¿`KFold`/`train_test_split` sin `group`? El mismo municipio aparece en train y test. Test: reentrenar con `GroupKFold(municipio)` y comparar. Una caída de R² > 0,15 indica fuga. |
| L2 | **Fuga temporal** | ¿La validación incluye años posteriores al entrenamiento sin `TimeSeriesSplit`? Test: reentrenar con split temporal y comparar. |
| L3 | **Fuga por variable derivada del objetivo** | Ej. usar `precio_venta` para predecir `precio_venta`. Test:SHAP/importances y correlación con el target. |
| L4 | **Fuga entre fases de la cadena** | ¿M4 usa variables de M3 (proyectadas) y de M1 (entrenadas sobre el mismo periodo)? ¿Alguna fase se entrenó con datos que incluyen el periodo de evaluación? |
| L5 | **Fuga por normalización** | ¿`MinMaxScaler`/`StandardScaler` **antes** del split? Test: los `scaler`/`imputer` se ajustan dentro del `Pipeline` y se re-ajustan en cada fold. |
| L6 | **Imputación leaking** | ¿El `SimpleImputer`/`KNNImputer` se ajusta con todo el dataset? Test: imputación dentro del pipeline CV. |
| L7 | **Fuga por duplicación de filas** | ¿Filas casi idénticas (mismo municipio, mismo año, variables imputadas) en train y test? Test: distances entre filas de train y test. |

### Fase 3 — Sesgo de selección y survivorship
- ¿Se han excluido municipios del panel de forma no aleatoria (p. ej. los que "no tienen datos")?
  Eso es *survivorship bias* y cambia la conclusión del modelo.
- ¿El conjunto de evaluación representa a los 41 municipios, o solo a los "bonitos"?

### Fase 4 — Reproduce y cuantifica
Ejecuta el experimento **con leakage** y el **sin leakage**, con la misma semilla. Reporta:

| Métrica | Con leakage | Sin leakage | Δ |
|---|---|---|---|
| R² / MAE / RMSE (train) | | | |
| R² / MAE / RMSE (test) | | | |
| Correlación features–target | | | |

**Si la diferencia es pequeña**, la fuga no está impacting y dilo: es una buena noticia.

### Fase 5 — Dictamen
Clasifica cada fuga encontrada: `BLOQUEANTE` (infla métricas de forma material) | `MATERIAL` |
`TEÓRICA` | `LIMPIA`.

## Output Expectations

```
# Auditoría de fuga — <modelo>
## Veredicto: <n> bloqueantes, <n> materiales, <n> limpias
## 1. Tabla de disponibilidad (as-of) por variable
| variable | fuente | fecha publicación | disponible en scoring | veredicto |
## 2. Hallazgos
### [BLOQUEANTE] L1 — <nombre>
**Evidencia:** <código, línea, comando y salida>
**Impacto cuantificado:** <métrica antes vs después>
**Fix mínimo:** <cambio concreto, fichero y líneas>
## 3. Tabla de experimentos (con vs sin leakage)
## 4. Sesgo de selección
## 5. Plan de corrección priorizado
## 6. Qué NO está leaking (descartado con evidencia)
```

## Quality Assurance

- [ ] Cada hallazgo cita **código y salida de comando**, no interpretación.
- [ ] He ejecutado los dos experimentos (con/sin leakage) con la misma semilla.
- [ ] He incluido los hallazgos descartados: "no hay fuga aquí, y esto es por qué".
- [ ] He verificado el orden `fit` → `transform` dentro del `Pipeline`.
- [ ] He comprobado explícitamente si `scaler`, `imputer` y `selector` están dentro del pipeline.
- [ ] He quantified el impacto, no solo su presencia.
