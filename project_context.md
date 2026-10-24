# PROJECT_CONTEXT.md — LoDCORE Madrid (II Datathon 2026)

> Contexto operativo para el equipo (3 personas) y para las IAs de cada miembro.
> Objetivo: ganar el II Datathon LoDCOREMadrid el 29 de octubre de 2026 con un MVP funcional orientado a instituciones (jurado: UC3M + Comunidad de Madrid).
> **Última actualización:** 24 oct 2026 — plan ampliado a 16 fases con mapeo a los 14 prompts operativos de `PROMPTS-LoDCORE`; documentación alineada con el estado real (20 municipios, 4 endpoints, heurística voraz M4-OPT).

---

## 1. Qué es este proyecto

LoDCORE predice qué municipios de la Comunidad de Madrid con menos de 50.000 habitantes pueden acoger de forma sostenible a la nueva población que la región debe absorber, y explica de forma auditable dónde y cuánto invertir para maximizar esa capacidad.

**No es un predictor de precios de vivienda.** Es un sistema de inteligencia territorial con doble utilidad:
- **Ciudadanos:** encontrar municipios que se ajusten a sus necesidades y posibilidades económicas.
- **Instituciones (DGRT, ayuntamientos):** información objetiva para priorizar inversiones, detectar desequilibrios territoriales y diseñar políticas de desarrollo más eficientes.

**Stack:** datos públicos abiertos → Python → Oracle Database (ONNX en N2) → Oracle APEX + FastAPI (N3).

> **Advertencia técnica crítica:** con 20-41 municipios, un modelo supervisado puro (XGBoost, Random Forest, GBR) se sobreajusta y no predice nada generalizable. El valor del proyecto no está en "predecir con ML sobre 20 filas", sino en **reglas determinísticas + optimización matemática + simulador what-if + efecto spillover por comarca**. Eso es lo que vendemos al jurado institucional.

---

## 2. Reto oficial y criterios del jurado

**Reto (Bases oficiales):** ayudar a las Administraciones Públicas a identificar qué municipios de <50.000 habitantes tienen mejores posibilidades para acoger la nueva población.

**Entregable exigido:** Producto Mínimo Viable (MVP) funcional + presentación de impacto.

**Presentación:** 15 minutos el 29 de octubre de 2026, Salón de Grados, UC3M Leganés. Presentan los 3 miembros del equipo.

**Jurado:** representantes de UC3M y Comunidad de Madrid (perfil institucional, no ingeniero).

**Criterios de valoración (0-100):**
| Bloque | Criterio | Puntos |
|--------|----------|--------|
| 1 | Calidad del resultado: planteamiento teórico correcto | hasta 25 |
| 1 | Calidad del resultado: grado de resolución del reto | hasta 25 |
| 2 | Usabilidad: sencillez en obtención y comprensión de resultados | hasta 25 |
| 2 | Usabilidad: interactividad/flexibilidad para adaptarse al caso del usuario | hasta 25 |

**Desempate:** 2.2 (interactividad) → 1.2 (resolución del reto) → 1.1 (teórico) → 2.1 (sencillez).

> Implicación práctica: el jurado valora más que se entienda y se pueda interactuar con la solución que la complejidad del algoritmo. Hablar en lenguaje institucional: "dónde invertir", "cuánto cuesta", "cuánta población puede absorber", "efecto en pueblos vecinos". Evitar tecnicismos tipo SHAP, float32, ONNX, AVM frente al jurado.

---

## 3. Arquitectura técnica (N1 / N2 / N3)

| Nivel | Entorno | Función |
|-------|---------|---------|
| **N1** | Entrenamiento (Python/CI) | Modelos entrenados y exportados a ONNX. |
| **N2** | Scoring en Oracle Database | `DBMS_VECTOR.LOAD_ONNX_MODEL` + `PREDICTION()`. Ningún modelo se entrena dentro de APEX. |
| **N3** | FastAPI + Oracle APEX | `/recomendar` (ciudadano) y `/whatif` + `/optimizar-presupuesto` (institución). Interfaz visual para consulta y simulación. |

El DDL de `oracle/ddl/` es fuente de verdad; APEX consume, no redefine. Toda vista expuesta a APEX incluye `origen`, `metodo` y `dataset_version`.

