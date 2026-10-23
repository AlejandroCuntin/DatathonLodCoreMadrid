---
description: 'Construye el Modelo 2: sub-índices de capacidad 0-100 con PCA + MinMaxScaler e isócronas de accesibilidad sobre OSM y GTFS'
agent: 'agent'
tools: ['search/codebase', 'edit/editFiles', 'runCommands']
argument-hint: '[foco=isocronas|pca|ambos]'
---

# Modelo 2 — Indicadores Territoriales, PCA e Isócronas

## Misión

Implementar el **Módulo de Indicadores de Capacidad e Infraestructura**:

1. Calcular **isócronas de accesibilidad** (Dijkstra / A\*) sobre **OpenStreetMap + GTFS**
   (CRTM, Cercanías, Renfe interurbanos), con el criterio de **"municipio de 30 minutos"** en
   transporte público **vs. privado** hacia polos de empleo y hospitales de referencia.
2. Condensar decenas de variables correlacionadas en **4 sub-índices 0-100** con
   **PCA + MinMaxScaler**, sin multicolinealidad.

## Alcance y precondiciones

- Precondición: dataset municipal con variables de los 7 bloques; feeds GTFS descargados.
- Alcance: `src/lodcore/models/m2_indices/`.
- El grafo de OSM es **pesado**: cachea en disco (`data/cache/osmnx/`) y nunca lo recalcules en cada run.

## Inputs

- `${input:foco}` — `isocronas` | `pca` | `ambos` (por defecto `ambos`).

## Workflow

### Parte 1 — Isócronas de accesibilidad

**Red viaria (OSMnx)**
- `ox.graph_from_place` o `ox.graph_from_polygon` con el polígono del municipio (fuente: IGN/CNIG).
  **Cachea siempre**: `ox.save_graphml` / `ox.load_graphml`.
- `network_type='drive'` para el modo privado; `network_type='walk'` para el primer y último
  tramo a pie hacia la parada.
- **Imputa velocidades** si faltan (`ox.add_edge_speeds` + `ox.add_edge_travel_times`).
- Simplifica con `consolidate_intersections` para acelerar el routing.

**Red de transporte público (GTFS)**
- Parsea `stops.txt`, `routes.txt`, `trips.txt`, `stop_times.txt`, `calendar.txt`,
  `calendar_dates.txt` del GTFS de CRTM (y Renfe Cercanías si hay feed).
- **Identifica las paradas dentro del municipio** y, para cada una, calcula:
  - tiempo a pie desde el centroide (o desde el casco urbano: usa el centroide **ponderado por
    población**, no el geométrico) → `t_walk_origen`;
  - tiempos de viaje hacia los **polos de destino** (empleo: Madrid centro, Alcalá, Getafe,
    Henares; hospitales de referencia: Hospital de La Paz, Ramón y Cajal, etc.).
- **Transferencias**: máximo 1 transbordo (criterio explícito del proyecto: no se asume
  unlimited transfers).
- **Modo**: en hora punta (día laborable, 08:00) **y** en valle (14:00). Reporta ambos; el
  indicador de conectividad usa la **media de los dos modos** y la **peor** como indicador de riesgo.
- **Criterio de 30 minutos**: porcentaje de la población del municipio que alcanza cada polo
  dentro de 30 min (público) y en privado. Este es el **gap de accesibilidad**, una de las
  "brechas marcadas" que el documento de diseño menciona para municipios < 20.000 habitantes.

**Implementación**
- Routing multimodal: `r5py` (OpenTripPlanner, ideal para GTFS+OSM) o `networkx` +
 raphael. Si usas `networkx`: Dijkstra para privado, y un grafo temporal propio para GTFS.
- **Herencia**: `dijkstra` sobre grafo estático; `A*` con heurística de distancia geodésica
  cuando el destino es un polo de empleo concreto (más rápido en grafos grandes).
- Test de paridad: verifica que para al menos 5 trayectos el resultado A\* coincide con
  Dijkstra (mismo coste, Within tolerance).

**Salida de esta parte** (variables del panel, por municipio × año):
- `pct_pob_acc_30min_publico_empleo`, `pct_pob_acc_30min_privado_empleo`,
  `pct_pob_acc_30min_publico_hospital`, `min_transito_empleo_publico`,
  `n_transbordos_medio`, `gap_accesibilidad_30min` (privado − público).

### Parte 2 — PCA y sub-índices 0-100

**Variables de entrada** (según bloque):
- *Capacidad Sanitaria/Educativa*: hab/médico, hab/enfermera, plazas de colegio por aula,
  % ocupación aulas, nº centros de salud, % población > 65 años, plazas deczyńcare.
