# Model Cards — LoDCORE Madrid
## II Datathon LoDCOREMadrid 2026 · `dataset_version = v1.0.0-F2`

> **Qué es este documento (F13.1):** una ficha por modelo con lo que hace, lo que **no** hace,
> cómo se ha validado y, sobre todo, **dónde falla**, con un municipio concreto como ejemplo.
> **Regla:** cada número de estas fichas existe en un artefacto del repositorio (sección final
> de cross-check). **Fecha:** 24 de octubre de 2026. **Alcance:** piloto de 20 municipios y 8 comarcas.

---

## M1 — Precio de referencia y asequibilidad (AVM)

| Campo | Valor |
|---|---|
| Versión | `M1_AVM_HEDONICO` · `v1.0.0-F2` |
| Responsable | P2 (modelos) |
| Target | `precio_m2_compra` (€/m²) — **variable calibrada, no precio observado** |
| Features | tiempo a Madrid, densidad, fibra, paradas/1.000 hab, viviendas vacías/1.000 hab, médicos/1.000 hab, holgura escolar |
| Validación | `GroupKFold` espacial por comarca (5 folds) |
| Estado | **Ilustrativo**. No es un AVM comercial ni una tasación. |

**Qué hace:** da un precio de referencia relativo para comparar asequibilidad entre municipios y calcular el esfuerzo financiero familiar.
**Qué no hace:** no tasa una vivienda concreta, no sustituye una valoración homologada y no estima el precio de mercado con precisión comercial.

### Métricas auditadas

| Métrica | Valor | Fuente |
|---|---:|---|
| MAE CV (media de folds) | **382,83 €/m²** (± 230,20) | `m1_avm/metrics.json` → `mae_cv_mean`, `mae_cv_std` |
| R² CV (OOF) | **−0,3398** | `m1_avm/metrics.json` → `r2_cv_oof` |
| R² in-sample | 0,8032 | `m1_avm/metrics.json` → `r2_in_sample` |
| Equivalencia ONNX (abs / rel) | 5,47e−4 / 3,65e−7 | `m1_avm/metrics.json` |

### Límites y riesgos conocidos

1. **Con n=20 el R² fuera de muestra es negativo.** El modelo no bate a la media de forma consistente. Ejemplo: **Manzanares el Real** (precio real 2.450 €/m²; predicción OOF 1.466 €/m²; error −984 €/m²).
2. **El target es sintético.** El “precio” del panel es calibración (seed 2026), no un precio escriturado. Ejemplo: **Colmenar de Oreja** (real 1.150; predicción 1.849; error +699) refleja el artefacto de calibración, no una oportunidad de mercado.
3. **No hay validación temporal.** Solo existe un corte (24-10-2026); no se puede afirmar que el modelo prediga precios futuros.
4. **No es una tasación.** No debe usarse para hipotecas, impuestos, herencias ni decisiones de compra concreta.
5. **Sesgo de selección.** Los 20 municipios no representan a los 155 menores de 50k (son más medianos: mediana 8.219 vs 2.964).

**Uso previsto:** indicador de esfuerzo financiero relativo y de oportunidad de asequibilidad.
**No usar para:** tasación oficial, concesión de crédito o fijación de precios.

---

## M2 — Indicadores de capacidad e isócronas de 30 minutos

| Campo | Valor |
|---|---|
| Versión | `M2_PCA_HEURISTICA_30MIN` · `v1.0.0-F2` |
| Responsable | P2 (modelos) |
| Target | No supervisado (4 subíndices PCA 0–100) |
| Entradas | médicos/1.000, centros de salud/10.000, holgura escolar, centros educativos/1.000 alumnos, fibra, paradas, vivienda, superficie |
| Validación | Determinista; sin target que predecir |
| Estado | **Heurística descriptiva**, no rutas reales. |

**Qué hace:** resume decenas de variables en 4 subíndices comparables y estima si un municipio está a menos de 30 minutos.
**Qué no hace:** no calcula rutas reales sobre OSM ni horarios GTFS; no da tiempos de viaje certificados.

### Métricas auditadas

| Métrica | Valor | Fuente |
|---|---:|---|
| Varianza explicada PC1 | **0,7004** | `m2_indicadores/metrics.json` |
| Municipios ≤30 min (privado) | **16/20** | `m2_indicadores/metrics.json` |
| Municipios ≤30 min (público) | **8/20** | `m2_indicadores/metrics.json` |

### Límites y riesgos conocidos

1. **La isócrona es una heurística**, no un ruteo multimodal. Ejemplo: **Rascafría** (85 min, 38 paradas) y **Montejo de la Sierra** (85 min, 5 paradas) reciben el mismo tiempo estimado aunque su accesibilidad real es muy distinta.
2. **El PCA se ajusta con los 20 municipios.** Los subíndices son relativos a esta muestra; no son portables a un municipio nuevo sin reajustar el escalador/PCA.
3. **El umbral de 30 minutos es un parámetro de planificación del MVP**, no una norma oficial.
4. **No hay horarios reales de CRTM ni Renfe.** Las paradas son referencia curada; el conector GTFS está pendiente.

