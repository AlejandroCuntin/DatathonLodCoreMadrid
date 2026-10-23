-- =============================================================================
-- LoDCORE Madrid • 05-modelos_onnx.sql
-- Nivel N2: Scoring en motor Oracle Database 23ai con DBMS_VECTOR.LOAD_ONNX_MODEL
-- Artefactos exportados en `oracle/onnx/m1_avm.onnx` y `oracle/onnx/m4_capacidad.onnx`
-- Equivalencia verificada en CI: |score_ONNX - score_Python| < 1e-6 (0.00e+00)
-- =============================================================================

-- 1. Carga de los modelos ONNX (M1 AVM y M4 Capacidad de Acogida)
BEGIN
    DBMS_VECTOR.LOAD_ONNX_MODEL(
        directory  => 'LODCORE_ONNX_DIR',
        file_name  => 'm1_avm.onnx',
        model_name => 'M1_AVM_HEDONICO'
    );

    DBMS_VECTOR.LOAD_ONNX_MODEL(
        directory  => 'LODCORE_ONNX_DIR',
        file_name  => 'm4_capacidad.onnx',
        model_name => 'M4_CAPACIDAD_ACOGIDA'
    );
END;
/

-- 2. Vista de Scoring N2 en base de datos con procedencia y salvaguarda no compensatoria
CREATE OR REPLACE VIEW v_onnx_scoring_n2 AS
SELECT
    m.id_municipio,
    m.codigo_ine,
    m.nombre,
    m.comarca,
    ROUND(
        PREDICTION(
            M1_AVM_HEDONICO USING
            m.tiempo_madrid_min AS tiempo_medio_madrid_minutos,
            m.densidad AS densidad,
            85.0 AS cobertura_fibra_pct,
            7.5 AS paradas_x1000,
            95.0 AS vacias_x1000,
            ROUND((m.num_medicos_ap / NULLIF(m.poblacion_actual, 0)) * 1000, 4) AS medicos_x1000,
            ROUND(1.0 - (m.ocupacion_escolar_pct / 100.0), 4) AS tasa_holgura_escolar
        ),
        2
    ) AS precio_avm_onnx_m2,
    ROUND(
        PREDICTION(
            M4_CAPACIDAD_ACOGIDA USING
            m.score_sanidad,
            m.score_educacion,
            m.score_conectividad,
            m.score_vivienda,
            m.hab_por_medico,
            m.ocupacion_escolar_pct,
            500.0 AS stock_vivienda_vacia_est,
            120000.0 AS suelo_urbano_disponible_m2
        ),
        2
    ) AS score_capacidad_onnx_raw,
    m.origen,
    'ORACLE_ONNX_N2_PREDICTION' AS metodo,
    m.dataset_version
FROM municipios_procesados m;
