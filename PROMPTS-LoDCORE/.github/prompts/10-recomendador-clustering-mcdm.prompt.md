---
description: 'Construye el Modelo 5: clustering K-Means/GMM de tipologías territoriales + ranking MCDM por perfil ciudadano con exclusión'
agent: 'agent'
tools: ['search/codebase', 'edit/editFiles', 'runCommands']
argument-hint: '[perfil=joven|familia|teletrabajo|mayor]'
---

# Modelo 5 — Recomendador Inteligente (Clustering + MCDM)

## Misión

Implementar el **recomendador**:
1. **Segmentar** los 41 municipios en **tipologías territoriales** con K-Means / Gaussian Mixture
   Model (no supervisado), con nombres accionables ("nodos metropolitanos dinámicos",
   "municipios familiares de calidad ambiental", "pueblos rurales conectados para teletrabajo").
2. **Rankear** municipios para el perfil ciudadano del cuestionario, con **similitud del coseno
   ponderada (MCDM)** y **ranking de exclusión** (municipios que incumplen criterios duros
   quedan fuera aunque encajen en lo demás).

## Alcance y precondiciones

- Precondición: sub-índices de M2, precio de M1, proyección de M3 disponibles.
- Alcance: `src/lodcore/models/m5_recommender/`.

## Inputs

- `${input:perfil}` — `joven` | `familia` | `teletrabajo` | `mayor` (por defecto: todos).

## Workflow

### 1. Preprocessing para clustering
- Usa los **sub-índices de M2** + variables estructurales: `log(poblacion)`, densidad, % joven,
  % 65+, precio €/m², gap de accesibilidad 30 min, % empleo local, tasa de teletrabajo (proxy),
  presupuesto per cápita.
- `StandardScaler` (aquí **sí** tiene sentido estandarizar: el clustering no tiene split).
- **No** uses más variables que el número de municipios permite: con n=41, más de ~8-10 variables
  por cluster produce clusters degenerados. Justifica el número.

### 2. K-Means vs GMM: elige con evidencia
- Ejecuta ambos con `k` de 2 a 8.
- Criterios de selección: **BIC** (GMM), **AIC** (GMM), **silueta**, **Calinski-Harabasz**,
  **Davies-Bouldin**, y **estabilidad** por bootstrap (reajusta el modelo sobre el 80 % de los
  municipios y mide la consistencia de las asignaciones con el índice ARI).
- **Tabla comparativa obligatoria** con los 5 criterios por cada `k` y cada algoritmo.
- Regla: con n=41, el modelo más parsimonioso que no colapse es el que se usa. **Reporta también
  el mejor `k` por silueta** aunque no lo elijas, y explica por qué difiere.
- **Perfil de las siluetas**: si algún punto tiene silueta muy negativa (< -0.2), es un municipio
  mal clasificado → **márcalo como "atípico"** en la APP en vez de forzarle un clúster.

### 3. Nombrar los clusters (el paso que casi nadie hace bien)
Para cada cluster, genera un nombre basándote en:
- **Variables con mayor |loading| centroide** del cluster.
- **Perfil relativo**: en qué se diferencia de la media de los 41.
- **Naming verificable**: el nombre debe ser **comprobable con datos**. Ejemplo: "Pueblos rurales
  conectados" solo si ese cluster (a) tiene el mayor gap de accesibilidad *favorable*,
  (b) la mayor densidad de zonas verdes, (c) el mayor % de teletrabajo estimado.
- **Valida el nombre con los propios datos** y, si no se sostiene, renómbralo.
- Documenta para cada cluster: **municipios miembros**, **perfil relativo** (3-5 variables con su
  z-score), y **qué lo distingue** de los demás.

### 4. MCDM: el motor de ranking
El proyecto especifica *"similitud del coseno ponderada (MCDM)"*. Implementa:

**Vector de preferencias** (del cuestionario): `w ∈ R⁺` sobre los criterios
(Coste de vida, Conectividad, Servicios, Calidad ambiental, Empleo local, Espacio, Seguridad,
Ocio). Suma 1.

**Normalización**: los criterios son "más es mejor" o "menos es mejor" (precio = menos es mejor).
Normaliza a [0,1] con **MinMax sobre los 41 municipios** (la escala es relativa a la muestra:
documenta que un municipio con precio 2000 € es "0" en este conjunto).

**Score**:
```
score(m) = Σ_i w_i * v_i(m)            # suma ponderada (SAW)
```
Y en paralelo, **similitud del coseno** entre el vector de preferencias del usuario y el vector
normalizado del municipio:
```
sim(m) = cos( w , v(m) )
```
Documenta por qué difieren: SAW favorece a los municipios **excelentes en todo**; la similitud
del coseno favorece a los que **se parecen al perfil ideal** (puede ser malo en una dimensión).
**Recomendación: score final = α·SAW + (1−α)·sim**, con α justified y validado contra un
conjunto de casos de prueba.

