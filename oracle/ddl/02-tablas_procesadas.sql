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
    -- hab_por_medico se redondea a 0 decimales para replicar exactamente el panel F2
    -- con el que se entrenó M4 (si Oracle usara 2 decimales, los splits del árbol podrían cambiar).
    hab_por_medico NUMBER(8,2) GENERATED ALWAYS AS (ROUND(poblacion_actual / NULLIF(num_medicos_ap, 0), 0)) VIRTUAL,
    plazas_escolares NUMBER(6) NOT NULL,
    alumnos_matriculados NUMBER(6) NOT NULL,
    ocupacion_escolar_pct NUMBER(5,2) GENERATED ALWAYS AS (ROUND((alumnos_matriculados / NULLIF(plazas_escolares, 0)) * 100, 2)) VIRTUAL,
    
    -- Movilidad, conectividad y vivienda (entradas reales de los modelos M1/M4)
    cobertura_fibra_pct NUMBER(5,2) NOT NULL,
    paradas_x1000 NUMBER(8,3) NOT NULL,
    vacias_x1000 NUMBER(8,3) NOT NULL,
    stock_vivienda_vacia_est NUMBER(7) NOT NULL,
    suelo_urbano_disponible_m2 NUMBER(12,2) NOT NULL,

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
    origen VARCHAR2(100) DEFAULT 'OBSERVADO+SIMULADO' NOT NULL,
    metodo VARCHAR2(100) DEFAULT 'PANEL_INTEGRADO_MINMAX_PCA' NOT NULL,
    fuente_datos VARCHAR2(150) NOT NULL,
    fecha_disponible DATE NOT NULL,
    fecha_carga TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    CONSTRAINT chk_municipios_origen CHECK (
        REGEXP_LIKE(
            origen,
            '^(OBSERVADO|IMPUTADO|ESTIMADO|PROYECTADO|SIMULADO)(\+(OBSERVADO|IMPUTADO|ESTIMADO|PROYECTADO|SIMULADO))*$'
        )
    )
);
