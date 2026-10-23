---
description: 'Implementa los cuellos de botella no compensatorios: un municipio con un servicio crítico colapsado no puede obtener ICA alto'
agent: 'agent'
tools: ['search/codebase', 'edit/editFiles', 'runCommands']
argument-hint: '[servicio=sanitario|educativo|ambiental|transporte|presupuesto]'
---

# Modelo 4b — Cuellos de botella no compensatorios

## Misión

Cerrar el **gap técnico más importante del proyecto**: la hipótesis fundacional dice que

> *"la carencia severa de un servicio crítico (transporte público o atención primaria) actúa
> como un cuello de botella que no puede compensarse con otros factores como zonas verdes,
> abundancia de suelo"*

pero **XGBoost es compensatorio por construcción**: basta con tener muchas zonas verdes para
compensar la falta de médicos. Este prompt implementa esa no-compensatoriedad **de forma
explícita, auditable y explicable**.

## Alcance y precondiciones

- Precondición: existe M4 (o al menos los sub-índices de M2 y los ratios de servicio).
- Alcance: `src/lodcore/models/m4_hosting_capacity/bottlenecks.py` + `thresholds.py`.
- **Todos los umbrales viven en un único módulo `src/lodcore/config/thresholds.py`**, importado
  tanto por el modelo como por la APP. Nunca copies un número a mano en dos sitios.

## Inputs

- `${input:servicio}` — `sanitario` | `educativo` | `ambiental` | `transporte` | `presupuesto`.

## Workflow

### 1. Inventario de umbrales (fuente: el prototipo, sin cambiarlos)
```python
HAB_POR_MEDICO_COLAPSO   = 1500   # ratio sanitario crítico
HAB_POR_MEDICO_TENSION   = 1200   # banda de tensión (proponer y justificar)
OCUPACION_AULAS_COLAPSO  = 0.95   # ocupación escolar crítica
OCUPACION_AULAS_TENSION  = 0.85
ICA_COLAPSO              = 40     # semáforo: Baja <40
ICA_TENSION              = 40     # Media 40-59
ICA_ALTA                 = 60
ISOCRONA_MINUTOS         = 30
ESCENARIOS_ESTRESS       = [0.05, 0.10]
```
Documenta de dónde sale cada uno (prototipo / literature) y **no los cambies sin actualizar
también la tabla de la APP**.

### 2. Clasificación del estado de cada servicio
Para cada municipio × año, cada servicio crítico (sanitario, educativo, transporte,
ambiental, presupuesto) se clasifica en:
`NORMAL` | `TENSION` | `COLAPSO`.

Regla de decisión **explícita y parametrizable** (usa bandas, no un único corte):
```
COLAPSO  si  ratio >= umbral_colapso
TENSION  si  umbral_tension <= ratio < umbral_colapso
NORMAL   en caso contrario
```

### 3. Índices no compensatorios
Implementa y **compara** tres formulaciones; elige una y justifica:

**A. Mínimo sobre sub-índices (no compensatorio puro)**
```
ICA_final = 100 * min( sub_sanidad, sub_educacion, sub_conectividad, sub_ambiental, sub_presupuesto )
```
Pros: trivialmente interpretable ("el mínimo manda"). Contras: ignora el valor de los demás.

**B. Media geométrica con pesos (compensa, pero poco)**
```
ICA_final = 100 * Π( sub_i ^ w_i )   con Σw_i = 1
```
La media geométrica penaliza fuerte los valores bajos. Es el estándar en indicadores
compuestos no compensatorios.

**C. Regla de veto (la más fiel a la hipótesis) — RECOMENDADA**
```
ICA_final = 100 * media_ponderada(sub_índices)
if algun servicio crítico en COLAPSO:
    ICA_final = min(ICA_final, ICA_MAX_CON_VETO)     # p. ej. 35
elif algun servicio crítico en TENSION:
    ICA_final = min(ICA_final, ICA_MAX_CON_TENSION)  # p. ej. 55
```
Es exactamente "no puedes compensar un cuello de botella con otros factores".
Justifica los topes (`ICA_MAX_CON_VETO = 35` deja al municipio por debajo del umbral de
"Media" del semáforo, es decir, visiblemente crítico).

