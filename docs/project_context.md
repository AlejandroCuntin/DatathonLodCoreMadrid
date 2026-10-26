# PROJECT_CONTEXT.md — LoDCORE Madrid

> Documento de contexto operativo. Sustituye al plan anterior de 16 fases.
> **Última actualización:** 26 de octubre de 2026.
> Estado: MVP con datos reales integrados; en construcción el perfil ciudadano.

---

## 1. Qué es el proyecto

LoDCORE Madrid calcula qué municipios de la Comunidad de Madrid con menos de
50.000 habitantes pueden acoger nueva población sin colapsar sanidad, educación
y vivienda, y cuánto cuesta ampliar su capacidad.

**Pregunta que responde:**
> ¿Qué municipios pueden acoger la nueva población y cómo repartir inversión
> para que ninguno quede por debajo del umbral?

---

## 2. Estado real

| Elemento | Valor |
|---|---|
| Municipios del panel | **20** (8 comarcas, 200.267 hab.) |
| Columnas del panel | **92** |
| Columnas observadas (reales) | **8** |
| Dataset version | `v1.1.0-F2` |
| Perfil ciudadano | **C1 completado** (C2-C7 pendientes) |
| Tests | **36 en verde** |
| Modelos ONNX en Oracle | M1 y M4 |
| API | `/health`, `/recomendar`, `/whatif`, `/optimizar-presupuesto` |
| DDL Oracle | `02-tablas_procesadas.sql`, `03-vistas_apex.sql`, `05-modelos_onnx.sql` |

**Ejecutar:**
```powershell
python -m pytest tests -q
python -m src.lodcore.ingest.pipeline_datos_reales
python scripts/run_all_models_n1_n2_n3.py
uvicorn src.lodcore.serving.fastapi.app:app --port 8000
```

---

## 3. Qué es real y qué es calibrado

**Observado (fuente oficial):**

| Columna | Fuente |
|---|---|
| `poblacion_actual`, `anio_padron` | INE Padrón continuo (tabla 2881) |
| `num_centros_salud` | CKAN Comunidad de Madrid (sanidad, centros en ALTA) |
| `num_centros_educativos` | CKAN Comunidad de Madrid (educación reglada en ALTA) |
| `valor_catastral_residencial_eur_m2`, `anio_valor_catastral` | DG Catastro vía CKAN CAM (2026) |
| `migracion_neta_externa` | INE Variaciones Residenciales vía CKAN CAM (media 2017-2021) |
| `crecimiento_pob_pct_2020_2025` | INE Padrón 2881 (nult=6) |

**Calibrado con `seed=2026` y declarado en `fuente_datos`:** precios de vivienda,
viviendas vacías, suelo disponible, médicos de atención primaria, plazas
escolares, camas hospitalarias, transporte y fibra.

**Limitación estructural:** el número de médicos y de plazas escolares por
municipio **no existe en datos abiertos** (SERMAS y Consejería no lo publican
desagregado). Por eso la regla de 1.500 hab/médico se evalúa sobre una
calibración, y así debe declararse.

---

## 4. Reto y criterios del jurado

**Reto:** ayudar a las Administraciones Públicas a identificar qué municipios de
menos de 50.000 habitantes tienen mejores posibilidades para acoger la nueva
población.

**Presentación:** 15 minutos, 29 de octubre de 2026, UC3M Leganés.
**Jurado:** perfil institucional (UC3M + Comunidad de Madrid), no ingeniero.

| Bloque | Criterio | Puntos |
|---|---|---|
| 1 | Planteamiento teórico correcto | 25 |
| 1 | Grado de resolución del reto | 25 |
| 2 | Sencillez de obtención y comprensión | 25 |
| 2 | Interactividad y flexibilidad | 25 |

**Implicación:** el jurado premia claridad e interacción, no complejidad
algorítmica. Hablar de inversión, capacidad y coste; evitar jerga de ML.

---

