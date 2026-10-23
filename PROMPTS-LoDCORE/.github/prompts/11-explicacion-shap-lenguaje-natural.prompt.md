---
description: 'Convierte valores SHAP y resultados del modelo en explicaciones en lenguaje natural en español, con niveles por perfil de usuario'
agent: 'agent'
tools: ['search/codebase', 'edit/editFiles', 'runCommands']
argument-hint: '[municipio=<nombre>]'
---

# Explicabilidad: de SHAP a lenguaje natural (ciudadanía y administraciones)

## Misión

Convertir la salida técnica del modelo (valores SHAP, sub-índices, bandas) en **texto en
español que un ciudadano o un técnico municipal entienda y pueda usar**, manteniendo **trazabilidad
total**: cada afirmación debe poder rastrearse hasta un número, un umbral y una regla.

Este prompt produce el contenido de la **Ficha Municipal & SHAP** y del **Cuello de Botella
Dominante** del mapa.

## Alcance y precondiciones

- Precondición: existe la tabla de SHAP por municipio (`var_id, valor_observado, shap_value,
  base_value, prediccion, cuello_botella, direccion`) y los umbrales en `thresholds.py`.
- Alcance: `src/lodcore/explain/` (redacción) + plantillas + tests de consistencia.

## Inputs

- `${input:municipio}` — municipio concreto para el ejemplo (por defecto: el de peor ICA).

## Workflow

### 1. Reglas de redacción (no negociables)
1. **Un claim = un número.** Prohibido "tiene buenos servicios" sin cifra y sin umbral.
2. **Siempre con referencia al umbral**: "1.523 hab/médico (crítico: > 1.500)".
3. **Diferencia explicação de causalidad**: el modelo es **predictivo, no causal**. Usa
   "el modelo considera que...", "contribuye a...", nunca "causa" ni "provoca".
4. **Incertidumbre siempre presente**: si la banda es ancha, dilo ("estimación con un margen de
   ±4 puntos; municipalities similares están entre X y Y").
5. **Nada de jerga técnica sin traducir**: SHAP → "contribución al resultado"; PCA → "componente
   resumida"; quantile → "rango probable".
6. **Longitud**: máximo 3 frases por bloque. La ficha se lee en móvil.
7. **Sin alarmismo**: "tensión" ≠ "catástrofe". El semáforo es "Holdura / Tensión / Colapso Crítico",
   no "desastre".
8. **Sin lenguaje discriminante**: no uses "pueblos de segunda", "municipios pobres" o similar.
   Habla de "capacidad de Man's sassat" y "músculo presupuestario".

### 2. Estructura obligatoria de la ficha municipal
```
[municipio] — [comarca] — [población] habitantes — [ICA]/100 — Semáforo: [estado]

QUÉ TIENE A FAVOR
- <frase con cifra y umbral>  (SHAP +<valor>)
- ...

QUÉ LE PESA
- <frase con cifra y umbral>  (SHAP -<valor>)

RIESGO A MEDIO PLAZO
- <qué pasa con +5 % de población: ratio sanitario, ocupación aulas>
- <cuello de botella dominante: nombre, valor, umbral>

CÓMO SE CALCULA
- Fuente: <fuente oficial> (<fecha>) | Modelo: <nombre + versión> | Fecha: <fecha>
- Los valores marcados como estimados no son mediciones; ver «Fuentes oficiales».
```
La última línea es **obligatoria**: sin ella la explicación no es auditable.

### 3. Dos registros lingüísticos (mismo contenido)
| Aspecto | Portal Ciudadano | Panel Institucional |
|---|---|---|
| Tono | cercano, evita tecnicismos | técnico, cuantitativo |
| Foco | "¿me conviene?" | "¿qué inversión necesitan?" |
| Unidad | "1.523 habitantes por médico" | "ratio sanitario = 1.523 hab/médico" |
| Riesgo | "si llegan más familias, la atención primaria se tensaría" | "colapso sanitario en escenario +5 %" |
| Llamada a la acción | "compara con otros municipios" | "simula una inversión" |

Genera **las dos versiones** a partir de la **misma estructura de datos**, no escribiendo dos
textos a mano: define una plantilla por campo y dos tablas de estilo.

### 4. Procedimiento (datos → texto)
1. Selecciona las variables relevantes: top-3 por |SHAP| **y** las que están en estado
   TENSION/COLAPSO, aunque su SHAP sea pequeño (un cuello de botella clinically relevante puede
   tener SHAP modesto).
2. Para cada una, redacta con la plantilla correspondiente al estado.
3. Si la **banda de incertidumbre** cubre un umbral (p. ej. la estimación del ratio sanitario es
   1.450–1.600 y el umbral es 1.500), **no afirmes** TENSION ni NORMAL: redacta "resultado
   indeterminado en torno al umbral". Esto es crítico para la credibilidad.
4. Verifica **consistencia con el semáforo**: si el semáforo dice "Alta", no puede haber un
   párrafo de "riesgo a medio plazo" que suene a colapso sin matizarlo.

### 5. Control de calidad automático (implementa tests)
- **Test de trazabilidad**: cada número del texto aparece literalmente en la tabla de SHAP o en
  `thresholds.py`. Falla si hay un número "inventado".
- **Test de umbrales**: cada comparación con un umbral usa el valor vigente de `thresholds.py`.
- **Test de no-compensatoriedad**: el texto de "qué le pesa" menciona el cuello de botella
  dominante aunque el ICA sea alto.
- **Test de no-causalidad**: busca verbos causales prohibidos ("causa", "provoca", "genera",
  "lleva a", "por culpa de") y falla si aparecen.
- **Test de registro**: la versión ciudadana no contiene jerga (>3 términos técnicos → aviso).

### 6. Plantilla para el mapa (texto corto)
Para el popup del mapa (máx. 25 palabras):
> Chinchón · 5.810 hab. · ICA 31/100 · Colapso sanitario: 1.523 hab/médico (>1.500). flipped.

### 7. Redactar la ficha del cluster (M5)
Además de la ficha municipal, redacta la ficha de **tipología territorial**: a quién le conviene
ese tipo de municipio y a quién no. Con la misma trazabilidad.

## Output Expectations

1. `src/lodcore/explain/narrate.py` (motor de redacción) + `templates.py` (plantillas por campo)
   + `styles.py` (dos registros) + `tests/test_narrative.py` (los 5 tests del punto 5).
2. `reports/narrativa_ejemplos.md` con la ficha completa de 3 municipios (unoHealthy, uno en
   tensión, uno en colapso), en **ambos registros**, más los popups cortos del mapa.
3. Un **glosario** de 20 términos técnicos → lenguaje claro, reutilizable por el equipo.

## Quality Assurance

- [ ] Cada número del texto es rastreable a la tabla de SHAP o a `thresholds.py` (test automático).
- [ ] No hay verbos causales en ninguna redacción (test automático).
- [ ] Cuando la banda cruza un umbral, el texto dice "indeterminado".
- [ ] La versión ciudadana no supera 3 frases por bloque.
- [ ] Los dos registros se generan desde la misma plantilla, no son dos textos sueltos.
- [ ] La ficha incluye la línea "Cómo se calcula" con fuente, modelo y fecha.
- [ ] `uv run pytest -q` pasa, incluidos los tests nuevos.
