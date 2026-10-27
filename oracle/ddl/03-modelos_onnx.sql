-- =============================================================================
-- LoDCORE Madrid • 03-modelos_onnx.sql
-- Nivel N2: Scoring en motor Oracle Database 23ai con DBMS_VECTOR.LOAD_ONNX_MODEL
-- Artefactos exportados en `oracle/onnx/m1_avm.onnx` y `oracle/onnx/m4_capacidad.onnx`
-- Equivalencia verificada en CI: error relativo < 1e-6 y error absoluto < 1e-3
-- (el binario ONNX devuelve float32; un absoluto < 1e-6 no es representable a escalas de 2.000)
--
-- IMPORTANTE: los modelos de scikit-learn se exportan con un único tensor de
-- entrada llamado `float_input` y una salida llamada `variable`. Sin el metadata
-- JSON, Oracle carga el ONNX como modelo de embeddings y `PREDICTION` falla.
-- El bloque `input` asocia cada posición del tensor con una columna SQL.
-- =============================================================================

-- 1. Carga de los modelos ONNX (M1 AVM y M4 Capacidad de Acogida)
BEGIN
    DBMS_VECTOR.LOAD_ONNX_MODEL(
        directory  => 'LODCORE_ONNX_DIR',
        file_name  => 'm1_avm.onnx',
        model_name => 'M1_AVM_HEDONICO',
        metadata   => JSON('{
            "function": "regression",
            "regressionOutput": "variable",
            "input": {  
                "float_input": [
                    "tiempo_medio_madrid_minutos",
                    "densidad",
                    "cobertura_fibra_pct",
                    "paradas_x1000",
                    "vacias_x1000",
                    "medicos_x1000",
                    "tasa_holgura_escolar"
                ]
            }
        }')
    );

    DBMS_VECTOR.LOAD_ONNX_MODEL(
        directory  => 'LODCORE_ONNX_DIR',
        file_name  => 'm4_capacidad.onnx',
        model_name => 'M4_CAPACIDAD_ACOGIDA',
        metadata   => JSON('{
            "function": "regression",
            "regressionOutput": "variable",
            "input": {
                "float_input": [
                    "score_sanidad",
                    "score_educacion",
                    "score_conectividad",
                    "score_vivienda",
                    "hab_por_medico",
                    "ocupacion_escolar_pct",
                    "stock_vivienda_vacia_est",
                    "suelo_urbano_disponible_m2"
                ]
            }
        }')
    );
END;
/

-- 2. Vista de Scoring N2 en base de datos con procedencia y salvaguarda no compensatoria.
-- `USING *` pasa todas las columnas de `features`; Oracle selecciona las que
-- declara el metadata de cada modelo (no es necesario repetir la lista).
CREATE OR REPLACE VIEW v_onnx_scoring_n2 AS
WITH features AS (
    SELECT
        m.id_municipio,
        m.codigo_ine,
        m.nombre,
        m.comarca,
        m.tiempo_madrid_min AS tiempo_medio_madrid_minutos,
        m.densidad,
        m.cobertura_fibra_pct,
        m.paradas_x1000,
        m.vacias_x1000,
        -- Sin redondeo: replican exactamente las columnas del panel F2
        -- (medicos_x1000 y tasa_holgura_escolar se calcularon con precisión completa).
        (m.num_medicos_ap / NULLIF(m.poblacion_actual, 0)) * 1000 AS medicos_x1000,
        1.0 - (m.alumnos_matriculados / NULLIF(m.plazas_escolares, 0)) AS tasa_holgura_escolar,
        m.score_sanidad,
        m.score_educacion,
        m.score_conectividad,
        m.score_vivienda,
        m.hab_por_medico,
        m.ocupacion_escolar_pct,
        m.stock_vivienda_vacia_est,
        m.suelo_urbano_disponible_m2,
        m.origen,
        m.fuente_datos,
        m.dataset_version
    FROM municipios_procesados m
)
SELECT
    f.id_municipio,
    f.codigo_ine,
    f.nombre,
    f.comarca,
    ROUND(PREDICTION(M1_AVM_HEDONICO USING *), 2) AS precio_avm_onnx_m2,
    ROUND(PREDICTION(M4_CAPACIDAD_ACOGIDA USING *), 2) AS score_capacidad_onnx_raw,
    f.origen,
    'ORACLE_ONNX_N2_PREDICTION' AS metodo,
    f.fuente_datos,
    f.dataset_version
FROM features f;
