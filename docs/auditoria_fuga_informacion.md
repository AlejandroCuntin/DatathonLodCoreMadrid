# Auditoría de Fuga de Información — F3
## Modelo M4 (ICA) · Panel Municipal LoDCORE Madrid · `v1.0.0-F2`

> **Alcance:** auditoría metodológica del pipeline de M4 sobre el panel de **20 municipios y 8
> comarcas**. No evalúa la calidad del modelo, sino si puede usar información que no estaría
> disponible en el momento de la decisión.
> **Fecha:** 24 de octubre de 2026. **Reproducible con:** `python scripts/audit_f3_leakage.py`.

---

## Veredicto

**0 bloqueantes · 2 materiales · 5 limpias/controladas.**

| Tipo | Resultado |
|---|---|
| **L1 — CV aleatorio sobre el panel** | **LIMPIA / CONTROLADA.** Se usa `GroupKFold` por comarca. La diferencia máxima entre CV aleatorio y CV agrupado es **+0,062 de R²**, por debajo del umbral de 0,15 que indicaría fuga material. |
| **L2 — Fuga temporal** | **CONTROLADA, con limitación estructural.** El panel tiene un único corte (24-10-2026) y no hay serie histórica; no es posible un split temporal real. Se aplica filtro de punto-en-tiempo y ninguna variable futura entra en M4. |
| **L3 — Variable derivada del objetivo** | **MATERIAL (interpretativa).** El ICA es una combinación determinista de los sub-índices. Incluir el target o sus derivados dispara el R² (**+0,18**). El baseline actual no los incluye, pero el R² debe leerse como *aproximación de una fórmula*, no como capacidad predictiva. |
| **L4 — Fuga entre fases (M3 → M4)** | **LIMPIA.** Las proyecciones de M3 no están en `FEATURES_M4`; añadir `poblacion_2031` **no mejora** el R² (0,716 vs 0,735) y hay test que lo impide. |
| **L5 — Fuga por normalización** | **LIMPIA.** M4 no usa `StandardScaler`, `MinMaxScaler` ni `Pipeline`; no hay ajuste previo al split. |
| **L6 — Imputación leaking** | **LIMPIA.** No hay imputador; el panel tiene **0 nulos**. |
| **L7 — Duplicación de filas** | **LIMPIA.** 20 municipios, **1 fila por municipio**, 0 duplicados exactos. |
| **Sesgo de selección** | **MATERIAL.** El piloto sobrerrepresenta municipios medianos (5.000–20.000) e infrarrepresenta los pequeños (<5.000). Debe declararse. |

---

## 1. Tabla de disponibilidad (as-of) por variable

| Variable / grupo | Fuente | Fecha de publicación / referencia | ¿Disponible en scoring? | Veredicto |
|---|---|---|---|---|
| `poblacion_actual`, `anio_padron` | INE, tabla 2881 | Referencia 1-ene-2025; snapshot 24-10-2026 | Sí | **DISPONIBLE** |
| `num_centros_salud` | CKAN CAM, sanidad | Último año 2024; metadatos modificados 06-08-2026 | Sí | **DISPONIBLE** |
| `num_centros_educativos` | CKAN CAM, educación | Metadatos modificados 05-05-2026 | Sí | **DISPONIBLE** |
| `num_medicos_ap`, `num_plazas_escolares`, `num_alumnos_matriculados`, vivienda, precios | Calibración interna (seed 2026) | Generado en cada ejecución | Sí, pero **no es dato oficial** | **DISPONIBLE (calibrado)** |
| `score_sanidad`, `score_educacion`, `score_conectividad`, `score_vivienda`, `score_holgura` | Derivados del panel F2 | — | Son **componentes del target** | **NO USAR COMO FEATURE para predecir ICA** |
| `indice_capacidad_global` (target) | Fórmula determinista | — | Es el target | **TARGET** |
| `nivel_idoneidad`, `ranking_ica` | Derivados del target | — | No | **NO USAR COMO FEATURE** |
| `poblacion_2027/2029/2031`, `anio_estimado_saturacion`, `alerta_planificacion` | M3 (proyección) | Horizonte futuro | Solo como escenario | **REQUIERE PROYECCIÓN** |
| `fecha_disponible`, `fecha_carga`, `fecha_calculo`, `origen`, `metodo`, `dataset_version` | Metadatos | — | No son features | **NO APLICA** |
| Textos (`*_detalle`, `patrimonio_entorno`, `observaciones_acogida`), `img_local` | Referencia curada | — | No son features | **NO APLICA** |

**Fechas del panel:** `fecha_disponible = 2026-10-24`; `fecha_decision` del MVP = `2026-10-24`.
No hay ninguna fila con `fecha_disponible > fecha_decision`.

