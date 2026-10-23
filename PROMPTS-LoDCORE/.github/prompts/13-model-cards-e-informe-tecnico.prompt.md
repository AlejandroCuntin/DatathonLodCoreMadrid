---
description: 'Genera las model cards de los 5 modelos, la página «Los 5 Modelos ML» y el informe técnico reproducible para el datathon'
agent: 'agent'
tools: ['search/codebase', 'edit/editFiles', 'runCommands']
argument-hint: '[modelo=m1|m2|m3|m4|m5|todos]'
---

# Model cards, página «Los 5 Modelos ML» e informe técnico reproducible

## Misión

Producir la **documentación metodológica** del proyecto: una *model card* por modelo, el
contenido de la página **"Los 5 Modelos ML"** de la APP (que el prototipo ya anuncia) y el
**informe técnico reproducible** exigible por las administraciones (que deben poder
*reproducir* los números, no solo leerlos).

## Alcance y precondiciones

- Precondición: modelos entrenados, artefactos en `mlruns/`, `dvc.lock` al día, métricas en
  JSON por modelo.
- Alcance: `docs/model_cards/`, `oracle/…` (contenido de la vista `vw_modelos`), `docs/informe/`.

## Inputs

- `${input:modelo}` — `m1` | `m2` | `m3` | `m4` | `m5` | `todos` (por defecto `todos`).

## Workflow

### Parte 1 — Model card por modelo (plantilla fija)

```
# Model card — <M#: nombre>
## 1. Resumen en 3 frases
## 2. Uso previsto
   - Qué decisión soporta y quién la toma (ciudadanía / ayuntamiento / planificador territorial)
   - Qué decisiones NO debe tomar (uso indebido)
## 3. Datos
   - Fuentes (URL + fecha de snapshot), periodo, nº de municipios, nº de filas
   - Variables de entrada (lista con descripción y origen)
   - Procesamiento y filtrado (qué se excluyó y por qué)
## 4. Target
   - Fórmula exacta, unidades, por qué es la etiqueta correcta
## 5. Modelo e hiperparámetros
   - Algoritmo, parámetros finales (los de params.yaml), semilla, librería y versión
## 6. Evaluación
   - Protocolo (temporal + agrupado + espacial), métricas con banda de 95 %
   - Baselines comparados y resultado del contraste
   -.Error por estrato (tamaño de municipio, comarca)
## 7. Incertidumbre
   - Método (conformal / quantile / bootstrap), cobertura empírica, longitud del intervalo
## 8. Explicabilidad
   - Variable global más influyente, interpretabilidad de las componentes (PCA)
## 9. Límites y riesgos conocidos   ← **la sección más importante**
   - Mínimo 4 ítems, cada uno con: descripción | impacto esperado | mitigación | quién lo asume
## 10. Criterios de nouso (cuándo el modelo NO debe usarse)
## 11. Reproduction
   - Comando exacto (`dvc repro <stage>`), dataset_version, fecha de entrenamiento, entorno
## 12. Historial
   - Versión, fecha, cambios, quién
```

**Regla dura de la sección 9**: cada límite debe tener **al menos un ejemplo concreto** de un
municipio o de un dato donde el modelo falla. Un límite abstracto ("puede fallar con datos
escasos") no es acceptable: escribe "Robledo de Chavela (n = 4 observaciones de precio) presenta
un intervalo de predicción de ±780 €/m², frente a ±190 €/m² en la mediana".

### Parte 2 — Página «Los 5 Modelos ML» (contenido de la APP)
Para cada uno de los 5 modelos, un bloque con:
- **Nombre** y **qué hace** en una frase.
- **Algoritmo** y **por qué ese** (1 frase).
- **Entrada principal** y **salida**.
- **Métrica principal** con su valor y su banda.
- **Fecha de entrenamiento** y **versión del dataset**.
- **Limitación principal** (una frase).
- Enlace a la model card completa.

### Parte 3 — Informe técnico reproducible (para las administraciones)
Estructura:
1. Resumen ejecutivo (1 página): qué pregunta el sistema, qué responde, qué **no** responde.
2. **Metodología**: los 5 modelos, el diagrama de flujo de datos, la tabla de proceeding por variable.
3. **Fuentes de datos**: tabla con fuente, URL, fecha de descarga, frecuencia de actualización,
   calidad y limitaciones de cada fuente.
4. **Resultados**: los números del ICA por municipio y por comarca, con banda.
5. **Validación**: protocolo, métricas, baselines, **y el análisis de sensibilidad** (qué pasa si
   cambiamos un supuesto).
6. **Simulación de inversión**: 3 escenarios de ejemplo con el efecto sobre el ICA, incluida la
   **advertencia de que el modelo no es causal**.
7. **Limitaciones**: las de todas las model cards, consolidadas.
8. **Reproducibilidad**: cómo regenerar cada número (`dvc repro`, comandos, versiones).
9. **Glosario** de términos técnicos.
10. **Anexos**: tabla completa de resultados (CSV adjunto).

### Parte 4 — Verificación cruzada
Antes de publicar, comprueba que **cada número del informe** existe en los artefactos:
- Escribe un script que extrae todos los números del informe y verifica que aparecen en los
  JSON de métricas o en las tablas de Oracle. Reporta los que no.
- Comprueba que las cifras del informe, de la model card y de la APP **coinciden** (mismo valor,
  misma fecha).

## Output Expectations

1. `docs/model_cards/m1_avm.md` … `m5_recommender.md` (5 archivos).
2. `docs/informe/informe_tecnico.md` + `docs/informe/anexo_resultados.csv`.
3. `docs/informe/glosario.md` (mínimo 25 términos).
4. `src/lodcore/publish/model_cards.py` que genera el contenido de `vw_modelos` desde MLflow y
   los JSON de métricas (para que la página no se quede desactualizada).
5. `reports/verificacion_documentacion.md` con el resultado del cross-check de números.

## Quality Assurance

- [ ] Las 5 model cards existen y tienen las 12 secciones.
- [ ] La sección de límites tiene **≥ 4 ítems**, cada uno con ejemplo concreto.
- [ ] Cada modelo tiene un criterio de "cuándo NO usarlo".
- [ ] El informe técnico tiene los 10 apartados.
- [ ] Todos los números del informe están verificados contra los artefactos.
- [ ] Informe, model cards y APP muestran las **mismas cifras**.
- [ ] El informe explica el pipeline de forma que un tercero pueda reproducirlo.
- [ ] El informe dice explícitamente qué preguntas **no** responde el sistema.
