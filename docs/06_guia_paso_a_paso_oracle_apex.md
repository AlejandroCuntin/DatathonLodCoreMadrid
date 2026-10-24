# GUÍA PASO A PASO: PUESTA EN MARCHA EN ORACLE Y ORACLE APEX
**II Datathon LoDCOREMadrid 2026**

> ⚠️ **AVISO (octubre 2026)**: esta guía describe el prototipo antiguo de 5 tablas
> (`MUNICIPIOS`, `DOTACION_SERVICIOS`, `VIVIENDA_Y_SUELO`, `INDICES_CAPACIDAD`,
> `PARAMETROS_MODELO`). El esquema vigente es `oracle/ddl/01-tablas_raw.sql` …
> `06-dataset_completo_APEX.sql` (el 06 está **en revisión**: duplica una tabla
> del 02; no ejecutarlo hasta validar). El orden de carga está en el `README.md` §3.
> **No ejecutes** el script de ~35 sentencias que menciona esta guía: ya no existe
> en el repositorio.

Esta guía explica con capturas textuales y paso a paso cómo cargar el modelo de datos del reto y ver los mapas y tablas funcionando en **Oracle APEX** en menos de 10 minutos.

---

## OPCIÓN RECOMENDADA: ORACLE APEX EN LA NUBE (Sin instalar nada en local)

Oracle APEX funciona 100% en el navegador web sobre una base de datos Oracle gestionada.

Tienes dos opciones de acceso gratuito:
1. **Cuenta del Datathon (Oracle Academy / Cloud):** La que Óscar Sánchez y la organización facilitan a los equipos inscritos (con los créditos OCI).
2. **Entorno Gratuito Inmediato de Pruebas (apex.oracle.com):** Si aún no tienes las claves del equipo, puedes solicitar un Workspace gratuito en 1 minuto en:
   👉 **[https://apex.oracle.com/pls/apex/f?p=4550](https://apex.oracle.com/pls/apex/f?p=4550)** (Pulsar en *"Request a Free Workspace"*).

---

## PASO 1: Iniciar Sesión en Oracle APEX
1. Abre tu navegador y accede a tu URL de Oracle APEX (o a `https://apex.oracle.com`).
2. Introduce:
   - **Workspace:** El nombre de tu espacio de trabajo.
   - **Username:** Tu usuario (o correo).
   - **Password:** Tu contraseña.
3. Llegarás a la pantalla principal con 4 grandes iconos:
   - **App Builder** (Creador de aplicaciones web).
   - **SQL Workshop** (Gestor de la base de datos Oracle).
   - **Team Development** (Gestión ágil).
   - **App Gallery** (Galería de ejemplos).

---

## PASO 2: Cargar el Esquema y los Datos en la Base de Datos

Vamos a ejecutar los 3 ficheros SQL que ya tenemos listos en tu carpeta `DATATHON/sql/`:

1. Haz clic en el menú **SQL Workshop** ➔ selecciona **SQL Scripts**.
2. Pulsa el botón **Upload** (Subir) situado arriba a la derecha.

### Subir y ejecutar en este orden exacto:

#### A) Script 1: Estructura de Tablas
- Pulsa **Choose File** y selecciona:
  `C:\Users\USUARIO\Desktop\DATATHON\sql\01_ddl_schema.sql`
- Script Name: `01_ddl_schema.sql`
- File Character Set: `Unicode (UTF-8)`
- Pulsa **Upload**.
- Una vez subido, en la lista de scripts haz clic en el icono de **Run** (el triángulo o botón "Run").
- Confirma pulsando **Run Now**.
- Verás el resumen: `Statements Processed: ~35`, sin errores. Se habrán creado las tablas `MUNICIPIOS`, `DOTACION_SERVICIOS`, `VIVIENDA_Y_SUELO`, `INDICES_CAPACIDAD` y `PARAMETROS_MODELO`.

#### B) Script 2: Carga de Datos Calculados del ICA
- Vuelve a pulsar **Upload**.
- Selecciona el archivo:
  `C:\Users\USUARIO\Desktop\DATATHON\sql\02_dml_inserts.sql`
- Script Name: `02_dml_inserts.sql`
- Pulsa **Upload** y luego **Run** ➔ **Run Now**.
- Se insertarán los 20 municipios analizados con todas sus métricas calculadas.

#### C) Script 3: Vistas Analíticas para el Mapa y Reportes
- Vuelve a pulsar **Upload**.
- Selecciona el archivo:
  `C:\Users\USUARIO\Desktop\DATATHON\sql\03_views_and_apex_queries.sql`
- Script Name: `03_views_and_apex_queries.sql`
- Pulsa **Upload** y luego **Run** ➔ **Run Now**.
- Creará la vista desnormalizada `V_MUNICIPIOS_ICA_APEX` con los colores de pines, iconos y métricas de APEX.

---

## PASO 3: Verificar los Datos con tus Propios Ojos

1. En el menú superior, ve a **SQL Workshop** ➔ **Object Browser**.
2. En la columna de la izquierda verás la lista de **Tables**:
   - Haz clic en `MUNICIPIOS` y luego en la pestaña **Data**: verás los 20 municipios con su población INE 2025, superficie, latitud y longitud.
   - Haz clic en `INDICES_CAPACIDAD` ➔ pestaña **Data**: verás los scores 0-100, la columna `NIVEL_IDONEIDAD` (*ALTA, MEDIA, BAJA*) y los cuellos de botella calculados.
   - En el selector de objetos cambia de *Tables* a **Views** y haz clic en `V_MUNICIPIOS_ICA_APEX`: verás la tabla completa combinada con los códigos de color hexadecimales (`#2ecc71`, etc.).

---

## PASO 4: Crear la Aplicación con Mapa Interactivo (en 2 minutos)

1. En el menú superior de APEX, haz clic en **App Builder**.
2. Pulsa en **Create a New App** ➔ selecciona **New Application**.
3. **Name:** `Observatorio ICA Madrid`.
4. En la sección **Pages** (Páginas):
   - Por defecto tendrás la página *Home*.
   - Pulsa **Add Page** (Añadir Página):
     - Selecciona **Map** (Mapa).
     - Page Name: `Mapa de Capacidad Territorial`.
     - Table / View Name: Escribe o selecciona `V_MUNICIPIOS_ICA_APEX`.
     - Geolocation Type: `Points (Longitude / Latitude)`.
     - Longitude Column: `LONGITUD`.
     - Latitude Column: `LATITUD`.
     - Tooltip / Title Column: `NOMBRE`.
     - Pulsa **Add Page**.
   - Vuelve a pulsar **Add Page**:
     - Selecciona **Interactive Report**.
     - Page Name: `Diagnóstico y Cuellos de Botella`.
     - Table / View Name: `V_MUNICIPIOS_ICA_APEX`.
     - Pulsa **Add Page**.
5. Al final de la página de creación, pulsa el botón verde **Create Application**.

---

## PASO 5: Ejecutar la Aplicación y Ver el Resultado
1. Pulsa el botón **Run Application** (el icono de Play arriba a la derecha).
2. Se abrirá una pestaña en el navegador con la aplicación web corporativa.
3. Inicia sesión con tus credenciales de APEX.
4. Navega a la página **Mapa**: verás el mapa de la Comunidad de Madrid con los 20 municipios marcados sobre el territorio.
5. Navega a **Diagnóstico**: tendrás una tabla interactiva profesional con filtros automáticos, búsqueda instantánea y botón de descarga a Excel o PDF.