---

## 4. Los 5 modelos (M1-M5)

| Modelo | Nombre | Algoritmo | Función clave |
|--------|--------|-----------|---------------|
| **M1** | AVM (valoración inmobiliaria) | Random Forest | Precio de referencia por m² y esfuerzo financiero familiar. |
| **M2** | Indicadores de capacidad | PCA + heurística de tiempos de viaje | 4 sub-índices 0-100 (sanidad/educación, conectividad, vivienda, holgura) y criterio "municipio de 30 minutos". |
| **M3** | Demografía | Extrapolación geométrica calibrada (2031) | Proyección poblacional a 5 y 10 años con bandas 95% y escenarios +5% / +10%. |
| **M4** | **Capacidad de acogida (CORE)** | Gradient Boosting + reglas duras + atribuciones aditivas + simulador what-if + asignación presupuestaria comarcal | Predice el ICA, detecta cuellos de botella y permite simular inversiones. **Heurística voraz de asignación presupuestaria por comarca (M4-OPT)** implementada en `optimizador_presupuestario.py`; el spillover geográfico continuo con matriz OD queda formalmente como roadmap Fase 2. |
| **M5** | Recomendador ciudadano | K-Means + MCDM coseno ponderado | Ranking personalizado por preferencias del ciudadano. |

> **Diferencial competitivo del proyecto (estado real):** ya están implementados la predicción del ICA, las reglas duras, el simulador what-if y la **heurística voraz de asignación presupuestaria por comarca (M4-OPT)**, que reparte un presupuesto cerrado priorizando cuellos de botella y podando inversiones ineficientes. El efecto spillover continuo intermunicipal se declara formalmente como evolución metodológica (Roadmap Fase 2).

---

## 5. Reglas de negocio y umbrales (no cambian sin discusión)

- **Ratio sanitario crítico:** > 1.500 hab/médico de Atención Primaria.
- **Ocupación escolar crítica:** > 95% de plazas ocupadas.
- **Semáforo ICA:** Baja < 40, Media 40-59, Alta ≥ 60.
- **No-compensatoriedad:** si un municipio supera alguno de los umbrales críticos, su ICA se trunca a BAJA (<40) y no puede compensarse con otros factores (vivienda, suelo, conectividad).
- **Toda predicción de modelo (M1/M4) se publica con banda de incertidumbre al 95% y procedencia (`origen` + `metodo`).** Las simulaciones what-if y la heurística de presupuesto se publican como `SIMULADO` con `origen`/`metodo`/`dataset_version` (sin banda: no son predicciones estadísticas).
- **Las atribuciones describen el modelo, nunca la realidad.** No usar palabras causales ("causa", "provoca") frente al usuario; usar "el modelo asocia", "según el modelo", "contribuye a".
- **Idioma de salida al usuario final:** español de España.

Valores permitidos en `origen`: `OBSERVADO | IMPUTADO | ESTIMADO | PROYECTADO | SIMULADO`.

---

## 6. Estructura del repositorio (raíz de trabajo)

```
DATATHON/ (raíz del espacio de trabajo)
├── codigo/DatathonLodCoreMadrid/   # ÚNICO repositorio Git activo (todo el MVP vive aquí)
│   ├── src/lodcore/                #   ingest/ (INE+CKAN), data/, models/ M1-M5, explain/, publish/, serving/
│   ├── frontend/mapa/              #   Mapa interactivo del portal (HTML/CSS/JS)
│   ├── scripts/                    #   run_all_models_n1_n2_n3.py + pipeline F1
│   ├── tests/                      #   25 tests (unit + integración)
│   ├── oracle/                     #   ddl/ (01..06; el 06 en revisión), REST/ y onnx/
│   ├── data/                       #   raw/ (snapshots INE+CKAN), processed/, validated/, output/
│   ├── docs/                       #   validación, matriz de procedencia, specs y material_reto/ (PDFs oficiales)
│   ├── PROMPTS-LoDCORE/            #   Kit de 14 prompts + AGENTS.md de la cátedra
│   ├── .github/                    #   ISSUES_F1_F16.md (tablero documentado)
│   ├── entrega/                    #   Paquete para el jurado (dataset + diccionario + fuentes + checksums)
│   ├── README.md · project_context.md · estructura.md
│   ├── params.yaml · requirements.txt · dvc.yaml · index.html
│   └── diagrama_flujo.mmd / .png   #   Resumen visual en 7 bloques
└── fases.md                        # Plan histórico original (NO MODIFICAR; sustituido por la sección 8)
```

