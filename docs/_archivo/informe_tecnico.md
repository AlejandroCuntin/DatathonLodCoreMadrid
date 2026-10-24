# Informe Técnico para Administraciones Públicas
## LoDCORE Madrid · Capacidad de Acogida Municipal
### II Datathon LoDCOREMadrid 2026 · `dataset_version = v1.0.0-F2`

> **Para quién es este informe:** Dirección General de Reequilibrio Territorial, ayuntamientos,
> consorcios comarcales y equipos técnicos que necesiten entender qué mide la herramienta, con
> qué datos y con qué límites. **No es un informe comercial.**

---

## 1. Resumen ejecutivo

LoDCORE Madrid es una herramienta de diagnóstico territorial que responde a una pregunta concreta:
**¿qué municipios de la Comunidad de Madrid pueden absorber nueva población sin que se rompan la
sanidad, la educación o la vivienda, y dónde conviene invertir primero?**

El MVP trabaja sobre **20 municipios de 8 comarcas** (todos <50.000 habitantes) y ofrece:

- Un **índice de capacidad de acogida (ICA)** de 0 a 100.
- Una **regla no compensatoria**: un servicio colapsado no se compensa con vivienda o suelo.
- Un **simulador what-if** para estimar el efecto de una inversión.
- Una **heurística de asignación presupuestaria comarcal** que reparte una partida cerrada.
- Un **paquete de datos** con diccionario, fuentes, procedencia y checksums.

**Resultado del piloto:** ICA medio 37,9/100; 12 municipios en alerta; 5.078 personas de capacidad
inmediata; 35,9 M€ de refuerzo estimado. **No es una predicción del futuro:** es un diagnóstico
con reglas explícitas y límites declarados.

---

## 2. El problema

La Comunidad de Madrid combina dos realidades: presión residencial en el área metropolitana y
municipios pequeños con capacidad ociosa o con servicios al límite. Repartir población “por partes
iguales” no funciona: un municipio con vivienda barata pero sin médico no puede absorber gente;
otro con hospital y colegio puede hacerlo aunque su suelo sea más caro.

La herramienta ordena esa complejidad en tres preguntas:
1. ¿Cuál es el **cuello de botella** de cada municipio?
2. ¿Cuánta población puede absorber **sin colapsar**?
3. Con un presupuesto cerrado, **¿en qué municipios se invierte primero?**

---

## 3. Solución y arquitectura

```
Datos oficiales (INE + CKAN)  →  Panel municipal validado  →  Modelos y reglas
        →  Oracle Database (scoring)  →  Oracle APEX + FastAPI (consulta y simulación)
```

- **N1 — Entrenamiento:** Python; modelos y artefactos versionados.
- **N2 — Scoring en Oracle:** los modelos se cargan dentro de Oracle; el cálculo no depende del portátil.
- **N3 — Consulta:** API FastAPI (`/recomendar`, `/whatif`, `/optimizar-presupuesto`) y portal APEX.

**Trazabilidad:** cada fila del panel lleva `origen`, `metodo`, `fuente_datos`, `dataset_version` y
`fecha_disponible`. El desglose por variable está en `docs/matriz_procedencia_variables.md`.

---

## 4. Datos: qué es real y qué es estimado

| Bloque | Fuente | Estado |
|---|---|---|
| Población y año de padrón | INE, tabla 2881, 2025 | **OBSERVADO** (snapshot 24-10-2026) |
| Centros de salud y educativos | CKAN Comunidad de Madrid, CC BY 4.0 | **OBSERVADO** (snapshot 24-10-2026) |
| Médicos de AP, plazas, alumnado | Calibración interna (seed 2026) | **SIMULADO** |
| Vivienda vacía, suelo, precios | Calibración interna (seed 2026) | **SIMULADO** |
| Scores e ICA | Cálculo del equipo | **ESTIMADO** |
| Proyecciones 2027/2029/2031 | Modelo M3 | **PROYECTADO** |

**Cobertura:** 20 de 155 municipios <50k (12,9 %); 200.267 habitantes (20,1 % de la población de
los menores de 50k). **Sesgo declarado:** el piloto sobrerrepresenta municipios de 5.000–20.000
(14/20 frente a 46/155) e infrarrepresenta los <5.000 (4/20 frente a 96/155).

**Fuentes pendientes:** Catastro, CRTM, Notariado, SERMAS (detalle de cupos) y Consejería de
Educación (plazas/alumnado). Mientras no se conecten, sus variables son estimaciones declaradas.

---

## 5. Modelos y qué aporta cada uno

