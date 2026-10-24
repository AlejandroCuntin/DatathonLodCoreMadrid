# ESPECIFICACIÓN TÉCNICA DE INTERFAZ Y DEMO EN ORACLE APEX
**II DATATHON LODCOREMADRID · COMUNIDAD DE MADRID / UC3M**
*Proyecto: Herramienta de Diagnóstico del Índice de Capacidad de Acogida (ICA)*

---

## 1. ARQUITECTURA DE LA APLICACIÓN APEX
- **Tema:** Universal Theme (Theme 42) con estilo *Vita - Slate* o *Redwood Light*.
- **Estructura de Navegación:** Menú lateral replegable (Side Navigation Menu).
- **Control de Filtros Global:** Página 0 (Global Page) o Regiones de Filtro fijadas en cabecera/lateral.

---

## 2. MAPA DE PÁGINAS Y DISTRIBUCIÓN DE COMPONENTES

### PÁGINA 1: DASHBOARD EJECUTIVO & MAPA TERRITORIAL (Página de Inicio / Landing)
Diseñada para causar el **primer impacto visual** ante el tribunal evaluador.

- **Región 1 (Breadcrumb / Header):**
  - Título: *Observatorio de Capacidad de Acogida Territorial (CAM)*.
  - Subtítulo: *Evaluación de Holgura de Servicios en Municipios < 50.000 habitantes*.
- **Región 2 (Top Cards / Badge List - 4 Columnas):**
  - KPI 1: Municipios evaluados (`20` en piloto, extensible a 160+).
  - KPI 2: ICA Medio Regional (`37.9 / 100`).
  - KPI 3: Capacidad de Acogida Inmediata sin Colapso (`5.078 hab.`).
  - KPI 4: Inversión Estimada en Refuerzo de Servicios (`35.9 M€`).
- **Región 3 (Panel de Filtros Dinámicos - Collapsible Region a la Izquierda / Col 3):**
  - `P1_COMARCA`: Select List dinámica (`SELECT DISTINCT comarca d, comarca r FROM municipios`).
  - `P1_NIVEL_IDONEIDAD`: Radio Group Pill (`ALTA`, `MEDIA`, `BAJA`, `TODOS`).
  - `P1_POB_MAX`: Slider o Number Field (0 a 50.000).
  - `P1_PRECIO_MAX`: Slider de precio €/m² compra.
- **Región 4 (Centro-Derecha / Col 9 - Oracle APEX Map Component):**
  - **Tipo:** Map Region.
  - **Capa:** Puntos basados en Latitud/Longitud (`EPSG:4326`).
  - **Simbología:** Marcadores circulares con icono SVG, coloreados dinámicamente según `PIN_COLOR_HEX` (Verde: ALTA, Ámbar: MEDIA, Rojo: BAJA).
  - **Tooltip / Popup:** Ficha HTML con ranking, ICA, población, capacidad sin colapso y botón directo para abrir la Ficha de Detalle.
- **Región 5 (Inferior / Col 12 - Top 5 Municipios con Mayor Capacidad):**
  - Componente **Cards** con badges de color indicando el factor limitante y la acogida neta.

---

### PÁGINA 2: EXPLORADOR ANALÍTICO MULTIDIMENSIONAL (Interactive Report / Grid)
Permite a los analistas de políticas públicas profundizar y cruzar variables.

- **Región de Filtros Avanzados Facetados (Faceted Search):**
  - Filtro por Comarca, Tipología (Rural / Semiurbano / Urbano), Rango de Precios, Factor Limitante (Sanidad vs Educación vs Vivienda).
- **Interactive Report (o Interactive Grid editable para simulaciones):**
  - Columnas coloreadas con Highlighting semafórico según el valor del ICA.
  - Desglose de costes de ampliación e indicadores per cápita (médicos/1.000 hab, plazas escolares, fibra óptica).
  - Botón de exportación nativo a **Excel, PDF y CSV** para justificación administrativa.