> Nota: `codigo/DatathonLodCoreMadrid/` contiene el código fuente activo (`src/`, `data/`, `docs/`, `oracle/`, `scripts/`, `tests/`). No crear duplicados en raíz. Los PDFs oficiales del Datathon (Bases, Diseño, Fuentes de datos y Prototipo de interfaz) están en `docs/material_reto/`.

---

## 7. Equipo (3 personas) y responsabilidades

| Persona | Rol principal | Áreas de trabajo |
|---------|--------------|------------------|
| **P1** | Datos + Optimizador M4 | Ingesta de datos (INE, CKAN, Catastro, CRTM), trazabilidad `origen`/`metodo`, reglas de no-compensatoriedad, optimizador matemático de infraestructura por comarca, efecto spillover, geometría para mapa APEX. |
| **P2** | Modelos + API | Entrenamiento M1-M5, exportación ONNX, equivalencia ONNX/Python, FastAPI (`/recomendar`, `/whatif`, `/optimizar-presupuesto`), tests (pytest), reproducibilidad, script único de ejecución. |
| **P3** | UI/APEX + Presentación | Oracle APEX (3 páginas en el MVP; 9 como roadmap), `index.html`, vistas APEX con trazabilidad, diseño de diapositivas, guion de 15 min, ensayo, materiales para el jurado institucional. |

---

## 8. Plan de fases (23 → 29 octubre 2026)

**16 fases en 6 días.** Cada fase tiene subfases específicas, responsables asignados y entregable concreto. Las fases F1-F4 (datos y calidad) son secuenciales; F5-F13 (modelos y publicación) se solapan; F14-F16 (presentación y entrega) son transversales al final.

> **Estado real al 24 oct 2026:** el núcleo ya es ejecutable y está probado
> (`python scripts/run_all_models_n1_n2_n3.py` + `pytest`: 25 tests en verde).
> F0.3 documentada (tablero F1–F16 en `.github/ISSUES_F1_F16.md`; creación de los issues reales en GitHub pendiente),
> F1 completada para las fuentes prioritarias (INE Padrón 2025 y CKAN Madrid Sanidad/Educación conectados, snapshots inmutables fechados, cruce 20/20 por código INE de 5 dígitos; Catastro/CRTM/Notariado quedan fuera del alcance MVP),
> F2 con veredicto formal APTO CON RESERVAS en `docs/validacion.md`, y
> heurística voraz de asignación presupuestaria comarcal (M4-OPT) implementada y documentada (el spillover continuo queda como roadmap de Fase 2).
> F3 documentada (`docs/auditoria_fuga_informacion.md`: 0 bloqueantes, 2 materiales — target determinista y sesgo de selección); F4 (validación), F12 (APEX P3) y F13-F16 continúan abiertas para sus respectivos responsables.
> El **paquete de datos para el jurado** está en `entrega/` (dataset validado + diccionario de 88 variables + catálogo de fuentes con licencias + checksums): cubre la parte de F16.2.

### Fase 0 — Fundamento y reparto (23 octubre)
- **Responsable:** P1 (estructura), P3 (roles), TODOS (regla de contexto).
- **Subfases:**
  - F0.1: Definir alcance honesto: piloto sobre 20 municipios, escalable a todos los <50k (P1) — [CERRADO].
  - F0.2: Crear repositorio GitHub y estructura limpia (P1) — [CERRADO].
  - F0.3: Asignar roles y documentar Issues: F1–F16 documentadas y asignadas en `.github/ISSUES_F1_F16.md`, rama `p1/datos` abierta (P1/P3) — [DOCUMENTADO; pendiente crear los issues en GitHub].
  - F0.4: Acordar canal de comunicación y regla de actualización del contexto (todos) — [CERRADO].
- **Entregable:** repositorio limpio, reglas de trabajo, tablero de issues documentado (creación en GitHub pendiente), rama `p1/datos`.

