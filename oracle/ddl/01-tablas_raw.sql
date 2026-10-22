-- =============================================================================
-- LoDCORE Madrid • 01-tablas_raw.sql
-- Tablas de almacenamiento crudo inmutable (espejo de data/raw/)
-- =============================================================================

CREATE TABLE raw_ine_padron (
    id_registro NUMBER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    codigo_ine NUMBER(5) NOT NULL,
    nombre_municipio VARCHAR2(100) NOT NULL,
    poblacion_total NUMBER NOT NULL,
    anio_referencia NUMBER(4) NOT NULL,
    origen VARCHAR2(50) DEFAULT 'INE_PADRON_2025' NOT NULL,
    fecha_disponible DATE NOT NULL,
    fecha_carga TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL
);

CREATE TABLE raw_ckan_sanidad (
    id_registro NUMBER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    codigo_ine NUMBER(5) NOT NULL,
    tipo_centro VARCHAR2(50) NOT NULL, -- 'CENTRO_SALUD' | 'CONSULTORIO'
    nombre_centro VARCHAR2(150) NOT NULL,
    num_medicos NUMBER(4) DEFAULT 1 NOT NULL,
    hospital_adscrito VARCHAR2(150),
    origen VARCHAR2(50) DEFAULT 'DATOS_COMUNIDAD_MADRID' NOT NULL,
    fecha_disponible DATE NOT NULL
);

CREATE TABLE raw_ckan_educacion (
    id_registro NUMBER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    codigo_ine NUMBER(5) NOT NULL,
    nombre_centro VARCHAR2(150) NOT NULL,
    plazas_totales NUMBER(5) NOT NULL,
    alumnos_matriculados NUMBER(5) NOT NULL,
    origen VARCHAR2(50) DEFAULT 'DATOS_COMUNIDAD_MADRID' NOT NULL,
    fecha_disponible DATE NOT NULL
);
