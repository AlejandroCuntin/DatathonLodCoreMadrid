-- =============================================================================
-- LoDCORE Madrid • 03-vistas_apex.sql
-- Vistas con origen, metodo, dataset_version y salvaguarda no-compensatoria
-- =============================================================================

CREATE OR REPLACE VIEW v_apex_portal_ciudadano AS
SELECT 
    m.id_municipio,
    m.codigo_ine,
    m.nombre,
    m.comarca,
    m.poblacion_actual,
    m.tiempo_madrid_min,
    m.precio_m2_compra,
    m.precio_avm_m2,
    m.gap_mercado_pct,
    m.personas_acogida_efectiva AS capacidad_neta_residentes,
    
    -- Regla DURA de No-Compensatoriedad:
    -- Si hab_por_medico > 1500 o ocupacion_escolar_pct > 95, el semáforo se fuerza a BAJA (<40)
    CASE 
        WHEN m.hab_por_medico > 1500 OR m.ocupacion_escolar_pct > 95.0 THEN 'BAJA'
        WHEN m.indice_capacidad_global >= 60.0 THEN 'ALTA'
        WHEN m.indice_capacidad_global >= 40.0 THEN 'MEDIA'
        ELSE 'BAJA'
    END AS semaforo_ica,
    
    CASE 
        WHEN m.hab_por_medico > 1500 OR m.ocupacion_escolar_pct > 95.0 
        THEN LEAST(m.indice_capacidad_global, 39.0)
        ELSE m.indice_capacidad_global
    END AS indice_ica_ajustado,
    
    m.factor_limitante,
    m.arquetipo_nombre,
    m.dataset_version,
    m.origen,
    m.metodo
FROM municipios_procesados m;

CREATE OR REPLACE VIEW v_apex_panel_institucional AS
SELECT 
    m.comarca,
    COUNT(*) AS total_municipios,
    SUM(m.poblacion_actual) AS poblacion_total,
    SUM(m.personas_acogida_efectiva) AS capacidad_neta_comarcal,
    ROUND(AVG(m.indice_capacidad_global), 2) AS ica_promedio,
    ROUND(AVG(m.precio_m2_compra), 2) AS precio_m2_medio,
    ROUND(AVG(m.precio_avm_m2), 2) AS precio_avm_medio,
    SUM(CASE WHEN m.factor_limitante = 'SANIDAD' THEN 1 ELSE 0 END) AS alerta_sanitaria,
    SUM(CASE WHEN m.factor_limitante = 'EDUCACION' THEN 1 ELSE 0 END) AS alerta_educativa,
    SUM(CASE WHEN m.factor_limitante = 'VIVIENDA' THEN 1 ELSE 0 END) AS alerta_vivienda,
    m.dataset_version,
    m.origen,
    m.metodo
FROM municipios_procesados m
GROUP BY m.comarca, m.dataset_version, m.origen, m.metodo;