### Fase 1 — Ingesta de fuentes oficiales (24 octubre)
- **Responsable:** P1.
- **Subfases:**
  - F1.1: Conectar o embeber datos reales: INE Padrón 2025, CKAN Madrid (sanidad/educación), Catastro, CRTM, Notariado (P1).
  - F1.2: `data/raw/` inmutable; snapshot cacheado con fecha (P1).
  - F1.3: Identificar municipio por código INE de 5 dígitos, nunca por nombre (P1).
- **Entregable (MVP real):** conectores Python + snapshots inmutables fechados + matriz de procedencia por variable (`docs/matriz_procedencia_variables.md`). Pandera, DVC como etapa y procedencia celda a celda quedan fuera del alcance del MVP.
- **Prompt asociado:** **01 · Ingesta de fuente oficial**.

### Fase 2 — Auditoría de calidad y procedencia (24 octubre)
- **Responsable:** P1.
- **Subfases:**
  - F2.1: Antes de entrenar nada, distinguir *no aplicable* de *falta de dato* (P1).
  - F2.2: Clasificar outliers (error de captura / valor real / imputación defectuosa) (P1).
  - F2.3: Recalcular de forma independiente `hab/médico` y `% ocupación aulas` (P1).
- **Entregable:** informe de calidad con veredicto APTO / APTO CON RESERVAS / NO APTO, y qué modelos puede alimentar.
- **Prompt asociado:** **02 · Auditoría de calidad y procedencia**.

### Fase 3 — Auditoría de fuga de información (25 octubre)
- **Responsable:** P2.
- **Subfases:**
  - F3.1: 7 tipos de fuga (L1-L7) + sesgo de selección (P2).
  - F3.2: Test empírico: reentrenar con y sin fuga y medir la diferencia (P2).
  - F3.3: Tabla de disponibilidad (as-of date) por variable (P2).
- **Entregable:** tabla de experimentos + dictamen de fuga (`docs/auditoria_fuga_informacion.md`).
- **Prompt asociado:** **03 · Auditoría de fuga de información**.

### Fase 4 — Diseño de validación temporal y espacial (25 octubre)
- **Responsable:** P2.
- **Subfases:**
  - F4.1: `GroupKFold` por municipio + split temporal (train ≤ t, test > t) (P2).
  - F4.2: Spatial K-fold por comarca (P2).
  - F4.3: Banda de 95% por bootstrap de municipio (P2).
  - F4.4: 4 baselines naive obligatorios (un modelo que no gana a la persistencia no se publica) (P2).
- **Entregable:** protocolo de validación + métricas con banda.
- **Prompt asociado:** **04 · Diseño de validación temporal y espacial**.

### Fase 5 — Modelo M1 — AVM (25-26 octubre)
- **Responsable:** P2.
- **Subfases:**
  - F5.1: Precio €/m² compra y alquiler + esfuerzo financiero familiar (P2).
  - F5.2: RF(100) como punto de partida, justificado con literatura española (P2).
  - F5.3: Banda de predicción por residuos fuera de muestra (OOF); conformal como mejora posterior (P2).
- **Entregable:** AVM + esfuerzo financiero + bandas por residuos OOF.
- **Prompt asociado:** **05 · Modelo AVM Random Forest / LightGBM**.

### Fase 6 — Modelo M2 — Índices y isócronas (25-26 octubre)
- **Responsable:** P2.
- **Subfases:**
  - F6.1: PCA + MinMaxScaler → 4 sub-índices 0-100 (sanidad/educación, conectividad, sostenibilidad, músculo presupuestario); se usan como auditoría, no sustituyen a los `score_*` del panel F2 (P2).
  - F6.2: Isócronas de 30 min (público vs privado) hacia polos de empleo y hospitales; implementación actual: heurística documentada sobre tiempo a Madrid y paradas, no rutas OSM/GTFS (P2).
  - F6.3: Fijar signo de componentes PCA y persistirlo (evitar que la APP se rompa entre ejecuciones) (P2).
- **Entregable:** 4 sub-índices + cumplimiento criterio 30 min.
- **Prompt asociado:** **06 · Modelo índices PCA + isócronas**.

