# LoDCORE Madrid · Índice de Capacidad de Acogida (ICA)

MVP para el **II Datathon LoDCOREMadrid 2026** (UC3M + Comunidad de Madrid).
Identifica en qué municipios de menos de 50.000 habitantes se puede acoger nueva
población **sin saturar sanidad, educación, vivienda y conectividad**, y permite
simular inversiones y shocks demográficos antes de decidir.

> **Alcance del MVP**: piloto reproducible sobre **20 municipios de 8 comarcas**.
> No pretende cubrir los ~160 municipios menores de 50.000 hab. de la región.
> El panel es una **maqueta calibrada**: la columna `fuente_datos` distingue la
> parte padronal de la calibrada sintéticamente (seed 2026).

---

## 1. Estructura real del repositorio

```
DatathonLodCoreMadrid/
├── params.yaml                      # Hiperparámetros (los leen los modelos)
├── requirements.txt
├── src/lodcore/
│   ├── config/                      # thresholds.py, weights.py, cargar_params()
│   ├── data/                        # quality gates, punto-en-tiempo, procedencia
│   ├── ingest/                      # Conectores INE + CKAN Madrid (Fase F1)
│   ├── models/
│   │   ├── m1_avm/                  # M1 · valoración hedónica y esfuerzo familiar
│   │   ├── m2_indicadores/          # M2 · PCA + isócronas de 30 min
│   │   ├── m3_demografia/           # M3 · extrapolación demográfica calibrada
│   │   ├── m4_capacidad/            # M4 · ICA + reglas no compensatorias (core)
│   │   └── m5_recomendador/         # M5 · K-Means + recomendación MCDM
│   ├── explain/                     # atribuciones aditivas y redacción sin causalidad
│   ├── publish/                     # bandas 95 %
│   └── serving/fastapi/             # API N3: /recomendar, /whatif y /optimizar-presupuesto
├── frontend/                        # portal estático (index.html, datos embebidos)
├── scripts/                         # run_all_models_n1_n2_n3.py + auditorías
├── tests/                           # unit + integración (pytest)
├── oracle/ddl/                      # 02 tabla, 03 vistas APEX, 04 ranking, 05 ONNX
├── oracle/onnx/                     # binarios ONNX para N2
├── data/raw/                        # descargas originales INE + CKAN (inmutables)
├── data/output/                     # payload JSON del panel
├── data/validated/                  # EL dataset canónico (20 × 92)
└── docs/                            # validación y notas de diseño (docs/_archivo = histórico)
```

---

## 2. Puesta en marcha

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt

# Pipeline completo: F2 (validación) -> F3..F7 (modelos) -> N2 (ONNX)
python scripts/run_all_models_n1_n2_n3.py

# Tests (unitarios + integración)
python -m pytest tests -q