---

## 2. Hallazgos

### [LIMPIA] L1 — CV aleatorio sobre el panel

**Evidencia:** `src/lodcore/models/m4_capacidad/train.py` usa `GroupKFold` con `groups=comarca`.
`tests/integration/test_no_leakage.py` comprueba que train y test no comparten comarca.
**Cuantificación:** comparación CV aleatorio vs agrupado (misma semilla y modelo):

| Configuración | R² GroupKFold | R² KFold aleatorio | Δ R² |
|---|---:|---:|---:|
| E1 variables crudas | 0,7861 | 0,8482 | **+0,062** |
| E0 baseline M4 | 0,7355 | 0,7809 | **+0,045** |
| E2 baseline + holgura | 0,7344 | 0,7533 | +0,019 |
| E5 baseline + población 2031 | 0,7164 | 0,7514 | +0,035 |

**Impacto:** el máximo es +0,062, por debajo del umbral 0,15. **No hay fuga espacial material.**
**Fix:** mantener `GroupKFold` y no publicar nunca métricas con KFold aleatorio.

### [CONTROLADA] L2 — Fuga temporal

**Evidencia:** el panel es un corte único (todas las filas, `fecha_disponible = 2026-10-24`).
No existe serie histórica municipal para hacer `TimeSeriesSplit`. El pipeline aplica
`filtrar_point_in_time(..., fecha_decision="2026-10-24")` y `test_no_leakage` verifica que M4
no usa columnas futuras de M3.
**Impacto:** no hay fuga temporal explotable, pero **no se puede afirmar generalización temporal**.
**Fix (declararlo):** en la model card y en la presentación, decir «validación espacial, no temporal».

### [MATERIAL, interpretativa] L3 — Variables derivadas del objetivo

**Evidencia:** el ICA es exactamente
`0,30·score_vivienda + 0,30·(score_sanidad+score_educacion)/2 + 0,25·score_conectividad + 0,15·score_holgura`.
El baseline incluye **4 de esos 5 componentes**. R² in-sample = **1,0000** (memoriza 20 filas).
Añadir el target o sus derivados infla el R² fuera de muestra:

| Experimento | R² OOF | MAE | Δ R² vs baseline |
|---|---:|---:|---:|
| E0 baseline | 0,7355 | 4,97 | — |
| E3 baseline + `indice_capacidad_global` | **0,9218** | 2,49 | **+0,186** |
| E4 baseline + `nivel_idoneidad` + `ranking_ica` | **0,9178** | 2,79 | **+0,182** |
| E2 baseline + `score_holgura` | 0,7344 | 5,33 | −0,001 |

**Lectura honesta:** el R² de 0,73 no mide «predicción»; mide cuánto se aproxima una fórmula
determinista con 20 municipios. Añadir el target lo sube a 0,92, que es la prueba de que la
métrica premia la tautología. **No hay fuga en el baseline actual**, pero el discurso debe ser
«modelo de scoring determinista», no «modelo predictivo».
**Dato adicional:** la importancia de features está dominada por `hab_por_medico` (0,749); los
scores aportan ~0,06 cada uno. El modelo captura sobre todo la **regla dura**, no la fórmula.
**Fix aplicado:** test `test_m4_no_usa_variables_derivadas_del_target` (F3) que impide que el
target, `nivel_idoneidad`, `ranking_ica`, `alerta_planificacion` o `anio_estimado_saturacion`
entren en `FEATURES_M4`.

### [LIMPIA] L4 — Fuga entre fases (M3 → M4)

**Evidencia:** `FEATURES_M4` no contiene `poblacion_2027/2029/2031` ni `anio_estimado_saturacion`;
`test_no_leakage_between_m3_future_and_m4_features` lo verifica.
**Cuantificación:** añadir `poblacion_2031` **empeora** el R² (0,7164 vs 0,7355), luego no hay
beneficio de fuga.
**Fix:** mantener el test en CI.

### [LIMPIA] L5 — Normalización

**Evidencia:** búsqueda de `StandardScaler|MinMaxScaler|Pipeline|fit_transform` en
`m4_capacidad/train.py` y `models/base.py`: **sin resultados**. M4 entrena con las variables tal cual.
**Impacto:** no puede haber fuga por ajustar el escalador con todo el dataset.

### [LIMPIA] L6 — Imputación

**Evidencia:** no hay `SimpleImputer`/`KNNImputer`; el panel validado tiene **0 valores nulos**.
**Impacto:** no aplica.

### [LIMPIA] L7 — Duplicación de filas

