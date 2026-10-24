# Guía Paso a Paso: Despliegue en Oracle Database 23ai y Oracle APEX (Fase P3)
## II Datathon LoDCORE Madrid · UC3M + Comunidad de Madrid (Octubre 2026)

> **Entregable F12 (APEX)**: Configuración guiada para desplegar las **3 páginas canónicas del MVP** sobre el panel validado de los 20 municipios piloto, con linaje de procedencia auditado (`origen`, `metodo`, `dataset_version`, `fuente_datos`) y reglas duras no compensatorias.

---

### Paso 1: Carga del Esquema DDL en Oracle Database 23ai

En el entorno de Oracle Cloud (Autonomous Database) o en **SQL Workshop › SQL Scripts** de Oracle APEX, ejecutar los siguientes ficheros en orden estricto:

1. `oracle/ddl/01-tablas_raw.sql`: Estructura para almacenamiento de snapshots crudos inmutables.
2. `oracle/ddl/02-tablas_procesadas.sql`: Tabla unificada `municipios_procesados` con las 88 columnas canónicas del panel validado y columnas virtuales de compatibilidad.
3. `oracle/ddl/03-vistas_apex.sql`: Vistas oficiales con trazabilidad obligatoria y salvaguardas no compensatorias:
   - `v_apex_portal_ciudadano`: Datos desnormalizados por municipio con `indice_ica_ajustado` (techo 39 ptos si hay saturación) y procedencia.
   - `v_apex_panel_institucional`: Agregación comarcal para el Dashboard directivo (8 comarcas, población total, alertas sanitarias y educativas).
4. `oracle/ddl/04-indices_espaciales.sql`: Columna `geometria SDO_GEOMETRY` e índice espacial R-Tree `idx_municipios_sdo` (SRID 25830 / ETRS89).
5. `oracle/ddl/05-modelos_onnx.sql`: Carga de modelos ONNX (`m1_avm.onnx` y `m4_capacidad.onnx`) con `DBMS_VECTOR.LOAD_ONNX_MODEL` y vista de scoring `v_onnx_scoring_n2`.

*(Nota: Si se precisa un refresco limpio desde cero en APEX, `oracle/ddl/06-dataset_completo_APEX.sql` ejecuta un `DROP TABLE ... CASCADE` previo).*

---

### Paso 2: Carga del Panel Municipal Validado

1. En Oracle APEX, acceder a **SQL Workshop › Utilities › Data Workshop › Load Data**.
2. Seleccionar el archivo oficial de entrega:
   `entrega/dataset/municipios_panel_validado.csv` (o `data/validated/municipios_panel_validado.csv`).
3. Indicar como tabla de destino: **`MUNICIPIOS_PROCESADOS`**.
4. **Mapeo directo 1:1**: Las 88 columnas coinciden exactamente por nombre.
   - Las columnas virtuales (`tiempo_madrid_min`, `plazas_escolares`, `alumnos_matriculados`, `precio_avm_m2`) son calculadas automáticamente por el motor de base de datos.
5. Confirmar la carga: deben insertarse exactamente **20 filas** (200.267 habitantes agregados).

---

### Paso 3: Las 3 Páginas Clave en Oracle APEX (F12.1)

En **App Builder › Create Application**, nombrar la aplicación como `Observatorio LoDCORE Madrid` (Theme 42: *Universal Theme - Redwood Light*).

#### Página 1: Dashboard Comarcal Institucional
- **Fuente de datos**: `v_apex_panel_institucional`.
- **Componentes**:
  - **KPI Badge List (Cabecera)**:
    - *Municipios Analizados*: `20`
    - *Población Total Acogida*: `200.267 hab.`
    - *Capacidad Neta Inmediata*: `5.078 hab.` (sin colapso de ningún servicio)
    - *Inversión Requerida en Alertas*: `35,9 M€`
  - **Cards / Interactive Grid Comarcal**: 8 comarcas con desglose de ICA promedio, alertas sanitarias (`SUM(alerta_sanitaria)`) y educativas (`SUM(alerta_educativa)`).
  - **Trazabilidad Visible**: Cada tarjeta muestra `dataset_version: v1.0.0-F2` y `fuente_datos`.

#### Página 2: Mapa Semafórico Territorial
- **Opción A (Nativa APEX Map Region)**:
  - Crear región de tipo **Map**.
  - Capa de Puntos sobre `V_MAPA_MUNICIPIOS` (o `v_apex_portal_ciudadano`).
  - Coordenadas: Longitud `LONGITUD`, Latitud `LATITUD`.
  - Color de Marcador dinámico:
    - Verde (`#16a34a`): `ALTA` (ICA $\ge 60$)
    - Ámbar (`#d97706`): `MEDIA` ($40 \le \text{ICA} < 60$)
    - Rojo (`#dc2626`): `BAJA` ($\text{ICA} < 40$ o colapso no compensatorio)
  - Tooltip: Nombre, Comarca, Población, Factor Limitante dominante y Capacidad Neta.
- **Opción B (Región HTML/JS Avanzada)**:
  - Incrustar la región estática Leaflet de `frontend/mapa/lodcore-mapa-region.html`.
  - Cargar `frontend/mapa/lodcore-mapa.css` y `frontend/mapa/lodcore-mapa.js`, que consume el endpoint ORDS `oracle/REST/mapa-Servicio-REST.sql`.

#### Página 3: Ficha Municipal y Simulador de Escenarios What-If
- **Fuente de datos**: Formulario / Ficha sobre `v_apex_portal_ciudadano`.
- **Expediente del Municipio**:
  - Indicadores clave: Habitantes por médico (alerta si $>1.500$), Ocupación escolar (alerta si $>95\%$), Precio m² y vivienda vacante.
  - Dictamen en lenguaje natural sin causalidad (según reglas F11 de `redaccion_natural.py`).
- **Simulador What-If Interactivo**:
  - Control de entrada: Deslizador de nuevos residentes proyectados (`+100` a `+2.000` personas).
  - Cálculo reactivo (vía llamada REST a `/whatif` de FastAPI o cálculo PL/SQL local):
    - Médicos de Atención Primaria adicionales requeridos para no colapsar.
    - Aulas / plazas escolares necesarias.
    - Presupuesto de inversión CAPEX estimado.
    - Nuevo semáforo resultante aplicando la salvaguarda no compensatoria.

---

### Paso 4: Verificación de Calidad y Cierre de Entrega

Ejecutar las consultas de verificación en SQL Workshop:

```sql
-- 1. Total exacto de 20 municipios
SELECT COUNT(*) AS total_filas FROM municipios_procesados; -- Esperado: 20

-- 2. Integridad de la regla dura: 0 municipios saturados con ICA >= 40
SELECT COUNT(*) FROM municipios_procesados
WHERE (hab_por_medico > 1500 OR ocupacion_escolar_pct > 95.0)
  AND indice_capacidad_global >= 40.0; -- Esperado: 0

-- 3. Trazabilidad completa por registro (0 nulos en metadatos)
SELECT COUNT(*) FROM municipios_procesados
WHERE origen IS NULL OR metodo IS NULL OR dataset_version IS NULL OR fuente_datos IS NULL; -- Esperado: 0
```
