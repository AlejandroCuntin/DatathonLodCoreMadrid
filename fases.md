# Fases del proyecto — LoDCORE Madrid

Plan de ejecución en **10 fases (F1–F10)** a lo largo de ~13 semanas.
Las fases de datos (F1–F2) son secuenciales; las de modelado (F3–F7) se solapan en el calendario; validación (F8) y publicación (F9) son transversales al final; F10 cierra y deja el sistema reproducible.

---

## 0. Resumen

| Fase | Nombre | Semanas | Tipo | Entregable principal |
|---|---|---|---|---|
| **F1** | Adquisición de datos públicos | 1–3 | Datos | `data/raw/` inmutable + DVC |
| **F2** | ETL, calidad y punto-en-tiempo | 3–5 | Datos | `data/processed/` y `data/validated/` |
| **F3** | M1 — AVM y asequibilidad | 5–7 | Modelo | Precio justo m² + esfuerzo familiar con banda 95 % |
| **F4** | M2 — Indicadores de capacidad e infraestructura | 6–8 | Modelo | 4 sub-índices 0–100 + isócronas 30 min |
| **F5** | M3 — Proyección demográfica | 7–9 | Modelo | Proyección 5/10 años con escenarios +5 % / +10 % |
| **F6** | M4 — Capacidad de acogida y simulación de inversiones | 8–11 | Modelo (core) | Índice de capacidad + SHAP + simulador |
| **F7** | M5 — Recomendador personalizado | 9–11 | Modelo | Ranking por preferencias + comparador |
| **F8** | Validación rigurosa y auditoría | 10–12 | Transversal | `docs/validacion.md` con evidencia |
| **F9** | Publicación Oracle + APEX | 11–13 | Serving | DDL, ONNX en Oracle, 9 páginas APEX |
| **F10** | Despliegue, monitoreo y cierre | 13+ | Operación | `dvc repro` completo + CI/CD + documentación |

**Hitos de control:** fin de F1 (fuentes congeladas), fin de F2 (dataset validado), fin de F6 (modelo core con no-compensatoriedad), fin de F8 (métricas auditadas), fin de F9 (APEX operativo).

---

## F1 — Adquisición de datos públicos (semanas 1–3)

**Objetivo:** descargar e inmovilizar todas las fuentes oficiales en `data/raw/`.

**Conectores** (uno por fuente, ya verificados en *Fuentes de datos.pdf*):

| Fuente | Datos que aporta | Carpeta destino |
|---|---|---|
| INE (Padrón, Tempus3, renta, pirámide, saldos migratorios) | Población, estructura generacional, renta media hogar | `data/raw/ine/` |
| CKAN Comunidad de Madrid (`datos.comunidad.madrid`) | Centros sanitarios, educación, servicios sociales, residuos, calidad aire, presupuestos | `data/raw/ckan_madrid/` |
| Catastro (`SECAccDescargaDatos`, estadísticas) | Valor catastral, superficie, precios referencia | `data/raw/catastro/` |
| CRTM GTFS (`datos.crtm.es`) | Redes transporte público, horarios, paradas | `data/raw/crtm_gtfs/` |
| Renfe (datos abiertos) | Cercanías y media distancia | `data/raw/renfe/` |
| OSM / Geofabrik | Red viaria, tiempos acceso privado | `data/raw/osm/` |
| IGN / CNIG CartoBase | Límites municipales, geometría ETRS89 | `data/raw/ign_cnig/` |
| MITECO (SNCZI, calidad aire) | Agua, riesgos, sostenibilidad ambiental | `data/raw/miteco/` |
| Notariado.org | Precios vivienda compra/venta | `data/raw/notariado/` |
| Canal de Isabel II | Datos agua por municipio | `data/raw/canal_isabel_ii/` |

**Regla:** `data/raw/` es inmutable y versionado con DVC. Ningún dato entra al pipeline sin registro de `fecha_disponible` (punto-en-tiempo).

**A quién sirve:** instituciones (datos oficiales auditables) y ciudadanos (recomendación basada en datos reales, no opiniones).

---

## F2 — ETL, calidad y punto-en-tiempo (semanas 3–5)

**Objetivo:** producir `data/processed/` y `data/validated/`.

**Actividades:**

- Join de los 7 bloques de factores en panel municipal (una fila por municipio y año).
- Esquemas pandera por fuente y por fase.
- Asignación de `origen` (`OBSERVADO | IMPUTADO | ESTIMADO | PROYECTADO | SIMULADO`) y `metodo` en cada celda.
- Puertas de calidad: pandera en Python, tests de `dbt-oracle` en SQL (Great Expectations no se usa en Oracle por el bug `FROM DUAL` → `ORA-00907`).
- Control de punto-en-tiempo: el modelo nunca ve un valor publicado después de la fecha de decisión.