---

### PÁGINA 3: FICHA MUNICIPAL Y SIMULADOR DE ESCENARIOS (Modal Page o Ficha Completa)
Al hacer clic en un municipio desde el Mapa o el Reporte, se abre su expediente individual.

- **Cabecera:** Nombre oficial, Escudo/Fotografía representativa, Código INE y Comarca.
- **Gráfico Radar / Polar:** 5 ejes (Sanidad, Educación, Conectividad, Vivienda, Holgura).
- **Diagnóstico de Saturación:**
  - Barra de progreso interactiva: Población actual vs Capacidad límite sanitaria vs Capacidad escolar.
  - Indicador de alerta roja en el factor que actúa como **cuello de botella**.
- **Calculadora / Simulador "What-If" (invoca a los endpoints FastAPI `/whatif` y `/optimizar-presupuesto`; PL/SQL opcional para validaciones en BD):**
  - Selector de nuevos residentes proyectados (ej. `+500 personas`).
  - Salida reactiva:
    * ¿Colapsa la atención médica? Sí/No (¿Cuántos médicos de AP hay que contratar?).
    * ¿Colapsa el colegio local? Sí/No (¿Cuántas aulas/plazas escolares se precisan?).
    * Presupuesto público estimado de la actuación de refuerzo.

---

## 3. GUION RECOMENDADO PARA LA DEMO ANTE EL JURADO (15 MINUTOS)

| Minuto | Bloque | Acción en la Pantalla | Mensaje Clave para el Jurado |
|---|---|---|---|
| **00:00 - 02:00** | **Planteamiento del Reto** | Abrir Página 1 (Dashboard). Mostrar KPIs superiores. | *"El reto demográfico de Madrid no es solo despoblación, sino desequilibrio territorial. Con datos abiertos de la CAM e INE, cuantificamos exactamente qué municipios pueden absorber población sin colapsar servicios."* |
| **02:00 - 05:00** | **Solución y Arquitectura** | Mostrar el flujo datos → modelos → Oracle → APEX. | *"Todo el modelo se ejecuta dentro de Oracle para ser rápido y seguro. El panel municipal combina datos oficiales del INE y de la Comunidad de Madrid."* |
| **05:00 - 07:30** | **Diagnóstico Territorial (Mapa)** | Interactuar con el Mapa APEX. Filtrar por `ALTA` idoneidad. Pasar el cursor por *Robledo de Chavela* y *Buitrago*. | *"Aquí vemos el semáforo territorial. No basta con que la vivienda sea asequible: si el consultorio o la escuela están al 100%, la llegada de familias provocará el colapso del servicio."* |
| **07:30 - 10:00** | **Simulador What-If y Ficha** | Abrir la Ficha Municipal de *Chinchón* o *San Martín de Valdeiglesias*. Simular una llegada de +400 hab. | *"Nuestra herramienta no solo diagnostica: presupuesta. Para acoger a 400 nuevos vecinos, el sistema calcula en tiempo real cuántos médicos y plazas escolares se requieren y con qué coste."* |
| **10:00 - 13:00** | **Diferenciador: Optimizador Comarcal** | Llamar a `/optimizar-presupuesto` con 2 M€ en Sierra Oeste y mostrar la asignación. | *"Y si el gestor tiene una partida cerrada, no simulamos a mano: la herramienta asigna el presupuesto entre los municipios de la comarca priorizando cuellos de botella y descartando inversiones ineficientes. El efecto sobre los pueblos vecinos es la siguiente fase."* |
| **13:00 - 15:00** | **Cierre y Escalabilidad** | Mostrar arquitectura (Oracle Database + APEX + Python). Resaltar uso de estándares abiertos. | *"Solución escalable a los ~160 municipios menores de 50.000 habitantes de la CAM, con trazabilidad desde el dato crudo hasta la decisión pública."* |