# API N3 (desde la raíz del proyecto)
uvicorn src.lodcore.serving.fastapi.app:app --reload --port 8000
```

Endpoints:

- `GET /health` — diagnóstico del servicio (versión, dataset y endpoints activos).
- `POST /recomendar` — recomendación personalizada para un ciudadano (M5 + MCDM).
- `POST /whatif` — simulación institucional de residentes, médicos, plazas e inversión.
- `POST /optimizar-presupuesto` — heurística voraz comarcal: reparte un presupuesto cerrado entre municipios (M4-OPT).
- `GET /docs` — Swagger autogenerado por FastAPI.

> El portal `frontend/index.html` es **estático y autocontenido**: los datos van
> embebidos en `index.js` y no llama a ninguna API. La UI de entrega será Oracle APEX.

---

## 3. Carga en Oracle Database 23ai / APEX

Ejecutar en orden con SQLcl, SQL Developer o APEX › SQL Workshop:

1. `oracle/ddl/02-tablas_procesadas.sql` (crea `municipios_procesados` con las **92 columnas** del panel y 4 columnas virtuales de compatibilidad)
2. `oracle/ddl/03-vistas_apex.sql`
3. `oracle/ddl/04-perfiles_y_ranking.sql` (perfiles, pesos y función de ranking del ciudadano)
4. `oracle/ddl/05-modelos_onnx.sql`

> Se retiraron `01-tablas_raw.sql` (tres tablas crudas que nadie rellenaba y que
> declaraban plazas y médicos inexistentes en las fuentes) y `06-dataset_completo_APEX.sql`
> (reset destructivo). El antiguo `04-indices_espaciales.sql` también se retiró:
> la columna SDO_GEOMETRY nunca se poblaba y el mapa trabaja con latitud/longitud.

Para el paso 4, copiar `oracle/onnx/*.onnx` a un directorio del servidor y crear
el objeto de directorio antes de cargar los modelos:

```sql
CREATE OR REPLACE DIRECTORY LODCORE_ONNX_DIR AS '/opt/lodcore/onnx';
-- Otorgar READ al usuario LODCORE si el directorio lo crea otro usuario.
```

La vista `v_onnx_scoring_n2` puntúa **con las columnas reales** del panel, no con
constantes. La equivalencia con Python se verifica con error relativo < 1e-6 y
absoluto < 1e-3 (ONNX devuelve float32).

Al cargar `data/validated/municipios_panel_validado.csv` en `municipios_procesados`
(APEX › Data Workshop › Load Data o SQL Developer), **las 88 columnas coinciden
1:1 por nombre**. No hay que mapear nada: las cuatro columnas antiguas
(`tiempo_madrid_min`, `plazas_escolares`, `alumnos_matriculados`, `precio_avm_m2`)
son **virtuales** y Oracle las calcula a partir de las columnas canónicas.

Todas las columnas del CSV se cargan, incluidas `densidad`, `hab_por_medico` y
`ocupacion_escolar_pct` (ahora son columnas normales `NOT NULL`, no virtuales).
`fecha_disponible`, `origen`, `metodo`, `dataset_version` y `fuente_datos` son
obligatorias.

---

## 4. Fórmula del ICA y reglas duras

```
ICA = 0,30 · vivienda
    + 0,30 · (sanidad + educación) / 2
    + 0,25 · conectividad
    + 0,15 · holgura
```

Capacidad de absorción (habitantes adicionales):

- **Sanidad** = médicos × 1.500 − población
- **Educación** = (plazas × 0,95 − alumnos) / 0,17
- **Vivienda** = 0,75 × viviendas vacías + 0,00375 × suelo urbano disponible (m²)
  (calibración del panel F2; reproduce `personas_absorb_vivienda`)
- **Sin colapso** = mín(sanidad, educación) · **Efectiva** = mín(las tres)
- **Coste de ampliación** = médicos adicionales × 450.000 € + plazas adicionales × 12.000 €

Regla **no compensatoria** (diferencial del proyecto): si un municipio supera
**1.500 hab/médico** o **95 % de ocupación escolar**, su ICA se trunca a
`< 40` (semáforo BAJA) aunque el resto de factores sea excelente.

Los umbrales y costes viven en `src/lodcore/config/thresholds.py`; los
hiperparámetros en `params.yaml`. **No hay** tabla `PARAMETROS_MODELO`: esa
referencia del prototipo antiguo quedó obsoleta.

---

## 5. Modelos y estado real

| Modelo | Qué hace | Método real | Estado |
|---|---|---|---|
| **M1** | Precio justo €/m², gap de mercado y esfuerzo familiar | Random Forest + CV espacial por comarca | Ilustrativo: con n=20 el R² fuera de muestra es inestable (puede ser negativo) |
| **M2** | 4 sub-índices 0–100 e isócronas de 30 min | PCA + MinMax + heurística con tiempo a Madrid y paradas (sin rutas OSM/GTFS) | Determinista |
| **M3** | Población 2030/2035 y escenarios +5 %/+10 % | Extrapolación geométrica calibrada con la proyección padronal 2031 | Determinista, no SARIMAX |
| **M4** | ICA, banda 95 %, reglas duras y atribuciones | Gradient Boosting + GroupKFold por comarca + ONNX | **Core**; usar `r2_cv_oof`, no el in-sample |
| **M5** | Arquetipos municipales y recomendación ciudadana | K-Means + coseno ponderado (MCDM) | No supervisado |

**Limitaciones que hay que declarar en la presentación**:

- El target de M4 (`indice_capacidad_global`) es una combinación determinista de
  los sub-índices; `r2_in_sample = 1.0` **no** es evidencia de generalización.
  La métrica honesta es `r2_cv_oof` (~0,73 con las 8 comarcas).
- Las atribuciones de M4 son una **aproximación aditiva de 2 órdenes**, no
  valores Shapley exactos. El JSON lo declara en `metodo_atribucion`.
- La parte de servicios y vivienda está calibrada sintéticamente. Antes de uso
  real hay que sustituirla por SERMAS, Consejería de Educación, CRTM, CNMC y
  Catastro.
- La **heurística voraz** de asignación presupuestaria por comarca (M4-OPT)
  **sí está implementada** (`optimizador_presupuestario.py` + endpoint
  `/optimizar-presupuesto`): reparte un presupuesto cerrado priorizando
  cuellos de botella y podando inversiones de ganancia marginal nula. El
  **spillover continuo** entre municipios vecinos **no** está implementado y
  se presenta como roadmap. El what-if evalúa escenarios manuales.

---

## 6. Procedencia y trazabilidad

Toda fila del panel debe portar:

- `origen`: `OBSERVADO | IMPUTADO | ESTIMADO | PROYECTADO | SIMULADO` (combinables con `+`).
- `metodo`: algoritmo o regla que produjo el valor.
- `fuente_datos`: fuente oficial concreta (INE, CKAN, Catastro, CRTM, etc.).
- `dataset_version`: `v1.0.0-F2`.
- `fecha_disponible`: control de punto-en-tiempo (nada posterior a `fecha_decision`).

Toda predicción publicada debe portar `origen`, `metodo`, `dataset_version` y su
banda de incertidumbre. Las puertas de `src/lodcore/data/quality_gates.py` bloquean
el pipeline si falta cualquiera de estos campos en el panel, si hay nulos en
columnas obligatorias o si un sub-índice sale de `[0, 100]`.
