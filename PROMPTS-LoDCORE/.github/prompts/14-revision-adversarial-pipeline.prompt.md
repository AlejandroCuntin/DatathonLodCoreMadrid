---
description: 'Revisión adversarial del pipeline completo: busca los 10 fallos que pueden hacer que el proyecto no supere una evaluación externa'
agent: 'agent'
tools: ['search/codebase', 'edit/editFiles', 'runCommands']
argument-hint: '[alcance=modelo|pipeline|completo]'
---

# Revisión adversarial del pipeline (pre-entrega)

## Misión

Intentar **romper** el proyecto antes de que lo haga un jurado externo. Buscar de forma
sistemática los fallos que invalidarían los resultados, y no confirmarlos.

Este prompt se ejecuta en **contexto fresco**, idealmente por otra persona o en otra sesión
de agente. Su valor está en el sesgo hacia la **disproof**, no hacia la aprobación.

## Alcance y precondiciones

- Precondición: pipeline completo implementado y entrenado al menos una vez.
- Alcance: lectura + ejecución de experimentos. **No modifiques el código** salvo que se te pida
  el *fix*. Reporta con precisión de fichero y línea.
- No repitas la documentación: si la model card ya dice algo, no lo señales como hallazgo
  (salvo que la documentación **mienta**, que es un hallazgo grave).

## Los 12 ataques (revísalos todos, en orden)

### A1 — ¿El modelo predice lo que dice predecir?
Ejecuta el pipeline end-to-end con el dataset **actual** y comprueba que el score publicado
coincide con el score recomputado. Divergencia > 0,5 puntos = **BLOQUEANTE**.

### A2 — ¿El índice ICA es una tautología?
Si el target del M4 es una combinación de los sub-índices de M2, y las features del M4 incluyen
esos mismos sub-índices, el modelo puede estar **repitiendo** lo que ya se sabe.
Cuantifica: ¿qué porcentaje de la varianza del target queda explicada por las features lineales
(R² de una regresión lineal simple sobre las mismas features)? Si R² lineal > 0,9, el M4 aporta
poco y hay que decirlo. **Si el target y las features comparten componentes, dilo con números.**

### A3 — ¿La no-compensatoriedad se sostiene?
Ejecuta el test del prompt 09 y además: **añade 50 % de zonas verdes a un municipio en colapso
sanitario y comprueba que su ICA no sube.** Si sube, la tesis del proyecto no está implementada
y el jurado lo detectará en 5 minutos.

### A4 — ¿La accesibilidad depende de datos que caducan?
¿El GTFS que usaste tiene fecha? ¿Los feeds de CRTM y Renfe tienen la misma cobertura temporal
que el Padrón? Si los isócronas son de 2026 y la población de 2015, el modelo mezcla plazos.

### A5 — ¿La proyección demográfica sobrevive a un backtest honesto?
Rolling-origin sobre los 3 últimos años **completos** del histórico: ¿el SARIMAX (con exógenas)
bate al drift? ¿La banda al 95 % cubre realmente el 95 %?

### A6 — ¿Los municipios excluidos son los que sobran?
41 municipios, 2 o 3 con datos pobres. ¿El pipeline los ha dejado fuera? Si sí, el modelo se
entrenó con 38 y **el ranking de la APP muestra 41** → inconsistencia grave. Comprueba que
`n_train + n_excluidos + n_sin_datos = 41` y que la APP lo declara.

### A7 — ¿La escala de los scores es interpretable?
Los sub-índices son MinMax sobre 41 municipios: el mejor municipio es 100 **por construcción**.
¿La ficha dice "ICA 100/100" al usuario sin advertir que es relativo a la muestra? ¿Y el
"cuello de botella dominante" se compara con un umbral absoluto o relativo? Mezclar ambos es
un error conceptual grave.

### A8 — ¿La simulación What-If es creíble?
Aplica un Δ de inversión **fuera del rango observado** y comprueba que la respuesta del modelo
es absurda. Si lo es y la APP no lo advierte, es **BLOQUEANTE** (el simulador es el producto).

### A9 — ¿Se puede reproducir?
Borra los artefactos (en un directorio de trabajo, no en el repo), ejecuta `dvc repro` y compara
con los publicados. ¿Sale idéntico? ¿Cuánto tarda? Si no es reproducible en < 30 min, es un
problema para un datathon.

### A10 — ¿Hay datos que no se pueden publicar o que están mal identificados?
- ¿Algún municipio está mal emparejado por **nombre** en vez de por **código INE**?
  Verifica las 41 correspondencias una a una, en una tabla.
- ¿Hay alguna cifra de la APP que no se pueda rastrear a una fuente oficial?

### A11 — ¿La narrativa sobrevive a un "¿de dónde sale esto?"
Simula una pregunta de un técnico de la Dirección General de Reequilibrio Territorial:
"¿Por qué Chinchón está en colapso?" → ¿puedes responder con la cifra, la fuente, el umbral, el
modelo y la fecha en menos de 2 minutos? Si no, falta trazabilidad.

### A12 — ¿Los claims del documento de diseño se cumplen?
Contrasta **uno por uno** los claims del PDF "Diseño e Implementación" con lo implementado:
- ¿Se calcula el precio €/m² **de compra y alquiler**? ¿Y el esfuerzo financiero?
- ¿Se calculan isócronas de **30 min** en público y privado?
- ¿Se aplican **PCA + MinMax** a **4 sub-índices** con esos nombres exactos?
- ¿La proyección es a **5 y 10 años** con **bandas de incertidumbre**?
- ¿El recomendador usa **K-Means/GMM** + **similitud del coseno ponderada**?
- ¿Se identifican **cuellos de botella** con SHAP?
Marca cada claim: `CUMPLIDO` | `PARCIAL` | `NO CUMPLIDO` | `NO VERIFICABLE`.

## Output Expectations

```
# Revisión adversarial — <fecha>
## Veredicto: APTO PARA ENTREGA / APTO CON RESERVAS / NO APTO
## Resumen: <n> bloqueantes, <n> materiales, <n> menores
## Bloqueantes
### [BLOQUEANTE] A<n> — <título>
**Qué encontré:** <descripción precisa>
**Evidencia:** <comando + salida, o fichero:línea + cita>
**Por qué importa:** <impacto en la evaluación o en el usuario>
**Fix mínimo:** <cambio concreto>
**Coste del fix:** <bajo|medio|alto> | <estimación>
## Materiales / Menores (mismo formato)
## Claims del documento de diseño (tabla A12)
## Lo que resiste el ataque (destacado: los puntos fuertes)
## Recomendación final: <qué hacer antes de entregar>
```

## Quality Assurance

- [ ] He ejecutado los 12 ataques, no solo los que me convencen.
- [ ] Cada hallazgo tiene **evidencia ejecutable** (salida de comando), no opinión.
- [ ] He separado bloqueante / material / menor con criterio explícito.
- [ ] He incluido una sección de **puntos fuertes** (una revisión solo negativa no es útil).
- [ ] He verificado la tabla de claims A12 completa (12 ataques, no 8).
- [ ] No he modificado el código del pipeline.
- [ ] He comprobado la reproducibilidad de verdad (A9).