### Fase 7 — Modelo M3 — Proyección demográfica (26 octubre)
- **Responsable:** P2.
- **Subfases:**
  - F7.1: Población a 5 y 10 años con bandas de incertidumbre (P2).
  - F7.2: Escenarios +5% / +10% de población (P2).
  - F7.3: Baseline real: extrapolación geométrica calibrada con la proyección padronal 2031; no ARIMA ni SARIMAX (P2).
- **Entregable:** proyección 2030/2035 con bandas 95%.
- **Prompt asociado:** **07 · Modelo proyección demográfica**.

### Fase 8 — Modelo M4 — Capacidad de acogida (26-27 octubre)
- **Responsable:** P2 (modelo), P1 (reglas de negocio).
- **Subfases:**
  - F8.1: Definir el ICA con fórmula explícita. El target es una combinación determinista de los sub-índices: R² in-sample = 1,0 es esperado; la métrica de referencia es el R² fuera de muestra con GroupKFold por comarca (P2).
  - F8.2: ICA + atribuciones aditivas normalizadas (aproximación de 2 órdenes, no Shapley exacto) + simulador What-If (P2).
  - F8.3: Criterio de cuello de botella: regla dura sanitaria (hab/médico > 1.500) o educativa (ocupación > 95 %); el resto de sub-índices no compensa (P2/P1).
  - F8.4: Advertencia en APP: simulaciones fuera de rango observado = extrapolación no fiable (pendiente en APEX) (P2).
- **Entregable:** ICA + atribuciones + simulador What-If + cuellos de botella.
- **Prompt asociado:** **08 · Modelo capacidad acogida XGBoost + SHAP**.

### Fase 9 — Modelo M4b — Cuellos de botella no compensatorios (26-27 octubre)
- **Responsable:** P1.
- **Subfases:**
  - F9.1: Comparar 4 formulaciones (min / media geométrica / regla de veto / penalización suave) y elegir una (P1).
  - F9.2: Regla de veto: municipio en colapso queda por debajo de Media, por mucho que acumule el resto (P1).
  - F9.3: Test de paso: municipio con ICA base 85 y colapso sanitario debe quedar < 40; +50% zonas verdes NO debe subirle el score (P1).
- **Entregable:** regla de no-compensatoriedad ejecutable + test de validación.
- **Prompt asociado:** **09 · Cuellos de botella no compensatorios**.

### Fase 10 — Modelo M5 — Recomendador ciudadano (27 octubre)
- **Responsable:** P2.
- **Subfases:**
  - F10.1: Clustering K-Means con silueta y estabilidad; GMM/BIC como comparación opcional (P2).
  - F10.2: MCDM similitud del coseno ponderada; TOPSIS/VIKOR/ELECTRE como comparación opcional, no implementados en el MVP (P2).
  - F10.3: Ranking de exclusión: criterios duros excluyen y se muestran; blandos ponderan (P2).
  - F10.4: Nombrar clusters verificablemente ("pueblos rurales conectados" solo si los datos lo sostienen) (P2).
- **Entregable:** tipologías territoriales + ranking personalizado + exclusiones duras.
- **Prompt asociado:** **10 · Recomendador clustering + MCDM**.

### Fase 11 — Explicabilidad en lenguaje natural (27 octubre)
- **Responsable:** P3.
- **Subfases:**
  - F11.1: Ficha municipal en español con 8 reglas de redacción (un claim = un número, siempre con umbral, nada de causalidad, incertidumbre presente, sin jerga, sin alarmismo, sin lenguaje discriminante, ≤3 frases) (P3).
  - F11.2: Dos registros (ciudadanía / administraciones) desde la misma plantilla (P3).
  - F11.3: Si la banda cruza un umbral, texto dice "indeterminado" en vez de afirmar TENSIÓN o NORMAL (P3).
- **Entregable:** ficha municipal en español + explicación sin palabras causales.
- **Prompt asociado:** **11 · Explicabilidad SHAP lenguaje natural**.

