-- =============================================================================
-- LoDCORE Madrid • 04-indices_espaciales.sql
-- Geometría SDO_GEOMETRY en ETRS89 (SRID 25830) para Oracle Spatial / APEX Map
-- =============================================================================

ALTER TABLE municipios_procesados ADD (
    geometria SDO_GEOMETRY
);

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

CREATE INDEX idx_municipios_sdo ON municipios_procesados(geometria)
INDEXTYPE IS MDSYS.SPATIAL_INDEX_V2;