**Uso previsto:** cribado comparativo y visualización de holgura.
**No usar para:** planificación de rutas, promesas de tiempo de viaje o comparación con municipios fuera del panel.

---

## M3 — Proyección demográfica a 5 y 10 años

| Campo | Valor |
|---|---|
| Versión | `M3_DEMOGRAFIA_EXTRAPOLACION_GEOMETRICA` · `v1.0.0-F2` |
| Responsable | P2 (modelos) |
| Target | Población futura (2030/2035) y año de saturación |
| Método | Extrapolación geométrica calibrada con la proyección padronal 2031; bandas 95 %; escenarios +5 % / +10 % |
| Estado | **Proyección calibrada**, no SARIMAX ni Prophet. |

**Qué hace:** estima la población a 5/10 años y el año en que se satura el factor limitante.
**Qué no hace:** no es un modelo de series temporales con backtest; no incorpora cambios de política, economía o migración no observados.

### Métricas auditadas

| Métrica | Valor | Fuente |
|---|---:|---|
| Población 2025 | **200.267** | `m3_demografia/metrics.json` |
| Población 2030 | **216.597** | `m3_demografia/metrics.json` |
| Población 2035 | **234.336** | `m3_demografia/metrics.json` |

### Límites y riesgos conocidos

1. **Se calibra con la proyección 2031**, que es un valor futuro. Por tanto, 2030/2035 **no son independientes** de esa referencia; no hay backtest temporal posible con un solo corte.
2. **Municipios pequeños = mucha volatilidad.** Ejemplo: **Montejo de la Sierra** (404 → 421 hab. en 2031; +4,2 %), donde un error de 20 personas cambia la conclusión de capacidad.
3. **Los extremos de crecimiento son difíciles.** Ejemplo: **Ciempozuelos** y **Navalcarnero** (+13,3 % en 2031) frente a **Robledo de Chavela** (+4,3 %); el modelo no distingue por sí solo un cambio de tendencia.
4. **El año de saturación depende de la capacidad estática.** Ejemplo: **Navalcarnero** y **Ciempozuelos** aparecen saturados ya en 2025; si se amplía un servicio, la fecha cambia y el modelo no lo sabe hasta que se recalcula.
5. **Las bandas son del modelo**, no empíricas; deben presentarse como horquilla, no como intervalo certificado.

**Uso previsto:** planificación a medio plazo y escenarios.
**No usar para:** previsión oficial de población ni decisiones de inversión sin contraste con las proyecciones del INE.

---

## M4 — Capacidad de acogida (ICA) — modelo core

| Campo | Valor |
|---|---|
| Versión | `M4_CAPACIDAD_ACOGIDA` · `v1.0.0-F2` |
| Responsable | P2 (modelo) + P1 (reglas) |
| Target | `indice_capacidad_global` (ICA 0–100) |
| Features | 4 subíndices + hab/médico + ocupación escolar + vivienda vacía + suelo |
| Validación | `GroupKFold` espacial por comarca + baselines + bootstrap B=1000 |
| Estado | **Modelo de scoring determinista**; no es un predictor de fenómenos futuros. |

**Qué hace:** aproxima el ICA, aplica reglas no compensatorias y alimenta el simulador what-if.
**Qué no hace:** no “predice” la capacidad futura; no sustituye la decisión del gestor.

### Métricas auditadas

| Métrica | Valor | Fuente |
|---|---:|---|
| MAE CV (media de folds) | **5,15 ptos** (± 2,41); OOF 4,95 | `m4_capacidad/metrics.json`; `evaluate.py` |
| R² CV (OOF) | **0,7345** | `m4_capacidad/metrics.json` |
| R² in-sample | 1,0000 (esperado) | `m4_capacidad/metrics.json` |
| Equivalencia ONNX (abs / rel) | 1,03e−5 / 2,29e−7 | `m4_capacidad/metrics.json` |
| Ridge (baseline) | R² 0,9264 / MAE 2,78 | `docs/validacion.md` §6.2 |

### Límites y riesgos conocidos

1. **El target es una fórmula, no un fenómeno independiente.** El ICA es una combinación determinista de los subíndices y `FEATURES_M4` contiene 4 de sus 5 componentes; el R² mide la aproximación de la fórmula. Un R² in-sample de 1,0 es memorización.
2. **Un modelo lineal predice mejor.** **Ridge** obtiene R² 0,9264 y MAE 2,78, por encima de M4 (0,7345 / 4,95). M4 se mantiene por las reglas no compensatorias, las atribuciones y el what-if, no por precisión.
3. **Errores altos en municipios concretos.** Ejemplo: **Soto del Real** (ICA real 22,8; predicción OOF 38,3; error +15,5) y **Robledo de Chavela** (66,7 → 54,4; −12,3). El modelo puede mover un municipio de semáforo.
4. **Sesgo de selección.** 20 de 155 municipios <50k; mediana 8.219 vs 2.964; sobrerrepresenta 5–20k. No se extrapola sin más a los 155.
5. **Sin validación temporal.** Un solo corte; no se afirma generalización en el tiempo.
6. **Los umbrales 1.500 hab/médico y 95 % de ocupación son parámetros del MVP**, no normativa. Ejemplo: **Navalcarnero** y **Ciempozuelos** quedan en alerta por estos umbrales; con otro umbral, cambiaría el semáforo.