### Fase 12 — Publicación en Oracle y capa APEX (27-28 octubre)
- **Responsable:** P3 (APEX/UI), P1 (geometría), P2 (Python→Oracle).
- **Subfases:**
  - F12.1: Sustituir el prototipo `index.html` estático por la aplicación Oracle APEX real (P3).
  - F12.2: 3 páginas APEX en el MVP (dashboard+mapa, explorador, ficha+simulador); las 9 páginas del diseño original quedan como roadmap (P3).
  - F12.3: Vistas APEX con `origen`, `metodo`, `dataset_version` (P3).
  - F12.4: DDL con `CHECK`/regex de `origen` en la base de datos, no solo en Python (P1/P2) — ya implementado en `02-tablas_procesadas.sql`.
  - F12.5: Geometría poblada (lat/lon o SDO_GEOMETRY) para el mapa (P1).
- **Entregable:** tablas Oracle + vistas APEX + export del workspace.
- **Prompt asociado:** **12 · Publicación Oracle y capa APEX**.

### Fase 13 — Model cards e informe técnico (28 octubre)
- **Responsable:** P3.
- **Subfases:**
  - F13.1: Model cards con sección obligatoria "Límites y riesgos conocidos" (≥4 ítems, cada uno con ejemplo concreto de municipio donde el modelo falla) (P3).
  - F13.2: Informe técnico para administraciones + glosario (P3).
  - F13.3: Cross-check de números: script que verifica que cada número del informe existe en los artefactos y que informe, model card y APP coinciden (P3).
- **Entregable:** model cards + informe + verificación de consistencia.
- **Prompt asociado:** **13 · Model cards e informe técnico**.

### Fase 14 — Revisión adversarial del pipeline (28 octubre)
- **Responsable:** Todos (revisión cruzada).
- **Subfases:**
  - F14.1: 12 ataques concretos: consistencia pipeline/publicado, tautología del ICA, no-compensatoriedad, caducidad del GTFS, backtest honesto, municipios excluidos, escala relativa vs absoluta, credibilidad del What-If, reproducibilidad real, correspondencia de municipios, trazabilidad de la narrativa, cumplimiento de claims del PDF de diseño (tabla APTO/PARCIAL/NO CUMPLIDO) (todos).
  - F14.2: Sección de "puntos fuertes" (una revisión solo negativa no genera confianza) (todos).
- **Entregable:** revisión de 12 ataques + sección de puntos fuertes.
- **Prompt asociado:** **14 · Revisión adversarial pipeline**.

### Fase 15 — Preparación de la presentación para instituciones (28-29 octubre)
- **Responsable:** P3 (contenido), P2 (demo en vivo).
- **Subfases:**
  - F15.1: Guion de 15 minutos, lenguaje no técnico (no decir SHAP, float32, ONNX, AVM ante el jurado) (P3).
  - F15.2: Diapositivas visuales: mapa semafórico, tabla inversión→municipios beneficiados, efecto spillover (P3).
  - F15.3: Simulador what-if en vivo durante la presentación (P2).
  - F15.4: Ensayo cronometrado 15 min + preparación para preguntas del jurado (P3).
- **Entregable:** diapositivas + guion cronometrado + demo lista.

### Fase 16 — Cierre y entrega (29 octubre)
- **Responsable:** Todos.
- **Subfases:**
  - F16.1: Commit final limpio en GitHub (P1).
  - F16.2: Datasets y prototipo accesibles para el jurado durante la deliberación (P2).
  - F16.3: Presentación cargada y probada en el ordenador del salón UC3M (P3).
- **Entregable:** entrega lista antes del 29 oct, 10:00 (inicio del evento).

---

## 9. Matriz: fases ↔ prompts operativos de `PROMPTS-LoDCORE`