**Evidencia:** 20 filas, 20 códigos INE únicos, 1 fila por municipio, 0 duplicados exactos.
**Impacto:** no hay filas casi idénticas entre train y test.

### [MATERIAL] Sesgo de selección

**Evidencia (piloto vs municipios <50k del INE):**

| Métrica | Piloto (20) | Municipios <50k CAM (155) |
|---|---:|---:|
| N | 20 | 155 |
| Población mediana | **8.219** | **2.964** |
| Población total | 200.267 | 997.059 |
| <5.000 hab. | 4 (20 %) | 96 (62 %) |
| 5.000–20.000 | **14 (70 %)** | 46 (30 %) |
| 20.000–50.000 | 2 (10 %) | 13 (8 %) |

**Lectura:** el piloto **sobrerrepresenta los municipios medianos (5–20k)** y **infrarrepresenta
los pequeños (<5k)**. No es *survivorship* (no se excluyó por falta de datos, se eligió por diseño),
pero **limita la validez externa**. Los resultados no se pueden extrapolar sin más a los 155.
**Fix (declararlo):** en la model card y en la presentación; en la siguiente iteración, estratificar
por tamaño o ampliar a los 155.

---

## 3. Tabla de experimentos (con vs sin leakage)

Mismo modelo (`GradientBoostingRegressor`, 120 árboles, lr 0,05, profundidad 3, semilla 2026) y
mismo panel. R²/MAE/RMSE **out-of-fold**.

| Experimento | CV | R² | MAE | RMSE |
|---|---|---:|---:|---:|
| E1 variables crudas (sin scores) | GroupKFold | 0,7861 | 5,07 | 6,05 |
| E1 variables crudas (sin scores) | KFold aleatorio | 0,8482 | 4,12 | 5,09 |
| **E0 baseline M4** | **GroupKFold** | **0,7355** | **4,97** | **6,72** |
| E0 baseline M4 | KFold aleatorio | 0,7809 | 4,41 | 6,12 |
| E2 baseline + `score_holgura` | GroupKFold | 0,7344 | 5,33 | 6,74 |
| E3 baseline + target | GroupKFold | 0,9218 | 2,49 | 3,66 |
| E4 baseline + nivel + ranking | GroupKFold | 0,9178 | 2,79 | 3,75 |
| E5 baseline + `poblacion_2031` | GroupKFold | 0,7164 | 5,29 | 6,96 |

> **Nota sobre `metrics.json`:** el pipeline publica R² = 0,7345 y MAE = 5,15. Aquí sale R² = 0,7355
> y MAE = 4,97 porque `metrics.json` promedia el MAE de los 5 folds y esta auditoría calcula el MAE
> sobre las predicciones out-of-fold. La diferencia es de cálculo, no de datos. El R² es equivalente.

---

## 4. Qué NO está leaking (descartado con evidencia)

- **CV aleatorio:** diferencia máxima +0,062 < 0,15 (tabla L1).
- **Temporal:** corte único; filtro de punto-en-tiempo; sin columnas futuras en M4 (L2).
- **Entre fases:** M3 no entra en M4; añadirlo no mejora (L4).
- **Normalización:** no hay scaler (L5).
- **Imputación:** no hay imputer y 0 nulos (L6).
- **Duplicados:** 1 fila por municipio (L7).
- **Target como feature:** no está en `FEATURES_M4`; nuevo test lo bloquea (L3).
- **Fechas:** `fecha_disponible ≤ fecha_decision` en las 20 filas.

---

## 5. Plan de corrección priorizado

| Prioridad | Acción | Estado |
|---|---|---|
| 1 | Test que impide target/derivados en `FEATURES_M4` | **Hecho** (`test_m4_no_usa_variables_derivadas_del_target`) |
| 2 | Etiquetar M4 como *scoring determinista / surrogate*, no predicción | **Hecho** en `docs/validacion.md` y `metrics.json` (advertencia); reforzar en la model card F13 |
| 3 | Declarar el sesgo de selección (20/155; mediana 8.219 vs 2.964) en model card y presentación | Pendiente (F13) |
| 4 | No usar nunca KFold aleatorio para métricas publicadas | Regla de equipo |
| 5 | Evaluar con P2 un M4 con variables crudas (E1: R² 0,786 vs 0,735) | Opcional, post-datathon |
| 6 | F4: asumir que no hay validación temporal posible; usar CV espacial + bootstrap y decirlo | F4 |

---

## 6. Reproducibilidad

```powershell
python scripts/audit_f3_leakage.py
python -m pytest tests/integration/test_no_leakage.py -q
```

Salida esperada: la tabla de experimentos de la sección 3, las correlaciones con el target y el
bloque de sesgo de selección. El script no modifica datos ni artefactos.
