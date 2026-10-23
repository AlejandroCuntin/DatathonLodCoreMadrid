---
description: 'Audita la calidad y la trazabilidad del dataset municipal: nulos, imputaciones, procedencia y saltos de cobertura'
agent: 'agent'
tools: ['search/codebase', 'edit/editFiles', 'runCommands']
argument-hint: '[ruta_del_dataset]'
---

# Auditoría de calidad y procedencia del dataset municipal

## Misión

Auditar el dataset (panel de municipios × años × variables) y producir un informe **accionable**
que certifique o desmienta que el dataset cumple el requisito del proyecto: **distinguir
explícitamente valores observados, imputados/estimados, proyectados y simulados**.

Un dataset sin procedencia no es publicable en este proyecto.

## Alcance y precondiciones

- Precondición: existe el dataset en formato largo con columnas
  `municipio_ine, anio, variable_id, valor, unidad, origen, metodo, fuente_url`.
- Alcance: **solo lectura** salvo que se te pida escribir un script de auditoría reutilizable.
- Si el dataset no tiene columna `origen`, **no lo inventes**: repórtalo como hallazgo crítico
  y propón el esquema de fijación.

## Inputs

- `${input:dataset}` — ruta al parquet/csv a auditar (obligatorio).
- `${input:variables}` — lista opcional de variables a priorizar.

## Workflow

1. **Perfila** con `ydata-profiling` (modo `minimal=True` si el dataset es grande) y guarda el
   HTML en `reports/`. No lo imprimas entero: resume.
2. **Cobertura temporal y espacial**: por variable, ¿qué años cubre cada municipio? Detecta
   municipios que entran o salen del panel (`panel_entry` / `panel_exit`) y reporta su año.
   Un municipio con cobertura irregular altera denominadores (hab/médico, % ocupación).
3. **Nulos por variable y por municipio**: clasifica cada nulo como
   (a) *no aplicable* (p. ej. un municipio sin centro educativo),
   (b) *falta real de dato*,
   (c) *dato no publicado ese año*.
   Cada clase requiere tratamiento distinto y solo (b) y (c) pueden imputarse.
4. **Audita la imputación**: ¿qué método se usó, con qué datos, qué variables auxiliares y con
   qué banda de error? ¿Se puede reproducir? Si el método no está registrado, es un hallazgo crítico.
5. **Coherencia entre variables derivadas**: recalcula de forma independiente al menos
   `hab/medico`, `ratio_sanitario` y `ocupacion_aulas` para una muestra de municipios y compara
   con el valor almacenado. Tolerancia: 0,5 %. Reporta las desviaciones.
6. **Outliers**: usa box plot y regla 3σ **dentro de cada municipio** (serie temporal) y también
   entre municipios del mismo año. Un municipio pequeño puede ser legítimamente un outlier.
   Clasifica cada outlier como *error de captura* | *valor real extremo* | *imputación defectuosa*.
7. **Duplicados y claves**: unicidad de `(municipio_ine, anio, variable_id)`.
8. **Procesamiento por lotes** si el dataset no cabe en memoria: `chunksize` + agregación.

## Output Expectations

Informe markdown en `reports/audit_{timestamp}.md` con:

```
# Auditoría de calidad — <dataset>
## 1. Veredicto
APTO / APTO CON RESERVAS / NO APTO   + 1 párrafo justificando
## 2. Resumen tabular
| variable_id | n_filas | n_municipios | rango_años | %nulos | %OBSERVADO | %IMPUTADO | %PROYECTADO | %SIMULADO | cober_mín_años |
## 3. Hallazgos críticos (bloqueantes)
## 4. Hallazgos mayores
## 5. Hallazgos menores
## 6. Tabla de imputaciones (variable | método | auxiliares | banda | reproducible sí/no)
## 7. Outliers clasificados
## 8. Plan de corrección priorizado (acción | esfuerzo | impacto | bloqueante sí/no)
## 9. Decisión: ¿puede este dataset alimentar el entrenamiento de los modelos?
```

Cada hallazgo debe llevar: **evidencia concreta** (número de filas, municipios, valores),
**por qué importa** para el modelo al que alimenta, y **acción** concreta.

## Quality Assurance

- [ ] He verificado que cada fila tiene `origen` ∈ {OBSERVADO, IMPUTADO, ESTIMADO, PROYECTADO, SIMULADO}.
- [ ] No he derivado de forma circular (recalcular una variable a partir de ella misma).
- [ ] He separado *no aplicable* de *falta de dato* antes de recomendar imputación.
- [ ] Cada hallazgo crítico cita números, no adjectives.
- [ ] El informe dice explícitamente si el dataset puede alimentar M1/M2/M3/M4/M5 o solo algunos.
- [ ] `uv run pytest -q` sigue pasando (no he tocado el dataset original).