| Fase | Subfases clave | Responsable | Prompt operativo | Qué produce el prompt |
|------|---------------|-------------|------------------|----------------------|
| F0 | Fundación y reparto | P1/P3/TODOS | (ninguno operativo) | Repositorio, roles, issues |
| F1 | Ingesta fuentes oficiales | P1 | **01 · Ingesta de fuente oficial** | Conector + datos con procedencia |
| F2 | Calidad y procedencia | P1 | **02 · Auditoría de calidad y procedencia** | Informe de calidad y veredicto |
| F3 | Fuga de información | P2 | **03 · Auditoría de fuga de información** | Informe de fuga + experimentos |
| F4 | Validación temporal-espacial | P2 | **04 · Diseño de validación temporal y espacial** | Protocolo + métricas con banda |
| F5 | M1 AVM | P2 | **05 · Modelo AVM Random Forest / LightGBM** | AVM + esfuerzo + bandas |
| F6 | M2 Índices + isócronas | P2 | **06 · Modelo índices PCA + isócronas** | Isócronas + 4 sub-índices 0-100 |
| F7 | M3 Demografía | P2 | **07 · Modelo proyección demográfica** | Población +5/+10 con bandas |
| F8 | M4 Capacidad de acogida | P2 | **08 · Modelo capacidad acogida XGBoost + SHAP** | ICA + atribuciones + simulador |
| F9 | M4b No-compensatoriedad | P1 | **09 · Cuellos de botella no compensatorios** | No-compensatoriedad + test |
| F10 | M5 Recomendador | P2 | **10 · Recomendador clustering + MCDM** | Clusters + ranking + exclusiones |
| F11 | Explicabilidad en lenguaje natural | P3 | **11 · Explicabilidad SHAP lenguaje natural** | Ficha municipal en español |
| F12 | Publicación Oracle/APEX | P3/P1/P2 | **12 · Publicación Oracle y capa APEX** | Tablas + vistas + export APEX |
| F13 | Documentación técnica | P3 | **13 · Model cards e informe técnico** | Model cards + informe + glosario |
| F14 | Revisión adversarial | Todos | **14 · Revisión adversarial pipeline** | Revisión de 12 ataques |
| F15 | Presentación | P3/P2 | Prompts 11 + 13 + revisión manual | Diapositivas + guion 15 min |
| F16 | Entrega | Todos | Prompt 14 (revisión final) | Entrega lista para el jurado |

### Flujo encadenado recomendado (desde `00-INDICE-Y-METODOLOGIA.md`)

```
01-ingesta-fuente-oficial
  └─> 02-auditoria-calidad-y-procedencia
        └─> 03-auditoria-fuga-informacion
              └─> 04-diseno-validacion-temporal-espacial
                    ├─> 05-modelo-avm-random-forest (M1)
                    ├─> 06-modelo-indices-pca-isocronas (M2)
                    │     └─> 07-modelo-proyeccion-demografica (M3)
                    │           └─> 08-modelo-capacidad-acogida-xgboost-shap (M4)
                    │                 └─> 09-cuellos-botella-no-compensatorios
                    ├─> 10-recomendador-clustering-mcdm (M5)
                    └─> 11-explicacion-shap-lenguaje-natural
                          └─> 12-publicacion-oracle-y-apex
                                └─> 13-model-cards-e-informe-tecnico
                                      └─> 14-revision-adversarial-pipeline
```

### Reparto de prompts por persona (para que no se pisen)

- **P1 (Datos + M4):** 01, 02, 03, 09 (y geometría para APEX en 12).
- **P2 (Modelos + API):** 04, 05, 06, 07, 08, 10, 12 (parte técnica de publicación Python→Oracle).
- **P3 (APEX + Presentación):** 11, 12 (parte APEX/UI), 13, 14 (revisión final conjunta), 15, 16.

---

## 10. Cómo ejecutar el proyecto

Desde la raíz del repositorio activo (`codigo/DatathonLodCoreMadrid/` o la ruta que se establezca):

```powershell
pip install -r requirements.txt
python scripts/run_all_models_n1_n2_n3.py
pytest tests -q
```

Para servir la API N3:

```powershell
uvicorn src.lodcore.serving.fastapi.app:app --reload
```

Endpoints activos: `/health`, `/recomendar`, `/whatif`, `/optimizar-presupuesto`.

---

## 11. Datos y trazabilidad

- Procedencia en dos niveles: a nivel de fila, el panel lleva `origen`/`metodo`/`fuente_datos`; a nivel de variable, el desglose fino está en `docs/matriz_procedencia_variables.md`. Publicar una variable sin procedencia declarada es un bug.
- `fecha_disponible` por fila: punto-en-tiempo, evita fuga temporal. Se deriva
  de los snapshots realmente consumidos.
- `fecha_decision` del MVP: `FECHA_DECISION_MVP` en
  `scripts/run_all_models_n1_n2_n3.py` (hoy `2026-10-24`). Si se actualizan los
  snapshots, hay que actualizarla de forma explícita para no usar datos futuros.