**Métodos MCDM alternativos a implementar y comparar** (usa `pymcdm` o `scikit-criteria`):
- **TOPSIS** (distancia a la solución ideal) — es el más intuitivo para "el municipio que más se
  parece a mi perfil ideal".
- **VIKOR** (compromiso entre cercanía y#"deseable").
- **ELECTRE** (no compensatorio, útil para el "ranking de exclusión").
- **SAW** (base, multiplicativo).
Compara el ranking resultante de cada método con **Kendall's tau** para medir sensibilidad.

### 5. Ranking de exclusión (requisito explícito)
Un municipio **queda excluido** del ranking si incumple un **criterio duro**, con independencia
de su score:
- `hab_por_medico > 1500` (colapso sanitario).
- `ocupacion_aulas > 95 %` bajo el escenario de estrés de referencia.
- `ICA < 40` (semáforo bajo).
- El municipio **no tiene** ninguna vivienda disponible en venta (oferta = 0) → no es una opción
  de reubicación real.
- No cumple un requisito **declarado por el usuario** en el cuestionario (p. ej. "necesito
  colegio de secundaria a < 20 min").
**Presenta la exclusión como información, no como silencio**: "Excluidos 2 municipios por
colapso sanitario: A (1.812 hab/médico), B (1.640 hab/médico)".

### 6. Restricciones del cuestionario → filtros duros y blandos
El cuestionario produce restricciones **duras** (presupuesto máximo, necesidad de colegio,
disponibilidad deayed) y **blandas** (preferencias). Trátalas distinto:
- Duras → **filtro previo** (excluir) o **restricción dura del score** (TOPSIS con restricciones).
- Blandas → pesos.
Documenta el mapping completo questionnaire → pesos/filtros en un archivo de configuración,
no en código.

### 7. Comparador (hasta 3 municipios)
- Devuelve las features normalizadas de 3 municipios para el radar chart de la APP:
  los 6 ejes que ya aparecen en el prototipo (**Sanidad, Educación, Conectividad, Asequibilidad,
  Medioambiente, y el 6º eje del prototipo**) + el score final y el cluster.
- Aplica **normalización común** para que el radar sea comparable.

### 8. Validación
- ¿El ranking es **estable**? Bootstrap los 41 municipios y recalcula el ranking: mide la
  frecuencia con la que cada municipio aparece en el top-5. Reporta la **estabilidad por
  municipio** (un municipio inestable debe marcarse como "resultado sensible a los datos").
- ¿Los clusters son **espacialmente coherentes**? Calcula el índice de Moran de la asignación
  al cluster o la dispersión espacial: si los clusters mezclan municipios contiguos, puede
  indicar que falta una variable espacial.
- **Test de coherencia con el mundo**: ¿el cluster "pueblos rurales conectados" incluye
  municipios que *realmente* lo son? Verifícalo con las variables que lo definen, no con la
  intuición.

## Output Expectations

1. `src/lodcore/models/m5_recommender/` (`cluster.py`, `mcdm.py`, `questionnaire.py`,
   `exclude.py`, `evaluate.py`, `model_card.md`).
2. `reports/m5_recommender.md`:
```
# M5 — Recomendador
## Tabla comparativa K-Means vs GMM: k=2..8 × (BIC, AIC, silueta, CH, DB, ARI bootstrap)
## k elegido y justificación
## Perfil de cada cluster: miembros | variables con mayor z-score | nombre asignado | verificación del nombre
## Municipios atípicos (silueta < -0.2)
## Métodos MCDM comparados: ranking top-5 de cada uno + Kendall tau entre métodos
## Fórmula final del score y valor de α justificado
## Ranking de exclusión: reglas y resultado por perfil
## Estabilidad del ranking (frecuencia top-5 por municipio)
## Configuración del cuestionario → pesos/filtros (tabla)
```
3. `model_card.md` de M5, incluyendo la advertencia de que la normalización MinMax hace que
   los scores sean **relativos a la muestra de 41 municipios**.

## Quality Assurance

- [ ] He comparado K-Means y GMM con BIC/silueta/estabilidad; no he elegido por intuición.
- [ ] Los nombres de cluster son **verificables con datos** y he mostrado la verificación.
- [ ] He comparado ≥ 3 métodos MCDM y medido la concordancia (Kendall tau).
- [ ] Los criterios duros **excluyen**; los blandos **ponderan**. No están mezclados.
- [ ] Las exclusiones se muestran al usuario, no se ocultan.
- [ ] He medido la estabilidad del ranking con bootstrap.
- [ ] Todos los pesos del cuestionario están en configuración, no hardcodeados.
- [ ] `model_card.md` advierte que los scores son relativos a la muestra.