**D. Complemento: penalización suave (opcional)**
```
ICA_final = ICA_base - Σ penalización_servicio_crítico(tensión) - 2*penalización(colapso)
```
Evita el efecto "cliff" (un municipio en 1499 hab/médico y otro en 1501 recibe scores muy distintos).

### 4. Auditoría de la no-compensatoriedad (test que hay que pasar)
Escribe un test que **falla si el modelo es compensatorio**:
```
Dado un municipio X con ICA_base = 85 yCollapse en el servicio sanitario,
    el ICA_final de X < 40
Dado el mismo municipio con +50% de zonas verdes (sin tocar servicios),
    el ICA_final NO aumenta (o aumenta < 2 puntos)
Dado un municipio Y sin ningún servicio en TENSION ni COLAPSO,
    el ICA_final de Y puede superar 60
```
Este test es **la prueba de que la tesis del proyecto está implementada**. Debe estar en `tests/`.

### 5. Índice de saturación de servicios frente a crecimiento esperado
Calcula, para el escenario de crecimiento `g` (5 % o 10 %):
```
ratio_sanitario_proy(g) = ratio_sanitario_actual / (1 + g)
ocupacion_aulas_proy(g) = ocupacion_actual * (1 + g)     # aproximación; refinar con plazas
```
Clasifica el municipio en `SOSTENIBLE` | `TENSION` | `COLAPSO_CRITICO` y produce la **matriz
de saturación** que la página "Escenarios de Crecimiento" muestra (con la alerta global).

### 6. Detección del "cuello de botella dominante"
Cuando un municipio tiene varios servicios tensos, ¿cuál se muestra en el mapa como
`Cuello de Botella Dominante`? Regia:
1. El de estado COLAPSO con mayor severidad (ratio normalizado más extremo).
2. Si no hay colapso, el de mayor tensión.
3. Si hay empate, el de mayor peso en el ICA final.
Documenta la regla. Devuelve también la lista completa (no solo el dominante) para la ficha.

### 7. Explicabilidad
Para cada cuello de botella detectado, genera una frase en **español** apta para la ficha municipal:
> "Chinchón tiene 1.523 habitantes por médico (umbral crítico: 1.500). Su conectividad (68/100)
> y su calidad ambiental (74/100) son sólidas, pero la presión sobre la atención primaria limita
> su capacidad de acogida a 31/100."

Estructura obligatoria: **estado → valor → umbral → contexto → consecuencia**.

## Output Expectations

1. `src/lodcore/config/thresholds.py` (única fuente de verdad) + `bottlenecks.py`.
2. `tests/test_no_compensatoriedad.py` con los 3 escenarios del punto 4.
3. `reports/m4_bottlenecks.md`:
```
# Cuellos de botella no compensatorios
## Formulación elegida: <A/B/C/D> y justificación (con comparación de las 4)
## Umbrales usados (tabla con origen)
## Estado por municipio × servicio × año (muestra) + nº de colapsos por comarca
## Test de no-compensatoriedad: PASS/FAIL con salida
## Matriz de saturación escenario +5 % y +10 % (colapsos sanitarios y escolares)
## Cuello de botella dominante por municipio
## Ejemplos de redacción de ficha (3 municipios)
```
4. Actualización de `model_card.md` de M4: el ICA final **no** es el output directo de XGBoost,
   es `f(XGBoost, umbrales)`. Documéntalo con claridad.

## Quality Assurance

- [ ] Todos los umbrales están en `thresholds.py` y **ningún número está duplicado** en el código.
- [ ] El test de no-compensatoriedad **falla** si alguien cambia la formulación a una compensatoria.
- [ ] El estado NORMAL/TENSION/COLAPSO usa **bandas**, no cortes únicos.
- [ ] La matriz de saturación usa los mismos umbrales que la APP.
- [ ] La redacción en español incluye valor, umbral y consecuencia.
- [ ] He comparado las 4 formulaciones y justificado la elegida.
- [ ] `uv run pytest -q` pasa, incluido el test nuevo.
