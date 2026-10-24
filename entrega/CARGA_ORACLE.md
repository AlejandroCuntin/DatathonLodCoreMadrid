# Carga del Dataset en Oracle Database 23ai / Oracle APEX

> Esta guía carga el panel validado en la tabla `municipios_procesados` y deja el mapa y las
> vistas listos para APEX. Está pensada para el entorno del Datathon (Oracle Cloud / APEX).

## 1. Orden de ejecución del DDL

Ejecutar en SQLcl, SQL Developer o APEX › SQL Workshop, **en este orden**:

1. `oracle/ddl/01-tablas_raw.sql`
2. `oracle/ddl/02-tablas_procesadas.sql` (crea `municipios_procesados` con las 88 columnas canónicas y columnas virtuales de compatibilidad)
3. `oracle/ddl/03-vistas_apex.sql`
4. `oracle/ddl/04-indices_espaciales.sql`
5. `oracle/ddl/05-modelos_onnx.sql`

> 💡 **Nota sobre `06-dataset_completo_APEX.sql`**: Si ya ejecutó `02-tablas_procesadas.sql`, no es necesario ejecutar el `06`. Este último incluye `DROP TABLE ... CASCADE` para recrear limpiamente la estructura completa en entornos aislados si fuera necesario.

## 2. Cargar el CSV

`dataset/municipios_panel_validado.csv` → tabla **`municipios_procesados`**.

Al importar (SQL Developer › *Import Data* o APEX › *Data Workshop › Load Data*), la correspondencia es **directa 1:1 por nombre de columna**:
- Las 88 columnas del CSV se cargan directamente sin necesidad de renombrado manual.
- Las columnas virtuales de compatibilidad (`tiempo_madrid_min`, `plazas_escolares`, `alumnos_matriculados`, `precio_avm_m2`) se calculan automáticamente en base de datos.
- Son columnas obligatorias auditadas: `fecha_disponible`, `origen`, `metodo`, `dataset_version` y `fuente_datos`.

## 3. Modelos para el scoring dentro de Oracle (N2)

1. Copiar `oracle/onnx/*.onnx` al servidor de base de datos.
2. Crear el objeto de directorio (si no existe):

```sql
CREATE OR REPLACE DIRECTORY LODCORE_ONNX_DIR AS '/opt/lodcore/onnx';
-- Otorgar READ al usuario LODCORE si el directorio lo crea otro usuario.
```

3. Ejecutar `oracle/ddl/05-modelos_onnx.sql` (carga `m1_avm` y `m4_capacidad` con
   `DBMS_VECTOR.LOAD_ONNX_MODEL` y crea la vista de scoring `v_onnx_scoring_n2`).

## 4. Mapa interactivo y API REST

El frontend (`frontend/mapa/`) consume un endpoint ORDS. Los scripts están en:

- `oracle/REST/mapa-Vista-datos.sql`
- `oracle/REST/mapa-Servicio-REST.sql`

El endpoint configurado en el frontend es:

```
https://<host>/ords/datathon/lodcore/municipios
```

Si cambia el host o el esquema, actualizar `apiUrl` en `frontend/mapa/lodcore-mapa.js`.

## 5. Comprobación rápida tras la carga

```sql
-- 1) Deben salir 20 filas
SELECT COUNT(*) FROM municipios_procesados;

-- 2) Población total: 200.267
SELECT SUM(poblacion_actual) FROM municipios_procesados;

-- 3) Semáforo: 2 ALTA, 6 MEDIA, 12 BAJA
SELECT nivel_idoneidad, COUNT(*) FROM municipios_procesados GROUP BY nivel_idoneidad;

-- 4) La regla dura debe dar 0 filas (ningún colapso con ICA >= 40)
SELECT COUNT(*) FROM municipios_procesados
WHERE (hab_por_medico > 1500 OR ocupacion_escolar_pct > 95)
  AND indice_capacidad_global >= 40;

-- 5) Procedencia obligatoria, sin nulos
SELECT COUNT(*) FROM municipios_procesados
WHERE origen IS NULL OR metodo IS NULL OR dataset_version IS NULL
   OR fuente_datos IS NULL OR fecha_disponible IS NULL;
```

## 6. Si algo no cuadra

- **Acentos raros:** el CSV debe cargarse como UTF-8.
- **Fechas:** `fecha_disponible` y `fecha_carga` son `YYYY-MM-DD`; `fecha_calculo` es
  `YYYY-MM-DDTHH:MM:SS`.
- **Los números no coinciden con la ficha:** comprobar que se está usando
  `dataset/municipios_panel_validado.csv` (v1.0.0-F2) y no una copia antigua.