| Modelo | Qué hace | Límite principal |
|---|---|---|
| **M1** — precio de referencia | Compara asequibilidad y esfuerzo familiar | R² fuera de muestra negativo; no es una tasación |
| **M2** — indicadores | 4 subíndices 0–100 y criterio de 30 min | Heurística de tiempos, sin rutas OSM/GTFS |
| **M3** — demografía | Población 2030/2035 y año de saturación | Calibrado con 2031; sin backtest temporal |
| **M4** — capacidad (core) | ICA + reglas no compensatorias + what-if | El target es una fórmula; Ridge predice mejor |
| **M5** — recomendador | 4 arquetipos + ranking por preferencias | Silhouette 0,318; descriptivo, no predictivo |

**Fichas completas:** `docs/model_cards.md` (con límites y municipios donde fallan).

---

## 6. Validación y rigor

- **Validación espacial:** `GroupKFold` por comarca; nunca se entrena y evalúa con la misma comarca.
- **Auditoría de fuga (F3):** 7 tipos revisados; **0 bloqueantes, 2 materiales** (target determinista
  y sesgo de selección). Ver `docs/auditoria_fuga_informacion.md`.
- **Baselines y bootstrap (F4):** 4 referencias (media, mediana, lineal, Ridge) y banda del 95 %
  por bootstrap de municipios (B=1000). Ver `docs/validacion.md` §6.
- **Métricas clave:** M4 R² OOF 0,7345 / MAE 5,15; M1 R² OOF −0,3398 / MAE 382,83; M5 silhouette
  0,3183. **No se publica el R² in-sample de M4 (1,0)** como evidencia de generalización.
- **36 tests automáticos** y scripts de cross-check (`scripts/check_model_cards.py`,
  `scripts/audit_f3_leakage.py`).

---

## 7. Gobernanza, ética y uso responsable

- **No causalidad:** el modelo asocia; no afirma que una variable “cause” otra.
- **No decisiones automáticas:** la herramienta informa; la decisión de inversión es humana.
- **Procedencia obligatoria:** ninguna variable se publica sin origen y método.
- **Datos personales:** el panel es municipal; no contiene PII.
- **Licencias:** INE (reutilización con atribución) y CKAN CAM (CC BY 4.0). Ver
  `docs/fuentes_oficiales.md`.
- **Limitación de responsabilidad:** las estimaciones de dotación no sustituyen registros oficiales.

---

## 8. Cómo se usa

- **API:** `GET /health`; `POST /recomendar`; `POST /whatif`; `POST /optimizar-presupuesto`.
- **Portal:** `frontend/index.html` (estático, datos del panel) y `frontend/mapa/mapa.html` (mapa con ORDS).
- **Oracle/APEX:** `oracle/ddl/01..05`; guía en `entrega/CARGA_ORACLE.md`.
- **Dataset:** `entrega/dataset/municipios_panel_validado.csv` (+ JSON) con diccionario y checksums.

---

## 9. Próximos pasos (roadmap)

1. Conectar **SERMAS** (médicos), **Consejería de Educación** (plazas/alumnado), **Catastro**
   (vivienda/suelo), **CRTM** (transporte) y **Notariado** (precios).
2. Ampliar de 20 a los **155 municipios <50k**, con muestra estratificada por tamaño.
3. Montar las **3 páginas APEX** (dashboard+mapa, explorador, ficha+simulador) y las 9 del diseño
   original como evolución.
4. Modelo de **spillover** intermunicipal (matriz OD) para medir el efecto en pueblos vecinos.
5. Validación temporal cuando exista serie histórica.

---

## 10. Glosario

- **ICA:** índice de capacidad de acogida (0–100).
- **Cuello de botella:** servicio que se satura primero.
- **No compensatorio:** un servicio colapsado no se compensa con otros factores.
- **OOF:** predicción sobre municipios no vistos en entrenamiento.
- **GroupKFold por comarca:** entrenar con unas comarcas y evaluar con otras.
- **Banda del 95 %:** horquilla de incertidumbre del modelo.
- **Calibración:** valor estimado para representar una variable no disponible.
- **What-if:** simulación de una inversión o llegada de población.
- **M4-OPT:** heurística voraz de reparto presupuestario comarcal.
- **Procedencia:** origen y método de cada variable (`OBSERVADO`, `SIMULADO`, etc.).

---

## 11. Contacto y atribución

> Equipo LoDCORE Madrid (2026). *Panel Municipal Integrado LoDCORE Madrid, v1.0.0-F2*.
> II Datathon LoDCOREMadrid. Población: INE (Padrón 2025, tabla 2881). Centros: Comunidad de
> Madrid, Datos Abiertos (CC BY 4.0). El resto de variables son estimaciones declaradas.
