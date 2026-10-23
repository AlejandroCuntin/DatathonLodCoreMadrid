-- =============================================================================
-- LoDCORE Madrid • 02-tablas_procesadas.sql
-- Dataset integrado municipal (Fase F2) con procedencia y versionado
-- =============================================================================

CREATE TABLE municipios_procesados (
    id_municipio NUMBER PRIMARY KEY,
    codigo_ine NUMBER(5) UNIQUE NOT NULL,
    nombre VARCHAR2(100) NOT NULL,
    comarca VARCHAR2(80) NOT NULL,
    poblacion_actual NUMBER(7) NOT NULL,
    superficie_km2 NUMBER(8,2) NOT NULL,
    densidad NUMBER(8,2) GENERATED ALWAYS AS (ROUND(poblacion_actual / NULLIF(superficie_km2, 0), 2)) VIRTUAL,
    tiempo_madrid_min NUMBER(4) NOT NULL,
    precio_m2_compra NUMBER(8,2) NOT NULL,
    precio_m2_alquiler NUMBER(6,2),
    
    -- Dotaciones
    num_medicos_ap NUMBER(4) NOT NULL,
    hab_por_medico NUMBER(8,2) GENERATED ALWAYS AS (ROUND(poblacion_actual / NULLIF(num_medicos_ap, 0), 2)) VIRTUAL,
    plazas_escolares NUMBER(6) NOT NULL,
    alumnos_matriculados NUMBER(6) NOT NULL,
    ocupacion_escolar_pct NUMBER(5,2) GENERATED ALWAYS AS (ROUND((alumnos_matriculados / NULLIF(plazas_escolares, 0)) * 100, 2)) VIRTUAL,
    
    -- Sub-índices (0-100)
    score_sanidad NUMBER(5,2) NOT NULL,
    score_educacion NUMBER(5,2) NOT NULL,
    score_conectividad NUMBER(5,2) NOT NULL,
    score_vivienda NUMBER(5,2) NOT NULL,
    
    -- Core Model Outputs
    indice_capacidad_global NUMBER(5,2) NOT NULL,
    personas_acogida_efectiva NUMBER(7) NOT NULL,
    factor_limitante VARCHAR2(30) NOT NULL,
    precio_avm_m2 NUMBER(8,2) NOT NULL,
    gap_mercado_pct NUMBER(6,2) NOT NULL,
    arquetipo_nombre VARCHAR2(80) NOT NULL,
    
    -- Procedencia y Trazabilidad obligatoria
    dataset_version VARCHAR2(20) DEFAULT 'v1.0.0-F2' NOT NULL,
    origen VARCHAR2(100) DEFAULT 'INE+SERMAS+CRTM+CATASTRO' NOT NULL,
    metodo VARCHAR2(100) DEFAULT 'PANEL_INTEGRADO_MINMAX_PCA' NOT NULL,
    fecha_carga TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL
);
