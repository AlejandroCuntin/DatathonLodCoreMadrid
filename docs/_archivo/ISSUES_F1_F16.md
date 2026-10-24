# Tablero de Issues GitHub — II Datathon LoDCORE Madrid (F1 a F16)
> Reparto de responsabilidades acordado en F0.3:
> - **P1**: Datos + Ingesta + Reglas de negocio/no-compensatoriedad + Optimizador M4
> - **P2**: Modelos M1–M5 + Validación + API FastAPI + ONNX
> - **P3**: Oracle APEX + Vistas + Explicabilidad NL + Presentación jurado

---

### Issue #1: [F1] Ingesta de fuentes oficiales y snapshot inmutable
- **Asignado a**: @P1 (Datos)
- **Fase**: Fase 1
- **Fecha objetivo**: 24 octubre 2026
- **Descripción**:
  - Conectar o snapshottear datos oficiales: Padrón INE 2025 (tabla 2881) y CKAN Comunidad de Madrid (sanidad/educación).
  - Almacenar snapshot crudo con fecha en `data/raw/` de forma inmutable.
  - Cruce de datos por código INE de 5 dígitos estricto (nunca por nombre).
  - Trazabilidad de origen y método por variable.
- **Criterio de aceptación**:
  - Módulo conector Python en `src/lodcore/ingest/`.
  - Snapshot en `data/raw/` con timestamp ISO.
  - Validación de 20 municipios piloto mediante código INE.

---

### Issue #2: [F2] Auditoría de calidad, metrología y procedencia
- **Asignado a**: @P1 (Datos)
- **Fase**: Fase 2
- **Fecha objetivo**: 24 octubre 2026
- **Descripción**:
  - Distinguir datos no aplicables de faltantes.
  - Clasificación de outliers e imputaciones.
  - Recálculo independiente de hab/médico y ocupación escolar.
  - Veredicto formal por escrito: APTO / APTO CON RESERVAS / NO APTO en `docs/validacion.md`.
- **Criterio de aceptación**:
  - Quality gates ejecutados en Python (`src/lodcore/data/quality_gates.py`).
  - Documento `docs/validacion.md` actualizado con veredicto.

---

### Issue #3: [F3] Auditoría de fuga de información (L1-L7)
- **Asignado a**: @P2 (Modelos)
- **Fase**: Fase 3
- **Fecha objetivo**: 25 octubre 2026
- **Descripción**:
  - Revisar los 7 tipos de fuga (L1–L7) y el sesgo de selección.
  - Comprobar que el target ICA no use variables futuras y que `fecha_disponible` se respete.
  - Experimento empírico de entrenamiento con y sin fuga.
- **Criterio de aceptación**:
  - Test de integración `tests/integration/test_no_leakage.py` y `test_pointintime.py` en verde.
  - Tabla de experimentos y dictamen de fuga en documentación.

---

### Issue #4: [F4] Diseño de validación temporal y espacial
- **Asignado a**: @P2 (Modelos)
- **Fase**: Fase 4
- **Fecha objetivo**: 25 octubre 2026
- **Descripción**:
  - Implementar GroupKFold por comarca y split temporal.
  - Banda del 95% por bootstrap de municipios.
  - 4 baselines naive de referencia.
- **Criterio de aceptación**:
  - Métricas honestas reportadas sin sobreajuste in-sample.
  - Módulo de validación cruzada espacial.

---

### Issue #5: [F5] Modelo M1 — AVM Inmobiliario y Asequibilidad
- **Asignado a**: @P2 (Modelos)
- **Fase**: Fase 5
- **Fecha objetivo**: 25-26 octubre 2026
- **Descripción**:
  - RandomForestRegressor para precio €/m² compra y alquiler.
  - Cálculo de esfuerzo financiero familiar.
  - Exportación a ONNX y prueba de equivalencia N1/N2.
- **Criterio de aceptación**:
  - Artefacto `m1_avm.onnx` en `oracle/onnx/`.
  - Diferencia relativa contra predicción Python $< 10^{-6}$ y absoluta $< 10^{-3}$.

---

### Issue #6: [F6] Modelo M2 — Indicadores de capacidad e Isócronas
- **Asignado a**: @P2 (Modelos)
- **Fase**: Fase 6
- **Fecha objetivo**: 25-26 octubre 2026
- **Descripción**:
  - PCA + normalización [0, 100] para los 4 sub-índices.
  - Heurística y verificación de criterio "municipio de 30 minutos".
  - Fijar signos de componentes PCA para reproducibilidad.
- **Criterio de aceptación**:
  - Sub-índices persistidos en el panel municipal.
  - Signos de PCA estables en tests.

---

### Issue #7: [F7] Modelo M3 — Proyección demográfica a 5 y 10 años
- **Asignado a**: @P2 (Modelos)
- **Fase**: Fase 7
- **Fecha objetivo**: 26 octubre 2026
- **Descripción**:
  - Extrapolación geométrica calibrada con padrón oficial 2031.
  - Bandas de incertidumbre al 95%.
  - Escenarios de estrés (+5% y +10% de población).
- **Criterio de aceptación**:
  - Proyecciones 2030 y 2035 por municipio con bandas en `metrics.json`.