## 5. Arquitectura

| Nivel | Dónde | Qué hace |
|---|---|---|
| **N1** | Python / CI | Entrena y exporta a ONNX |
| **N2** | Oracle Database 23ai | `DBMS_VECTOR.LOAD_ONNX_MODEL` + `PREDICTION()` |
| **N3** | FastAPI + APEX | Recomendación, what-if y optimización |

**Flujo de una consulta desde APEX:**

```
APEX (formulario de perfil y parámetros)
   → proceso PL/SQL
   → SELECT sobre municipios_procesados + PREDICTION(ONNX)
   → función de ranking por perfil
   → región de resultados + mapa + comparador + ficha
```

El modelo **no** accede a la base de datos: el modelo **vive dentro** de la base
de datos. Ese es el argumento Oracle del proyecto.

---

## 6. Los 5 modelos y su papel

| Modelo | Algoritmo real | Pregunta que responde | Estado |
|---|---|---|---|
| **M1 · AVM** | Random Forest (sklearn) | ¿Puedo permitírmelo? Precio €/m² y gap de mercado | Ilustrativo: R² fuera de muestra inestable |
| **M2 · Indicadores** | PCA + StandardScaler + MinMax | ¿Qué tal servicios y conexión? 4 sub-índices 0-100 | Determinista |
| **M3 · Demografía** | Extrapolación geométrica calibrada (CAGR) | ¿Va a crecer o vaciarse? | Determinista; pendiente backtest |
| **M4 · Capacidad** | GradientBoostingRegressor (sklearn) | ¿Cuánta gente cabe y qué se rompe antes? | Core; reproduce la fórmula del ICA |
| **M5 · Recomendador** | KMeans + coseno ponderado (MCDM) | ¿Cuál encaja conmigo? | Determinista |

**No se usa:** XGBoost, LightGBM, SHAP (librería), statsmodels, Prophet, OSMnx,
NetworkX, inferencia causal. Si se mencionan, deben presentarse como roadmap.

**Cadena:**
```
M2 (sub-índices) → M4 (ICA + regla dura) ┐
M1 (asequibilidad)                        ├→ M5 (ranking por perfil) → ficha
M3 (riesgo futuro)                        ┘
```

---

## 7. Reglas de negocio (no cambian sin discusión)

### Índice de capacidad de acogida
```
Sanidad    = médicos × 1.500 − población
Educación  = (plazas × 0,95 − alumnos) / 0,17
Vivienda   = 0,75 × viviendas vacías + 0,00375 × suelo disponible

ICA = 0,30·vivienda + 0,30·(sanidad+educación)/2 + 0,25·conectividad + 0,15·holgura
```

### Regla no compensatoria
```
Si hab/médico > 1.500  o  ocupación escolar > 95 %  →  ICA < 40 (BAJA)
```
Un servicio crítico colapsado no se compensa con otros factores.

### Regla de los perfiles
> **Los pesos del perfil cambian el RANKING. Nunca el ICA ni la regla dura.**

Orden obligatorio de cálculo:
```
1. ICA objetivo (igual para todos)
2. Regla no compensatoria (techo 40 si colapsa)
3. Ranking según pesos del perfil (solo entre municipios ya evaluados)
```

### Construcción de pesos (decisión C1)
```
Pesos base = iguales (0,25 cada dimensión): no hay evidencia para preferir
Ajustes personales = supuestos declarados y acotados
Aplicación = transferencia (el total suma 1,0; tope del 20 % por perfil)
Sensibilidad = ±20 % por dimensión; se reporta Spearman y estabilidad del top-5
```
No se afirma que exista un peso correcto: se mide cuánto importa equivocarse.

### Umbrales
Viven en `src/lodcore/config/thresholds.py`. Una sola fuente de verdad.
La fecha de decisión vive en `src/lodcore/config` (`FECHA_DECISION_MVP`).

---

## 8. Perfiles de usuario

