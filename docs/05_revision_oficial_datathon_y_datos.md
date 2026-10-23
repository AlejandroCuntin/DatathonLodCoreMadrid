# REVISIÓN INTEGRAL DE BASES, PROGRAMA Y FUENTES DE DATOS OFICIALES
**II DATATHON LODCOREMADRID 2026 · UC3M & COMUNIDAD DE MADRID**
*Evento de Lanzamiento: 14 de Octubre de 2026 · Salón de Grados (Campus de Leganés, UC3M)*  
*Fuente Oficial:* [Programa Datathon LoDCOREMadrid](https://datathon.lodcoremadrid.es/index.php/programa/)

---

## 1. AUDITORÍA DEL PROGRAMA OFICIAL Y PARTICIPANTES INSTITUCIONALES

Tras analizar el programa oficial de la jornada de hoy (14 de octubre de 2026) y las 7 ponencias técnicas de los organismos convocantes, se constata que cada bloque de datos y tecnología de nuestra solución responde con absoluta precisión a las instituciones y directrices presentadas:

```
┌─────────────────────────────────────────────────────────────────────────────────────────────────┐
│                                PROGRAMA OFICIAL DEL DATATHON                                   │
├──────────────────┬──────────────────────────────────────────┬───────────────────────────────────┤
│ Bloque / Horario │ Ponente e Institución                    │ Rol en Nuestra Solución           │
├──────────────────┼──────────────────────────────────────────┼───────────────────────────────────┤
│ 10:00 - 10:15    │ Javier Carazo (Dir. Gral. Reequilibrio)  │ Enfoque: Municipios < 50.000 hab. │
│ 10:30 - 10:45    │ Andrés Araújo (ORACLE)                   │ Backend: Oracle Database + Cloud  │
│ 10:45 - 11:00    │ Javier García Guzmán (Dir. del Reto UC3M)│ Formulación del ICA y Simulador   │
│ 11:20 - 11:35    │ Jordi Vila (Colegio de Notarios)         │ Datos: Precios €/m² compra/alq.   │
│ 11:35 - 11:50    │ Mariano Peñas (INE)                      │ Datos: API Padrón 2025 (Tab. 2881)│
│ 11:50 - 12:05    │ Ana Rosalía Lorenzo (CRTM)               │ Datos: Paradas y tiempo a Madrid  │
│ 12:05 - 12:20    │ José Alfonso Solórzano (Catastro)        │ Datos: Suelo vacante y viviendas  │
│ 12:30 - 13:15    │ Óscar Sánchez (ORACLE)                   │ Frontend: Oracle APEX (Low Code)  │
└──────────────────┴──────────────────────────────────────────┴───────────────────────────────────┘
```

---

## 2. CONFRONTACIÓN CON LAS "IDEAS OFICIALES PARA RESOLVER EL RETO"
*(Extraído textualmente de la diapositiva 3 de la presentación de Javier García Guzmán, Director del Reto)*

El comité organizador sugirió expresamente las siguientes líneas maestras, las cuales **nuestra arquitectura cubre al 100%**:

| Propuesta Oficial de la Organización | Implementación en Nuestra Solución | Estado |
|---|---|:---:|
| *"Una plataforma analítica e interactiva que calcule un índice sintético de capacidad de acogida para cada municipio de <50k habitantes"* | Algoritmo formal del **ICA** (0 a 100) implementado en `etl_pipeline.py` y almacenado en `INDICES_CAPACIDAD.INDICE_CAPACIDAD_GLOBAL`. | ✅ **Implementado** |
| *"Mapa de Holgura y Diagnóstico de Saturación de los Servicios Públicos (Salud, Educación, Servicios Sociales)"* | Componente **Oracle APEX Maps** con pines de color semafórico y tarjetas de holgura desglosando plazas sanitarias y escolares. | ✅ **Implementado** |
| *"Simulador del Umbral Dotacional y Coste de Ampliación"* | Cálculo de nuevos habitantes absorbibles antes del colapso y estimación presupuestaria CAPEX en `INDICES_CAPACIDAD.COSTE_ESTIMADO_AMPLIACION_SERVICIOS`. | ✅ **Implementado** |
| *"Simulador de Refuerzo de Infraestructuras y Costes Asociados"* | Página 3 de APEX: calculadora reactiva *what-if* que proyecta médicos y colegios necesarios al acoger $N$ habitantes adicionales. | ✅ **Implementado** |
| *"Análisis de la movilidad en diversas comarcas"* | Dimensión Conectividad (25% del ICA): paradas interurbanas CRTM y tiempo de viaje a Sol en hora valle. | ✅ **Implementado** |

---

## 3. ALINEACIÓN CON EL BAREMO DE EVALUACIÓN DEL JURADO (100 PUNTOS)
*(Extraído de las Bases Oficiales de la Convocatoria - Diapositiva 12 y documento de Bases)*

El jurado evaluará las propuestas presenciales el **29 de Octubre de 2026** bajo dos grandes bloques de 50 puntos:

### BLOQUE A: CALIDAD DEL RESULTADO (Hasta 50 puntos)
* **1.1. Nivel de corrección y adecuación del planteamiento teórico (25 pts):**
  - *Nuestra defensa:* No usamos números arbitrarios. Normalizamos mediante **Winsorización ($p_5-p_{95}$) + Min-Max**, invertimos variables de coste y aplicamos ratios oficiales de saturación (1.500 tarjetas por médico del SERMAS y 95% de aforo escolar de EduCAM).
* **1.2. Grado de resolución del reto planteado (25 pts):**
  - *Nuestra defensa:* La herramienta no se limita a mostrar "dónde es bonito vivir", sino que determina con rigor matemático **cuál es el cuello de botella** que impide acoger población (Sanidad, Educación o Vivienda) y cuánto cuesta solucionarlo.

### BLOQUE B: EXPLOTABILIDAD Y USABILIDAD (Hasta 50 puntos)
* **2.1. Nivel de sencillez en la obtención y comprensión de resultados (25 pts):**
  - *Nuestra defensa:* El gestor público comprende el estado del municipio en 3 segundos gracias a la semaforización Verde/Ámbar/Rojo, el Top 5 en Cards y el lenguaje claro sin jerga técnica opaca.
* **2.2. Nivel de interactividad y flexibilidad de la solución (25 pts):**
  - *Nuestra defensa:* Oracle APEX ofrece filtrado facetado multidimensional, exportación a Excel/PDF y un simulador *What-If* interactivo donde el alcalde o consejero introduce el número de familias y el sistema recalcula el impacto en vivo.

---

## 4. MAPA DE INTEGRACIÓN DE LOS DATASETS OFICIALES

Con las ponencias oficiales en mano, queda definido el mapa definitivo de datos:

```
                                  [ FUENTES DE DATOS OFICIALES ]
                                                │
         ┌──────────────────────┬───────────────┴───────────────┬──────────────────────┐
         ▼                      ▼                               ▼                      ▼
    [ INE - 2025 ]      [ CRTM - Open Data ]            [ CATASTRO / NOTARIOS ]    [ CAM / SERMAS ]
  (Mariano Peñas)      (Ana Lorenzo Lobo)             (Solórzano / Jordi Vila)   (Datos Abiertos CAM)
         │                      │                               │                      │
   Padrón continuo       Paradas interurbanas            Precios compra/alq.      Centros de salud,
   tabla 2881 (API)      Líneas, tiempo Sol              Stock vivienda vacía,    médicos de familia,
   Municipios <50k       Matriz movilidad                Suelo vacante            colegios y plazas
         │                      │                               │                      │
         └──────────────────────┴───────────────┬───────────────┴──────────────────────┘
                                                │
                                                ▼
                                    [ PIPELINE ETL (Python) ]
                                                │
                                                ▼
                                  [ ORACLE DATABASE & APEX ]
```

1. **INE (Mariano Peñas Pérez):**
   - **Dataset utilizado:** Padrón continuo de habitantes a 1-enero-2025 (ambos sexos, tabla 2881).
   - **Estado:** Conectado mediante la API Tempus3 JSON en tiempo real con *fallback* offline.
2. **Consorcio Regional de Transportes de Madrid (Ana Rosalía Lorenzo Lobo):**
   - **Datasets presentados:** Portal de Datos Abiertos del CRTM (`datos.crtm.es`), catálogo GTFS y geoservicios WFS de paradas y líneas.
   - **Aplicación:** Alimenta la conectividad y accesibilidad metropolitana en `DOTACION_SERVICIOS`.
3. **Colegio de Notarios (Jordi Vila) & Catastro (José Alfonso Solórzano Martín):**
   - **Datasets presentados:** Portal Estadístico Notarial (precios reales de escrituración) y Servicio de Descarga Masiva del Catastro (formato CAT y Shapefiles de parcelas e inmuebles vacantes).
   - **Aplicación:** Alimenta `VIVIENDA_Y_SUELO` (coste del metro cuadrado y capacidad física de edificación).
4. **Oracle (Andrés Araújo y Óscar Sánchez):**
   - **Plataforma:** Oracle Cloud Infrastructure (OCI) y Oracle APEX Application Development, respaldados con créditos y licencias para los equipos del Datathon.

---

## 5. CONCLUSIÓN Y SIGUIENTES PASOS

Nuestra solución no es una propuesta genérica: **está milimétricamente diseñada para encajar en el reto de la Cátedra LoDCOREMadrid, maximizar los 100 puntos de las bases y utilizar exactamente el ecosistema tecnológico recomendado por Oracle y la UC3M**.

Todos los materiales, presentaciones descargadas y volcados de texto están preservados en:
- `data/raw/presentaciones/` (PDFs originales)
- `data/raw/presentaciones/txt/` (Transcripciones completas en texto plano UTF-8)