- *Conectividad y Movilidad*: las isócronas anteriores, densidad de red viaria, % población
  con coche, nº de paradas de autobús, frecuencia del servicio.
- *Sostenibilidad Ambiental*: residuos per cápita, m² de zona verde per cápita, calidad del aire
  (PM2.5), % superficie protegida, riesgo de incendio, consumo hídrico.
- *Músculo Presupuestario/Inversor*: presupuesto municipal per cápita, inversión per cápita,
  deuda municipal,Eggreve_ratio ingresos propios / gasto, % gasto en inversión.

**Procedimiento**
1. **Transformación de orientación**: todas las variables son "más es mejor" (higher-is-better).
   Invierte las que no lo son (más médicos = mejor) **explícitamente** y documenta cuáles.
2. **Imputación**: median imputer **dentro del pipeline**; las imputaciones quedan marcadas como
   `IMPUTADO` en la procedencia.
3. **Normalización MinMaxScaler** a [0,1] y luego a **0-100**. MinMax **es sensible a outliers**:
   reporta si has winorizado (percentiles 5-95) y con qué criterio.
4. **PCA** sobre la matriz estandarizada:
   - ¿Cuántas componentes retienen > 80 % de la varianza? Ese es el nº de sub-índices a usar.
   - Reporta **loadings** para que cada componente sea interpretable.
   - **Trampa a evitar**: PCA con n=41 y muchas variables produce componentes **difíciles de
     nombrar**. Si una componente no tiene un nombre claro y accionable, **no la uses como
     sub-índice**: vuelve a agrupar variables por bloque conceptual y aplica PCA **dentro** de
     cada bloque.
5. **Orientación de las componentes**: el signo de una componente PCA es arbitrario. Fíjalo con
   un criterio explícito (ej. "la componente con mayor carga positiva en `hab_por_medico` va
     en positivo") y **persiste esa convención** en el artefacto del modelo, porque el signo
     cambia entre ejecuciones y rompería la APP.
6. **Redondeo**: los sub-índices se publican como enteros 0-100. Declara que el redondeo es
   de presentación y que internamente se usa el valor continuo.

**Alternativa metodológica a considerar (recomendada comparar)**
El **Manual OECD/JRC de Indicadores Compuestos** (2008) recomienda, para n pequeño,
**Mazziotta-Pareto Index** (AMPI) en lugar de PCA, porque el AMPI es **robusto ante la
normalización MinMax** y **no exige que las componentes sean interpretables**. Compara PCA vs AMPI
y elige con argumentos (sensibilidad a outliers, estabilidad de los pesos).

### Parte 3 — Validación
- ¿Los sub-índices son **estables**? Bootstrap por municipio: ¿los pesos de las componentes y el
  ranking de sub-índices se mantienen? Reporta la **inestabilidad** (índice de rotación).
- ¿Los sub-índices correlacionan con resultados externos plausibles? Ej.: `hab_por_medico` debe
  correlacionar negativamente con la mortalidad o el tiempo de espera hospitalaria si hay dato.
- Correlación de Pearson y Spearman entre sub-índices: detecta multicolinealidad residual.

## Output Expectations

1. `src/lodcore/models/m2_indices/isocrones.py`, `pca_indices.py`, `evaluate.py`.
2. `reports/m2_indices.md`:
```
# M2 — Indicadores
## Isócronas: <n> municipios | GTFS <fecha> | OSM Overpass <fecha>
| municipio | %pob 30min público empleo | %pob 30min privado | gap | transbordos | estado |
## PCA: <n> variables → <k> componentes | varianza explicada acumulada <x>%
### Componentes y loadings (top-5 por componente) y nombre asignado a cada una
## Alternativa AMPI: <comparativa>
## Sub-índices resultantes (muestra de 5 municipios)
## Estabilidad (bootstrap por municipio): <inestabilidad>
## Correlación entre sub-índices (matriz)
## Variables descartadas y por qué
```
3. `model_card.md` de M2, incluyendo la **fecha del snapshot GTFS/OSM** y la convención de signos PCA.

## Quality Assurance

- [ ] El grafo OSM y el GTFS están **cacheados**; no se re-descargan en cada ejecución.
- [ ] Se ha calculado el escenario punta **y** valle; el indicador usa la media y reporta la peor.
- [ ] Los transbordos están limitados a 1 y documentado.
- [ ] El centroide usado para el acceso a pie es el **ponderado por población**.
- [ ] La convención de signos de PCA está fijada y persistida en el artefacto.
- [ ] He comparado PCA vs AMPI y justificado la elección.
- [ ] Las variables imputadas quedan marcadas como `IMPUTADO`.
- [ ] He verificado la paridad A\* vs Dijkstra en al menos 5 trayectos.