| Perfil | Estado | Entradas | Objetivo |
|---|---|---|---|
| **Ciudadano** | En construcción (C1-C7) | presupuesto, ingresos, tiempo, hijos, edad, transporte, tenencia | Ranking personalizado |
| **Institución** | Diseñado (I1-I6) | presupuesto, comarca, objetivo eficiencia/equidad | Dónde invertir sin dejar municipios atrás |
| **Empresario** | **Roadmap** | — | Requiere suelo industrial, empleo y CNAE; hoy no hay datos |

Los municipios colapsados **se muestran marcados**, no se ocultan.

Los datos personales **no se almacenan**: se calculan en la sesión.

---

## 9. Etapas del perfil ciudadano

| Etapa | Contenido | Estado |
|---|---|---|
| **C1** | Modelo de preferencias: entradas, pesos, filtros y fórmula de esfuerzo | ✅ **Hecho**: `docs/perfil_ciudadano.md` + `src/lodcore/config/perfiles.py` (verificado) |
| **C2** | Motor de ranking con pesos del perfil y filtros duros | Pendiente |
| **C3** | Asequibilidad: cuota, esfuerzo financiero y gap de mercado (M1) | Pendiente |
| **C4** | Explicación por municipio: desglose de afinidad, fortalezas y carencias | Pendiente |
| **C5** | Capa Oracle: tabla `PERFILES_PESOS` + función de ranking | Pendiente |
| **C6** | API N3 equivalente a la función SQL | Pendiente |
| **C7** | Página APEX del ciudadano: formulario, resultados, mapa y comparador | Pendiente |

---

## 10. Etapas del perfil institución (diseño)

| Etapa | Contenido |
|---|---|
| **I1** | Tabla de objetivos: eficiencia vs equidad |
| **I2** | Optimizador con objetivo max-min (subir el mínimo comarcal) |
| **I3** | Efecto de arrastre en vecinos (supuesto configurable, **no causal**) |
| **I4** | Comparativa "mismo presupuesto, dos objetivos" |
| **I5** | Página APEX institucional |
| **I6** | Pruebas del optimizador |

---

## 11. Pruebas transversales

- Monotonía: bajar presupuesto no incorpora municipios más caros.
- Filtros duros: precio y tiempo se respetan siempre.
- Regla dura: un municipio colapsado no entra en el top aunque sus pesos le favorezcan.
- Determinismo: mismos parámetros, mismo orden.
- Equivalencia SQL ↔ Python del ranking.
- Equivalencia ONNX ↔ Python (`< 1e-6` relativo).

---

## 12. Qué está hecho, qué falta y qué no se hará

**Hecho:** panel con datos reales, índice documentado, reglas duras, simulador,
optimizador por eficiencia, ONNX en Oracle, mapa ORDS, portal estático, 36 tests.

**Falta:** C1-C7, I1-I6, backtest de M3, validación ICA vs crecimiento real,
regeneración del paquete de entrega.

**No se hará en este ciclo:** isócronas con GTFS, SARIMAX/Prophet, inferencia
causal/ATE, spillover medido, perfil empresario, panel de 179 municipios.

---

## 13. Roadmap técnico (para el pitch)

1. Isócronas reales sobre GTFS/OSM (hoy: heurística por tiempo y paradas).
2. SARIMAX con exógenas (hoy: extrapolación geométrica validable por backtest).
3. Inferencia causal y ATE (requiere historial de intervenciones no público).
4. Spillover estimado con matriz origen-destino (hoy: supuesto configurable).
5. Capa de datos oficiales para los 179 municipios menores de 50.000 hab.
6. Perfil empresario con CNAE, afiliación y uso industrial del suelo.

---

## 14. Regla de honestidad

Todo número publicado debe poder rastrearse a un fichero o a una función.
Si una variable es calibrada, se declara en `fuente_datos` y se dice en la
presentación. Es mejor un sistema pequeño y comprobable que uno grande y falso.