**Rigor:** una celda sin `origen` y `metodo` es un bug, no una excepción.

---

## F3 — Modelo M1: AVM y asequibilidad (semanas 5–7)

**Objetivo:** estimar precio justo por m² y esfuerzo financiero familiar en los 41 municipios.

**Algoritmo:** Random Forest / LightGBM. Regresión sobre árboles.

**Entradas:** Catastro, renta media por hogar (INE).

**Rigor específico n=41:** pocos municipios ⇒ alta varianza. Evaluación con `GroupKFold` + split temporal + spatial K-fold con buffer 20–30 km en EPSG:25830. Banda de incertidumbre 95 % (quantile regression o NGBoost, no solo RF punto).

**Salida:** `m1_avm/metrics.json`, modelo ONNX, predicciones con banda.

**A quién sirve:** ciudadanos (¿puedo permitirme vivir aquí?) e instituciones (presión inmobiliaria).

---

## F4 — Modelo M2: Indicadores de capacidad e infraestructura (semanas 6–8)

**Objetivo:** condensar decenas de variables correlacionadas en 4 sub-índices 0–100.

**Algoritmo:** PCA + MinMaxScaler. Grafos geoespaciales (Dijkstra / A* sobre OSM + GTFS) para isócronas.

**Sub-índices:**

1. Capacidad Sanitaria/Educativa.
2. Conectividad y Movilidad.
3. Sostenibilidad Ambiental.
4. Músculo Presupuestario/Inversor.

**Criterio «municipio de 30 minutos»:** acceso en transporte público vs privado a polos de empleo y hospitales de referencia.

**Salida:** `m2_indicadores/metrics.json`, sub-índices por municipio.

**A quién sirve:** instituciones (diagnóstico de cuellos de botella) y ciudadanos (tiempos reales de transporte).

---

## F5 — Modelo M3: Proyección demográfica (semanas 7–9)

**Objetivo:** proyectar población a 5 y 10 años bajo escenarios explícitos.

**Algoritmo:** SARIMAX / Prophet (series temporales multivariantes).

**Entradas:** Padrón Municipal histórico (INE/IECM), pirámide de edad, saldos migratorios, proyecciones oficiales. Exógenos: precios Madrid capital, presupuesto inversión municipal.

**Salida:** proyección con bandas de incertidumbre 95 %. Escenarios base, +5 %, +10 % de población.

**Rigor:** M4 no puede usar el futuro de M3. La demanda proyectada se cruza con oferta histórica.

**A quién sirve:** instituciones (planificación a 5–10 años) y ciudadanos (¿crecerá este municipio?).

---

## F6 — Modelo M4: Capacidad de acogida y simulación de inversiones (semanas 8–11)

**Objetivo:** identificar cuellos de botella limitantes y predecir el índice de capacidad de acogida futura.

**Algoritmo:** XGBoost Regressor + SHAP (explicabilidad).

**Entradas:** demanda futura (F3) + oferta de vivienda (F1) + servicios, transporte, medioambiente, presupuestos (F2).

> Ver *Observaciones de consistencia* al final: la demanda futura procede de F5 (M3).

**Regla de no-compensatoriedad:** un municipio con un servicio crítico colapsado (ratio > 1.500 hab/médico, ocupación > 95 %, ICA baja) no puede obtener score alto acumulando otros factores. Se aplica en capa de reglas (mínimo sobre sub-índices, umbrales duros).

**Salidas:** índice de capacidad, fortalezas/carencias por SHAP, simulador paramétrico (¿qué pasa si el ayuntamiento aumenta presupuesto transporte o construye centro educativo?).

**A quién sirve:** instituciones (dónde invertir) y ciudadanos (¿este municipio me acoge sin colapsar?).

---

## F7 — Modelo M5: Recomendador personalizado (semanas 9–11)

**Objetivo:** ranking de municipios adaptado al presupuesto y estilo de vida del ciudadano.

**Algoritmo:** clustering no supervisado (K-Means / GMM) + similitud del coseno ponderada (MCDM).

**Tipologías:** nodos metropolitanos dinámicos, municipios familiares de calidad ambiental, pueblos rurales conectados para teletrabajo.

**Entradas:** estructura de hogares, distribución por edades, preferencias del ciudadano (interfaz web).

**Salida:** ranking personalizado, comparación lado a lado de hasta 3 municipios, ficha municipal con ventajas y riesgos futuros.

**A quién sirve:** ciudadanos (perfil 1 del prototipo).

---

## F8 — Validación rigurosa y auditoría (semanas 10–12, transversal)

**Objetivo:** demostrar que los resultados son válidos, no optimísticamente sesgados.

**Actividades:**