- `dataset_version`: `v1.0.0-F2`.
- Fuentes oficiales: INE (Padrón 2025) y CKAN Comunidad de Madrid están conectadas; Catastro, CRTM, Notariado, IGN/CNIG, MITECO, Renfe y Canal Isabel II quedan como referencia/roadmap (ver `docs/material_reto/Fuentes de datos.pdf` y la matriz de procedencia).

---

## 12. Presentación final (15 min, audiencia institucional)

**Mensaje central:** "No decimos solo dónde falta sanidad o educación; decimos matemáticamente en qué municipio de cada comarca hay que invertir con un presupuesto dado para maximizar la capacidad de acogida de toda la zona." (El efecto en pueblos vecinos —spillover— se presenta como roadmap, no como funcionalidad.)

**Estructura sugerida (15 min):**
1. Problema y reto (2 min) — municipios <50k, reto demográfico CAM.
2. Solución y arquitectura (3 min) — MVP funcional, datos abiertos, Oracle APEX.
3. Demo en vivo (5 min) — mapa semafórico + simulador what-if (construir centro de salud/colegio y ver impacto en la comarca).
4. Diferenciador: optimizador comarcal (3 min) — dónde invertir para maximizar acogida. Presentar la asignación presupuestaria comarcal determinista (M4-OPT) y el roadmap de spillover continuo.
5. Cierre y pedido (2 min) — escalabilidad a todos los <50k, próximos pasos.

**Nunca decir ante el jurado:** "SHAP", "float32", "ONNX", "AVM", "p-valor", "gradient boosting". Decir: "el modelo identifica el cuello de botella", "el modelo se ejecuta dentro de Oracle para ser rápido y seguro", "estimador de precio de referencia".

---

## 13. Flujo de trabajo GitHub (3 personas)

- Rama `main`: estable, solo se integra tras revisión.
- Cada persona trabaja en su rama propia (ramas reales del equipo: `p1/datos`, `juancho`, `fix/...`).
- Issues por subfase (ver Fase 0 a Fase 16). Asignar issue a la persona responsable.
- Pull Requests: revisados por al menos otro miembro antes de mergear a `main`.
- Commits con mensaje descriptivo: `feat(p1): añade trazabilidad origen/metodo en data/validated/`.
- No hacer push directo a `main`.

---

## 14. REGLA DE ACTUALIZACIÓN DEL CONTEXTO (OBLIGATORIA)

Cada vez que algún miembro del equipo termine de modificar algo relevante en el proyecto (código, datos, modelo, DDL, UI, documentación), debe **publicar un texto resumen en el grupo del equipo** para que los otros dos miembros y sus respectivas IAs puedan actualizar su contexto y no trabajen con información desactualizada.

**Formato sugerido del resumen:**
```
[Fecha] [Persona]
Archivos modificados: ruta/archivo1, ruta/archivo2
Cambio clave: descripción breve de qué se cambió
Impacto en otras áreas: qué podría afectar a P2/P3 o a los modelos
Acción requerida: ¿alguien más debe hacer algo por este cambio?
```

Ejemplo:
```
[24 oct] P1
Archivos modificados: data/validated/municipios_panel_validado.csv, src/lodcore/data/provenance.py
Cambio clave: se añadió origen='OBSERVADO' y metodo='PADRON_INE_2025' a las columnas de población.
Impacto en otras áreas: P2 debe regenerar métricas de M4 si cambian los valores de entrada; P3 debe actualizar la vista APEX si cambia el esquema.
Acción requerida: P2 ejecuta run_all_models_n1_n2_n3.py y avisa.
```

Este archivo `project_context.md` debe considerarse la fuente de verdad operativa. Si alguien crea una IA nueva o se une un colaborador, este es el primer documento que debe leer.

---

## 15. Diagrama de flujo del proyecto

Ver archivo `diagrama_flujo.mmd` (formato Mermaid, renderizable en Mermaid Live Editor, GitHub, Notion, Obsidian, etc.) y `diagrama_flujo.png` (imagen ya generada). **Es un resumen visual en 7 bloques con subfases y responsable por nodo**; el detalle completo de las 16 fases está en la sección 8 de este documento. Pendiente: ampliar este resumen a una vista única de las 16 fases.
