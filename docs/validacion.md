# Informe de Validación Rigurosa y Auditoría (Fase F8)
## Proyecto LoDCORE Madrid • II Datathon 2026

> **Regla `AGENTS.md`**: todo número publicado en este documento procede de un
> fichero de resultados verificable en el repositorio (`metrics.json`,
> `shap_background.json` y el contrato ONNX de `src/lodcore/models/base.py`).

---

### 1. Puertas de Calidad y Punto-en-Tiempo (Fase F2)

- **Dataset validado**: `data/validated/municipios_panel_validado.csv`
  (`dataset_version = v1.0.0-F2`, 20 municipios, 8 comarcas).
- **Municipios superados**: **20 / 20**. Se comprueba población $< 50.000$ hab.,
  unicidad de claves INE, no-nulidad de columnas obligatorias, origen permitido,
  fechas parseables, rangos $[0, 100]$ en sub-índices y control
  `fecha_disponible <= fecha_decision`.
- **Evidencia**: `src/lodcore/data/quality_gates.py`,
  `src/lodcore/data/pointintime.py` y `tests/integration/test_pointintime.py`.
- **Procedencia**: la población parte del padrón; la dotación de servicios y
  vivienda está calibrada sintéticamente (seed 2026). El campo `origen` del panel
  queda como `OBSERVADO+SIMULADO` para no etiquetar como real lo que no lo es.

---

### 2. Resultados Auditados por Modelo (F3–F7)

| Modelo | Algoritmo | Esquema CV | Métrica honesta | Equivalencia ONNX (abs / rel) | Evidencia |
|---|---|---|---|---|---|
| **M1 — AVM y Asequibilidad** | `RandomForestRegressor` | `Spatial_GroupKFold_Comarca` | MAE CV: **382,83 €/m²** ($\pm 230,20$) · $R^2$ CV: **−0,3398** · $R^2$ in-sample: 0,8032 | **5,47e−4 / 3,65e−7** | `src/lodcore/models/m1_avm/metrics.json` |
| **M2 — Indicadores e Isócronas (heurística)** | `PCA` + `MinMaxScaler` | Determinista (0–100) | 16/20 municipios con tiempo estimado $\le 30$ min (privado); 8/20 en público | N/A | `src/lodcore/models/m2_indicadores/metrics.json` |
| **M3 — Proyección Demográfica** | Extrapolación geométrica calibrada | Bandas 95 % a 5 y 10 años | Pob. 2025: **200.267** $\rightarrow$ 2030: **216.597** $\rightarrow$ 2035: **234.336** | N/A | `src/lodcore/models/m3_demografia/metrics.json` |
| **M4 — Capacidad de Acogida (core)** | `GradientBoostingRegressor` + atribuciones aditivas | `Spatial_GroupKFold_Comarca` | MAE CV: **5,15 ptos** ($\pm 2,41$) · $R^2$ CV: **0,7345** · $R^2$ in-sample: 1,0000 | **1,03e−5 / 2,29e−7** | `src/lodcore/models/m4_capacidad/metrics.json` |
| **M5 — Recomendador MCDM** | `KMeans (k=4)` + coseno ponderado | No supervisado + MCDM | Silhouette: **0,3183** · Inercia: **39,01** | N/A | `src/lodcore/models/m5_recomendador/metrics.json` |

**Contrato ONNX**: el binario devuelve tensores `float32`; a escalas de
2.000 €/m² un error absoluto $<10^{-6}$ no es representable. Por eso el test
exige **error relativo $<10^{-6}$** y **absoluto $<10^{-3}$**, y comprueba
explícitamente que `predict()` usa scikit-learn (no ONNX) para que la
comparación no sea tautológica.

**Advertencias metodológicas que deben acompañar a estas cifras**:

- **M1**: con $n=20$ y 8 comarcas el $R^2$ fuera de muestra es **negativo**
  (−0,3398). M1 es un módulo ilustrativo; no debe presentarse como un AVM
  validado.
- **M4**: el target (`indice_capacidad_global`) es una combinación determinista
  de los sub-índices, por lo que $R^2$ in-sample $=1$ no es generalización. La
  cifra que se debe defender es el **$R^2$ CV = 0,7345**.
- **M5**: los nombres de arquetipo se asignan por interpretación de los
  centroides; `clustering.json` exporta ahora los centroides y tamaños para
  poder auditarlos.

---

### 3. Auditoría de Explicabilidad y No-Compensatoriedad

- **Método real**: `EFECTOS_MARGINALES_SIMETRICOS_NORMALIZADOS`. Es una
  aproximación aditiva de 2 órdenes (media de la contribución hacia delante y
  hacia atrás, normalizada para cumplir eficiencia), **no** valores Shapley
  exactos. El JSON lo declara en `metodo_atribucion`.
- **Background persistido**: `src/lodcore/models/m4_capacidad/shap_background.json`
  (el nombre del fichero se mantiene por compatibilidad).
- **Hash SHA-256 de integridad**: `4c86e5edf5164a9d…`
- **Auditoría léxica de no-causalidad**: `verificar_ausencia_causalidad` en
  `src/lodcore/explain/redaccion_natural.py`.
- **Pruebas adversariales de colapso**: `tests/unit/test_models.py` confirma que
  cualquier municipio con $>1.500$ hab/médico o $>95\,\%$ de ocupación escolar
  ve truncado su ICA a $<40,0$ puntos (`semaforo_ica = BAJA`).