- **Nested CV** para métricas publicadas (n=41, un solo CV es sesgado).
- **Spatial K-fold** con buffer 20–30 km, distancias en EPSG:25830 (nunca grados). Reportar dispersión entre folds.
- **Test de equivalencia ONNX vs Python:** `|score_ONNX − score_Python| < 1e-6` en CI.
- **Auditoría SHAP:** background fijado y persistido (hash). Sin causalidad en la redacción.
- **Revisión adversarial:** prompts de validación que intentan romper la no-compensatoriedad.

**Entregable:** `docs/validacion.md` con todas las métricas y su evidencia en ficheros de resultados (regla `AGENTS.md`: todo número debe existir en un fichero).

**A quién sirve:** instituciones (confianza en el sistema para decisiones de gasto público).

---

## F9 — Publicación Oracle + APEX (semanas 11–13)

**Objetivo:** llevar el modelo a producción en Oracle Database y exponerlo por APEX.

### Niveles de serving

| Nivel | Entorno | Función |
|---|---|---|
| **N1** | Entrenamiento (Python/CI) | Modelos entrenados y exportados a ONNX |
| **N2** | Scoring en Oracle | `DBMS_VECTOR.LOAD_ONNX_MODEL` + `PREDICTION()`. Ningún modelo se entrena dentro de APEX |
| **N3** | FastAPI | Solo `/recomendar` y `/whatif` |

### Páginas APEX (prototipo, 9 páginas)

**Portal ciudadano**

1. Cuestionario de preferencias + ranking personalizado.
2. Ficha municipal detallada con ventajas y riesgos futuros.
3. Comparador lado a lado (hasta 3 municipios): chart Radar nativo (3 series, 7 ejes = 7 capas).
4. Semáforo ICA: Status Meter Gauge (Baja < 40, Media 40–59, Alta ≥ 60).

**Panel institucional**

5. Visión agregada por comarcas y coronas.
6. Matriz de diagnóstico de cuellos de botella.
7. Índice de saturación vs tasa de crecimiento esperada.
8. Simulador paramétrico de inversiones con control presupuestario.
9. Exportación de informes técnicos reproducibles + página «Fuentes Oficiales» (atribución IGN CC BY 4.0).

**Regla Oracle:** toda vista expuesta a APEX incluye `origen`, `metodo`, `dataset_version`. El DDL de `oracle/ddl/` es fuente de verdad; APEX consume, no redefine.

**A quién sirve:** ciudadanos (portal) e instituciones (panel + simulador).

---

## F10 — Despliegue, monitoreo y cierre (semana 13+)

**Objetivo:** operación sostenible y reproducción completa.

**Entregables:**

- `dvc.yaml` ejecutable: `dvc pull && dvc repro` reconstruye todo desde cero.
- CI/CD: `ruff`, `mypy`, `pytest`, equivalencia ONNX.
- MLflow UI para experimentos.
- Changelog de municipios (`docs/cambios.md`).
- Documentación final para ciudadanos e instituciones.

**A quién sirve:** ambos perfiles (el sistema mantiene utilidad en el tiempo).

---

## Reglas transversales (aplican a todas las fases)

| Regla | Dónde se materializa |
|---|---|
| `data/raw/` inmutable; todo cambio de datos es una nueva versión DVC | F1, `docs/cambios.md` |
| Toda celda lleva `origen` + `metodo`; sin ellos es un bug | F2, `src/lodcore/data/provenance.py` |
| `fecha_disponible` por fila: sin fuga temporal | F2, `src/lodcore/data/pointintime.py` |
| Métricas solo con nested CV + spatial K-fold (EPSG:25830, buffer 20–30 km) | F3–F8 |
| Ninguna predicción se publica sin banda de incertidumbre 95 % | F3, F5, M4, `publish/uncertainty_band.py` |
| La no-compensatoriedad es una capa de reglas duras, no un peso más | F6, `src/lodcore/models/m4_capacidad/reglas_no_compensatorias.py` |
| SHAP describe el modelo, nunca causalidad | F6, F8, `src/lodcore/explain/` |
| Equivalencia ONNX ↔ Python < 1e-6 obligatoria en CI | F8, F9 |
| Toda vista APEX incluye `origen`, `metodo`, `dataset_version` | F9, `oracle/ddl/03-vistas_apex.sql` |
| Todo número publicado existe en un fichero de resultados | F8, `docs/validacion.md` |

---

## Observaciones de consistencia

- **F6 — entradas:** el texto original cita «demanda futura (F3)». La proyección de demanda se produce en **F5 (M3)**; F3 (M1) aporta precios y esfuerzo financiero. Se mantiene la referencia original arriba y se anota aquí para evitar ambigüedad al implementar los joins.
- **Solapamiento de calendario:** F3–F7 arrancan escalonadas y comparten semanas; el orden de dependencias real es F1 → F2 → (F3, F4, F5) → F6 → (F7) con F8/F9 en paralelo al cierre.
- **`docs/metrologia.md`** (target operativo de M4) sigue pendiente de validación antes de cerrar F6.