**Uso previsto:** scoring, diagnóstico de cuellos de botella, what-if y asignación presupuestaria.
**No usar para:** decisión automática de inversión sin revisión humana.

---

## M5 — Recomendador ciudadano (clustering + MCDM)

| Campo | Valor |
|---|---|
| Versión | `M5_CLUSTERING_MCDM_COSINE` · `v1.0.0-F2` |
| Responsable | P2 (modelos) |
| Target | No supervisado (4 clústeres) + ranking por similitud coseno |
| Features | scores de sanidad, educación, conectividad y vivienda + tiempo a Madrid + precio + densidad |
| Validación | Silhouette + inspección de centroides |
| Estado | **Descriptivo**, no predictivo. |

**Qué hace:** agrupa municipios en 4 arquetipos y ordena municipios según las preferencias del ciudadano.
**Qué no hace:** no asigna un arquetipo “verdadero” ni garantiza que el clúster se mantenga al ampliar la muestra.

### Métricas auditadas

| Métrica | Valor | Fuente |
|---|---:|---|
| k | **4** | `m5_recomendador/metrics.json` |
| Silhouette | **0,3183** | `m5_recomendador/metrics.json` |
| Inercia | **39,01** | `m5_recomendador/metrics.json` |
| Tamaños de clúster | 6 / 4 / 6 / 4 | `m5_recomendador/clustering.json` |

### Límites y riesgos conocidos

1. **La estructura es débil-media** (silhouette 0,3183). No es una segmentación natural fuerte; es una agrupación útil para describir, no para certificar.
2. **El panel y M5 no coinciden.** La columna `arquetipo_nombre` del panel conserva una asignación antigua (11/6/2/1) mientras que la salida vigente de M5 es 6/4/6/4. Ejemplo: **Meco** aparece en el panel como “Retiro Silver Economy y Alta Calidad Ambiental”, pero M5 lo asigna a otro clúster. Hay que regenerar `arquetipo_nombre`/`arquetipo_codigo` desde `clustering.json` antes de publicar.
3. **Los nombres son interpretación, no etiquetas oficiales.** `clustering.json` usa `Cabeceras Comarcales Equilibradas`, `Nodos Metropolitanos y Corredores Dinámicos`, `Pueblos Conectados de Calidad Ambiental y Teletrabajo` y `Reserva de Oportunidad Residencial y Suelo Asequible`; el panel usa otra nomenclatura.
4. **Con 20 municipios, los clústeres cambian si se amplía la muestra.** No son universales.
5. **El ranking es descriptivo**, no causal: “el modelo asocia”, no “este municipio es mejor para usted”.

**Uso previsto:** exploración y recomendación orientativa.
**No usar para:** segmentación oficial, marketing o decisiones automatizadas.

---

## Glosario para el jurado

- **ICA:** índice de capacidad de acogida, 0–100. Resume si un municipio puede recibir población sin romper servicios.
- **Cuello de botella:** el servicio que se satura primero (sanidad, educación o vivienda).
- **No compensatorio:** un servicio colapsado no se compensa con otros factores; la nota se trunca.
- **OOF (out-of-fold):** predicción sobre municipios que el modelo no vio al entrenar.
- **GroupKFold por comarca:** se entrena con unas comarcas y se examina con otras.
- **Banda del 95 %:** horquilla de incertidumbre; no es un intervalo de certeza.
- **Calibración:** valor generado por el equipo para representar una variable no disponible; se declara como estimación.
- **What-if:** simulación de una inversión o llegada de población.
- **M4-OPT:** heurística voraz que reparte un presupuesto cerrado entre municipios de una comarca.

---

## Cross-check de números (F13.3)

| Número | Artefacto | Clave |
|---|---|---|
| M1 MAE/R²/ONNX | `src/lodcore/models/m1_avm/metrics.json` | `mae_cv_mean`, `r2_cv_oof`, `onnx_max_*` |
| M2 PC1 / 30 min | `src/lodcore/models/m2_indicadores/metrics.json` | `explained_variance_ratio_pc1`, `municipios_30min_*` |
| M3 población | `src/lodcore/models/m3_demografia/metrics.json` | `poblacion_*` |
| M4 MAE/R²/ONNX | `src/lodcore/models/m4_capacidad/metrics.json` | `mae_cv_mean`, `r2_cv_oof`, `onnx_max_*` |
| M4 atribuciones | `src/lodcore/models/m4_capacidad/shap_background.json` | `metodo_atribucion` |
| M5 clústeres | `src/lodcore/models/m5_recomendador/metrics.json` y `clustering.json` | `silhouette_score`, `cluster_sizes` |
| Peores errores M1/M4 | `scripts/check_model_cards.py` | recalcula OOF y verifica las cifras de esta ficha |

```powershell
python scripts/check_model_cards.py
python -m pytest tests -q
```
