-- =============================================================================
-- LoDCORE Madrid • 04-indices_espaciales.sql
-- Geometría SDO_GEOMETRY en ETRS89 (SRID 25830) para Oracle Spatial / APEX Map
-- Script idempotente: se puede reejecutar sin ORA-01430 / ORA-00001.
-- =============================================================================

-- 1. Añadir la columna solo si no existe (ORA-01430 = column already exists)
BEGIN
    EXECUTE IMMEDIATE 'ALTER TABLE municipios_procesados ADD (geometria SDO_GEOMETRY)';
EXCEPTION
    WHEN OTHERS THEN
        IF SQLCODE != -1430 THEN
            RAISE;
        END IF;
END;
/

-- 2. Refrescar los metadatos espaciales (clave table_name + column_name)
DELETE FROM user_sdo_geom_metadata
 WHERE table_name = 'MUNICIPIOS_PROCESADOS'
   AND column_name = 'GEOMETRIA';

INSERT INTO user_sdo_geom_metadata (
    table_name, column_name, diminfo, srid
) VALUES (
    'MUNICIPIOS_PROCESADOS',
    'GEOMETRIA',
    SDO_DIM_ARRAY(
        SDO_DIM_ELEMENT('X', 300000, 600000, 0.05),
        SDO_DIM_ELEMENT('Y', 4400000, 4600000, 0.05)
    ),
    25830 -- ETRS89 / UTM zone 30N
);
COMMIT;

-- 3. Recrear el índice espacial sin fallar si ya existe
BEGIN
    EXECUTE IMMEDIATE 'DROP INDEX idx_municipios_sdo';
EXCEPTION
    WHEN OTHERS THEN
        IF SQLCODE != -1418 THEN -- ORA-01418: specified index does not exist
            RAISE;
        END IF;
END;
/

CREATE INDEX idx_municipios_sdo ON municipios_procesados(geometria)
INDEXTYPE IS MDSYS.SPATIAL_INDEX_V2;