---

### Issue #8: [F8] Modelo M4 — Capacidad de Acogida (ICA)
- **Asignado a**: @P2 (Modelos) y @P1 (Reglas de negocio)
- **Fase**: Fase 8
- **Fecha objetivo**: 26-27 octubre 2026
- **Descripción**:
  - GradientBoostingRegressor sobre sub-índices con atribuciones aditivas.
  - Detección de cuellos de botella y simulador what-if.
  - Exportación ONNX y carga en Oracle.
- **Criterio de aceptación**:
  - Artefacto `m4_capacidad.onnx` generado.
  - Equivalencia ONNX verificada en tests.

---

### Issue #9: [F9] Modelo M4b — Cuellos de botella y salvaguardas no compensatorias
- **Asignado a**: @P1 (Datos + Reglas)
- **Fase**: Fase 9
- **Fecha objetivo**: 26-27 octubre 2026
- **Descripción**:
  - Regla de veto ante colapso sanitario (>1.500 hab/médico) o educativo (>95% ocupación escolar).
  - Truncamiento a ICA < 40 (idoneidad BAJA) sin compensación.
- **Criterio de aceptación**:
  - Módulo `reglas_no_compensatorias.py` activo en backend y API `/whatif`.
  - Tests unitarios en verde.

---

### Issue #10: [F10] Modelo M5 — Recomendador ciudadano inteligente
- **Asignado a**: @P2 (Modelos)
- **Fase**: Fase 10
- **Fecha objetivo**: 27 octubre 2026
- **Descripción**:
  - Clustering K-Means sobre características territoriales.
  - Ranking MCDM por similitud del coseno ponderada con filtros duros.
- **Criterio de aceptación**:
  - Endpoint `/recomendar` operativo en FastAPI.
  - Clusters con nombres verificables y reproducibles.

---

### Issue #11: [F11] Explicabilidad en lenguaje natural y fichas municipales
- **Asignado a**: @P3 (APEX + Comunicación)
- **Fase**: Fase 11
- **Fecha objetivo**: 27 octubre 2026
- **Descripción**:
  - Generación de textos institucionales y ciudadanos cumpliendo las 8 reglas de redacción (sin causalidad, con umbral numérico, sin jerga).
- **Criterio de aceptación**:
  - Plantillas en `src/lodcore/explain/plantillas_es.md` y tests de redacción sin términos causales.

---

### Issue #12: [F12] Publicación en Oracle AI Database y Oracle APEX
- **Asignado a**: @P3 (APEX) y @P1 (Geometría / DDL) y @P2 (Writer)
- **Fase**: Fase 12
- **Fecha objetivo**: 27-28 octubre 2026
- **Descripción**:
  - Creación de 3 páginas esenciales en APEX (Dashboard comarcal, Mapa semafórico, Ficha + What-if).
  - Vistas SQL con metadatos de trazabilidad (`origen`, `metodo`, `dataset_version`).
  - Capa geográfica SDO_GEOMETRY / GeoJSON.
- **Criterio de aceptación**:
  - DDL de tablas y vistas aplicable en Oracle.
  - Export de la aplicación APEX o script de configuración.

---

### Issue #13: [F13] Model cards e informe técnico de metrología
- **Asignado a**: @P3 (Documentación)
- **Fase**: Fase 13
- **Fecha objetivo**: 28 octubre 2026
- **Descripción**:
  - Model card por modelo M1–M5 con sección "Límites y riesgos conocidos".
  - Verificación de consistencia entre texto y datos.
- **Criterio de aceptación**:
  - Documentos `docs/metrologia.md` y model cards completas.

---

### Issue #14: [F14] Revisión adversarial del pipeline (12 ataques)
- **Asignado a**: @TODOS (Revisión cruzada)
- **Fase**: Fase 14
- **Fecha objetivo**: 28 octubre 2026
- **Descripción**:
  - Evaluación de los 12 puntos de ataque crítico (R1–R12) identificados en la arquitectura.
  - Identificación de fortalezas defensivas ante preguntas del jurado.
- **Criterio de aceptación**:
  - Matriz de defensa adversarial documentada.

---

### Issue #15: [F15] Preparación del guion y presentación institucional
- **Asignado a**: @P3 (Guion) y @P2 (Demo) y @P1 (Datos clave)
- **Fase**: Fase 15
- **Fecha objetivo**: 28-29 octubre 2026
- **Descripción**:
  - Guion de 15 minutos en lenguaje no técnico.
  - Diapositivas institucionales para UC3M y Comunidad de Madrid.
  - Ensayo cronometrado con demo what-if en vivo.
- **Criterio de aceptación**:
  - Diapositivas listas y guion cerrado con mensajes clave.

---

### Issue #16: [F16] Cierre de entrega y congelación del repositorio
- **Asignado a**: @TODOS
- **Fase**: Fase 16
- **Fecha objetivo**: 29 octubre 2026 (10:00 AM)
- **Descripción**:
  - PR final integrado en `main`.
  - Repositorio limpio y reproducible con un solo comando.
  - Documentación de acceso para el jurado.
- **Criterio de aceptación**:
  - Repositorio listo para evaluación final.
