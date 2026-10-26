-- =============================================================================
-- LoDCORE Madrid - 04-perfiles_y_ranking.sql
-- Perfil ciudadano en Oracle: reglas como datos + pesos + ranking por perfil.
--
-- SINCRONIZACION OBLIGATORIA:
--   Los valores de esta cabecera se replican desde src/lodcore/config/perfiles.py
--   y desde src/lodcore/config/thresholds.py. El test
--   tests/unit/test_perfiles_sql_sync.py compara ambos lados y falla si divergen.
--   Si cambias un numero, cambialo en los dos sitios.
--
-- Orden de ejecucion: 02 (tabla) -> 03 (vistas) -> 04 (este) -> 05 (ONNX)
-- =============================================================================

-- ---------------------------------------------------------------------------
-- 1. Parametros del perfil (numeros unicos, en datos y no escondidos en codigo)
-- ---------------------------------------------------------------------------
CREATE TABLE PERFILES_PARAMETROS (
    nombre      VARCHAR2(50) PRIMARY KEY,
    valor       NUMBER NOT NULL,
    descripcion VARCHAR2(200)
);

INSERT INTO PERFILES_PARAMETROS (nombre, valor, descripcion) VALUES ('max_transferencia_total', 0.20, 'Tope de masa que un perfil puede transferir entre dimensiones');
INSERT INTO PERFILES_PARAMETROS (nombre, valor, descripcion) VALUES ('peso_min', 0.05, 'Peso minimo de una dimension tras los ajustes');
INSERT INTO PERFILES_PARAMETROS (nombre, valor, descripcion) VALUES ('peso_max', 0.60, 'Peso maximo de una dimension tras los ajustes');
INSERT INTO PERFILES_PARAMETROS (nombre, valor, descripcion) VALUES ('max_hab_por_medico', 1500, 'Regla dura: colapso sanitario si se supera');
INSERT INTO PERFILES_PARAMETROS (nombre, valor, descripcion) VALUES ('max_ocupacion_escolar_pct', 95, 'Regla dura: colapso educativo si se supera');
INSERT INTO PERFILES_PARAMETROS (nombre, valor, descripcion) VALUES ('umbral_ica_baja', 40, 'Por debajo de este ICA el semaforo es BAJA');
INSERT INTO PERFILES_PARAMETROS (nombre, valor, descripcion) VALUES ('umbral_ica_media', 60, 'A partir de este ICA el semaforo es ALTA');
INSERT INTO PERFILES_PARAMETROS (nombre, valor, descripcion) VALUES ('techo_afinidad_alerta', 39, 'Techo de afinidad si el municipio colapsa');

-- ---------------------------------------------------------------------------
-- 2. Pesos base por perfil (ciudadano: pesos iguales)
-- ---------------------------------------------------------------------------
CREATE TABLE PERFILES_BASE (
    perfil    VARCHAR2(30),
    dimension VARCHAR2(20),
    peso      NUMBER NOT NULL,
    CONSTRAINT pk_perfiles_base PRIMARY KEY (perfil, dimension),
    CONSTRAINT ck_perfiles_dim CHECK (dimension IN ('vivienda','educacion','conectividad','sanidad'))
);

INSERT INTO PERFILES_BASE (perfil, dimension, peso) VALUES ('ciudadano', 'vivienda', 0.25);
INSERT INTO PERFILES_BASE (perfil, dimension, peso) VALUES ('ciudadano', 'educacion', 0.25);
INSERT INTO PERFILES_BASE (perfil, dimension, peso) VALUES ('ciudadano', 'conectividad', 0.25);
INSERT INTO PERFILES_BASE (perfil, dimension, peso) VALUES ('ciudadano', 'sanidad', 0.25);

-- ---------------------------------------------------------------------------
-- 3. Reglas de ajuste personal (supuestos declarados, no verdades)
--    tope NULL = sin tope propio (solo aplica el tope global de transferencia)
-- ---------------------------------------------------------------------------
CREATE TABLE PERFILES_AJUSTES (
    regla              VARCHAR2(30) PRIMARY KEY,
    dimension          VARCHAR2(20) NOT NULL,
    delta              NUMBER NOT NULL,
    tope               NUMBER,
    rango_sensibilidad NUMBER NOT NULL,
    justificacion      VARCHAR2(200)
);

INSERT INTO PERFILES_AJUSTES (regla, dimension, delta, tope, rango_sensibilidad, justificacion) VALUES ('hijo', 'educacion', 0.05, 0.15, 0.02, 'La escolarizacion es la primera restriccion de una familia');
INSERT INTO PERFILES_AJUSTES (regla, dimension, delta, tope, rango_sensibilidad, justificacion) VALUES ('edad_joven', 'educacion', 0.05, NULL, 0.02, 'Etapa de formacion de hogar (edad <= 45)');
INSERT INTO PERFILES_AJUSTES (regla, dimension, delta, tope, rango_sensibilidad, justificacion) VALUES ('edad_senior', 'sanidad', 0.10, NULL, 0.03, 'Uso sanitario creciente (edad >= 65)');
INSERT INTO PERFILES_AJUSTES (regla, dimension, delta, tope, rango_sensibilidad, justificacion) VALUES ('edad_media', 'sanidad', 0.05, NULL, 0.02, 'Transicion (46 <= edad < 65)');
INSERT INTO PERFILES_AJUSTES (regla, dimension, delta, tope, rango_sensibilidad, justificacion) VALUES ('transporte_publico', 'conectividad', 0.05, NULL, 0.02, 'Dependencia real de la red de transporte');
INSERT INTO PERFILES_AJUSTES (regla, dimension, delta, tope, rango_sensibilidad, justificacion) VALUES ('alquiler', 'vivienda', 0.05, NULL, 0.02, 'Sensibilidad al mercado de alquiler');

COMMIT;

-- ---------------------------------------------------------------------------
-- 4. Tipos para las funciones pipelined
-- ---------------------------------------------------------------------------
CREATE OR REPLACE TYPE t_peso AS OBJECT (
    dimension VARCHAR2(20),
    peso      NUMBER
);
/

CREATE OR REPLACE TYPE t_pesos AS TABLE OF t_peso;
/

CREATE OR REPLACE TYPE t_ranking_row AS OBJECT (
    nombre                  VARCHAR2(100),
    comarca                 VARCHAR2(100),
    afinidad                NUMBER,
    desglose_vivienda       NUMBER,
    desglose_educacion      NUMBER,
    desglose_conectividad   NUMBER,
    desglose_sanidad        NUMBER,
    indice_ica_ajustado     NUMBER,
    semaforo_ica            VARCHAR2(10),
    alerta_no_compensatoria CHAR(1),
    factor_limitante        VARCHAR2(50)
);
/

CREATE OR REPLACE TYPE t_ranking AS TABLE OF t_ranking_row;
/

-- ---------------------------------------------------------------------------
-- 5. Pesos del perfil ciudadano (replica la transferencia de perfiles.py)
-- ---------------------------------------------------------------------------
CREATE OR REPLACE FUNCTION f_pesos_ciudadano (
    p_hijos      IN NUMBER   DEFAULT 0,
    p_edad       IN NUMBER   DEFAULT 35,
    p_transporte IN VARCHAR2 DEFAULT 'publico',
    p_tenencia   IN VARCHAR2 DEFAULT 'compra'
) RETURN t_pesos PIPELINED
IS
    v_viv NUMBER;
    v_edu NUMBER;
    v_con NUMBER;
    v_san NUMBER;
    v_inc_viv NUMBER := 0;
    v_inc_edu NUMBER := 0;
    v_inc_con NUMBER := 0;
    v_inc_san NUMBER := 0;
    v_delta NUMBER;
    v_tope NUMBER;
    v_total NUMBER;
    v_pool NUMBER;
    v_factor NUMBER;
    v_max_transf NUMBER;
    v_peso_max NUMBER;
BEGIN
    SELECT MAX(CASE WHEN dimension = 'vivienda'     THEN peso END),
           MAX(CASE WHEN dimension = 'educacion'    THEN peso END),
           MAX(CASE WHEN dimension = 'conectividad' THEN peso END),
           MAX(CASE WHEN dimension = 'sanidad'      THEN peso END)
      INTO v_viv, v_edu, v_con, v_san
      FROM PERFILES_BASE
     WHERE perfil = 'ciudadano';

    SELECT valor INTO v_max_transf FROM PERFILES_PARAMETROS WHERE nombre = 'max_transferencia_total';
    SELECT valor INTO v_peso_max   FROM PERFILES_PARAMETROS WHERE nombre = 'peso_max';

    -- Hijos: delta por hijo, con tope propio
    IF p_hijos > 0 THEN
        SELECT delta, tope INTO v_delta, v_tope FROM PERFILES_AJUSTES WHERE regla = 'hijo';
        v_inc_edu := v_inc_edu + LEAST(NVL(v_tope, 99), v_delta * p_hijos);
    END IF;

    -- Edad
    IF p_edad <= 45 THEN
        SELECT delta INTO v_delta FROM PERFILES_AJUSTES WHERE regla = 'edad_joven';
        v_inc_edu := v_inc_edu + v_delta;
    ELSIF p_edad >= 65 THEN
        SELECT delta INTO v_delta FROM PERFILES_AJUSTES WHERE regla = 'edad_senior';
        v_inc_san := v_inc_san + v_delta;
    ELSE
        SELECT delta INTO v_delta FROM PERFILES_AJUSTES WHERE regla = 'edad_media';
        v_inc_san := v_inc_san + v_delta;
    END IF;

    -- Transporte y tenencia
    IF LOWER(p_transporte) = 'publico' THEN
        SELECT delta INTO v_delta FROM PERFILES_AJUSTES WHERE regla = 'transporte_publico';
        v_inc_con := v_inc_con + v_delta;
    END IF;
    IF LOWER(p_tenencia) = 'alquiler' THEN
        SELECT delta INTO v_delta FROM PERFILES_AJUSTES WHERE regla = 'alquiler';
        v_inc_viv := v_inc_viv + v_delta;
    END IF;

    -- Tope individual de la dimension receptora
    IF v_inc_viv > 0 AND v_viv + v_inc_viv > v_peso_max THEN
        v_inc_viv := GREATEST(0, v_peso_max - v_viv);
    END IF;
    IF v_inc_edu > 0 AND v_edu + v_inc_edu > v_peso_max THEN
        v_inc_edu := GREATEST(0, v_peso_max - v_edu);
    END IF;
    IF v_inc_con > 0 AND v_con + v_inc_con > v_peso_max THEN
        v_inc_con := GREATEST(0, v_peso_max - v_con);
    END IF;
    IF v_inc_san > 0 AND v_san + v_inc_san > v_peso_max THEN
        v_inc_san := GREATEST(0, v_peso_max - v_san);
    END IF;

    -- Tope global de transferencia
    v_total := v_inc_viv + v_inc_edu + v_inc_con + v_inc_san;
    IF v_total > v_max_transf THEN
        v_factor := v_max_transf / v_total;
        v_inc_viv := v_inc_viv * v_factor;
        v_inc_edu := v_inc_edu * v_factor;
        v_inc_con := v_inc_con * v_factor;
        v_inc_san := v_inc_san * v_factor;
        v_total := v_max_transf;
    END IF;

    -- Masa disponible en las dimensiones que NO reciben
    v_pool := 0;
    IF v_inc_viv = 0 THEN v_pool := v_pool + v_viv; END IF;
    IF v_inc_edu = 0 THEN v_pool := v_pool + v_edu; END IF;
    IF v_inc_con = 0 THEN v_pool := v_pool + v_con; END IF;
    IF v_inc_san = 0 THEN v_pool := v_pool + v_san; END IF;

    IF v_total > 0 AND v_pool > 0 THEN
        -- Transferencia: se resta a las no ajustadas en proporcion a su peso
        IF v_inc_viv > 0 THEN v_viv := v_viv + v_inc_viv; ELSE v_viv := v_viv - v_total * (v_viv / v_pool); END IF;
        IF v_inc_edu > 0 THEN v_edu := v_edu + v_inc_edu; ELSE v_edu := v_edu - v_total * (v_edu / v_pool); END IF;
        IF v_inc_con > 0 THEN v_con := v_con + v_inc_con; ELSE v_con := v_con - v_total * (v_con / v_pool); END IF;
        IF v_inc_san > 0 THEN v_san := v_san + v_inc_san; ELSE v_san := v_san - v_total * (v_san / v_pool); END IF;
    ELSIF v_total > 0 THEN
        -- Caso limite: las cuatro dimensiones reciben. Se suma y se normaliza.
        v_viv := v_viv + v_inc_viv;
        v_edu := v_edu + v_inc_edu;
        v_con := v_con + v_inc_con;
        v_san := v_san + v_inc_san;
    END IF;

    -- Normalizacion final
    v_total := v_viv + v_edu + v_con + v_san;
    IF v_total > 0 THEN
        v_viv := v_viv / v_total;
        v_edu := v_edu / v_total;
        v_con := v_con / v_total;
        v_san := v_san / v_total;
    END IF;

    PIPE ROW (t_peso('vivienda',     ROUND(v_viv, 6)));
    PIPE ROW (t_peso('educacion',    ROUND(v_edu, 6)));
    PIPE ROW (t_peso('conectividad', ROUND(v_con, 6)));
    PIPE ROW (t_peso('sanidad',      ROUND(v_san, 6)));
    RETURN;
END;
/

-- ---------------------------------------------------------------------------
-- 6. Ranking del perfil ciudadano
--    Formula: suma ponderada de los 4 sub-indices (igual que ranking.py).
--    El colapso no excluye: se marca y se aplica el techo de afinidad.
-- ---------------------------------------------------------------------------
CREATE OR REPLACE FUNCTION f_ranking_ciudadano (
    p_presupuesto_m2 IN NUMBER,
    p_tiempo_max     IN NUMBER,
    p_hijos          IN NUMBER   DEFAULT 0,
    p_edad           IN NUMBER   DEFAULT 35,
    p_transporte     IN VARCHAR2 DEFAULT 'publico',
    p_tenencia       IN VARCHAR2 DEFAULT 'compra'
) RETURN t_ranking PIPELINED
IS
    v_viv NUMBER;
    v_edu NUMBER;
    v_con NUMBER;
    v_san NUMBER;
    v_max_hab NUMBER;
    v_max_ocup NUMBER;
    v_umbral_baja NUMBER;
    v_umbral_media NUMBER;
    v_techo NUMBER;
    v_alerta CHAR(1);
    v_af NUMBER;
    v_ica NUMBER;
    v_semaforo VARCHAR2(10);
BEGIN
    SELECT MAX(CASE WHEN dimension = 'vivienda'     THEN peso END),
           MAX(CASE WHEN dimension = 'educacion'    THEN peso END),
           MAX(CASE WHEN dimension = 'conectividad' THEN peso END),
           MAX(CASE WHEN dimension = 'sanidad'      THEN peso END)
      INTO v_viv, v_edu, v_con, v_san
      FROM TABLE(f_pesos_ciudadano(p_hijos, p_edad, p_transporte, p_tenencia));

    SELECT valor INTO v_max_hab      FROM PERFILES_PARAMETROS WHERE nombre = 'max_hab_por_medico';
    SELECT valor INTO v_max_ocup     FROM PERFILES_PARAMETROS WHERE nombre = 'max_ocupacion_escolar_pct';
    SELECT valor INTO v_umbral_baja  FROM PERFILES_PARAMETROS WHERE nombre = 'umbral_ica_baja';
    SELECT valor INTO v_umbral_media FROM PERFILES_PARAMETROS WHERE nombre = 'umbral_ica_media';
    SELECT valor INTO v_techo        FROM PERFILES_PARAMETROS WHERE nombre = 'techo_afinidad_alerta';

    FOR r IN (
        SELECT * FROM (
            SELECT m.nombre,
                   m.comarca,
                   m.score_vivienda,
                   m.score_educacion,
                   m.score_conectividad,
                   m.score_sanidad,
                   m.hab_por_medico,
                   m.ocupacion_escolar_pct,
                   m.indice_capacidad_global,
                   m.factor_limitante,
                   (v_viv * m.score_vivienda
                    + v_edu * m.score_educacion
                    + v_con * m.score_conectividad
                    + v_san * m.score_sanidad) AS afinidad
              FROM municipios_procesados m
             WHERE (CASE WHEN LOWER(p_tenencia) = 'compra'
                         THEN m.precio_m2_compra
                         ELSE m.precio_m2_alquiler END) <= p_presupuesto_m2
               AND m.tiempo_medio_madrid_minutos <= p_tiempo_max
        )
        ORDER BY CASE WHEN hab_por_medico > v_max_hab OR ocupacion_escolar_pct > v_max_ocup
                      THEN LEAST(afinidad, v_techo)
                      ELSE afinidad END DESC,
                 indice_capacidad_global DESC,
                 nombre
    ) LOOP
        IF r.hab_por_medico > v_max_hab OR r.ocupacion_escolar_pct > v_max_ocup THEN
            v_alerta := 'S';
            v_af := LEAST(r.afinidad, v_techo);
            v_ica := LEAST(r.indice_capacidad_global, v_umbral_baja - 1);
            v_semaforo := 'BAJA';
        ELSE
            v_alerta := 'N';
            v_af := r.afinidad;
            v_ica := r.indice_capacidad_global;
            IF v_ica >= v_umbral_media THEN
                v_semaforo := 'ALTA';
            ELSIF v_ica >= v_umbral_baja THEN
                v_semaforo := 'MEDIA';
            ELSE
                v_semaforo := 'BAJA';
            END IF;
        END IF;

        PIPE ROW (t_ranking_row(
            r.nombre,
            r.comarca,
            ROUND(v_af, 2),
            ROUND(v_viv * r.score_vivienda, 2),
            ROUND(v_edu * r.score_educacion, 2),
            ROUND(v_con * r.score_conectividad, 2),
            ROUND(v_san * r.score_sanidad, 2),
            ROUND(v_ica, 2),
            v_semaforo,
            v_alerta,
            r.factor_limitante
        ));
    END LOOP;
    RETURN;
END;
/

-- ---------------------------------------------------------------------------
-- 7. Vista de apoyo para APEX (ranking con los parametros por defecto)
-- ---------------------------------------------------------------------------
CREATE OR REPLACE VIEW v_ranking_ciudadano_demo AS
SELECT nombre, comarca, afinidad, semaforo_ica,
       alerta_no_compensatoria, factor_limitante, indice_ica_ajustado
  FROM TABLE(f_ranking_ciudadano(
           p_presupuesto_m2 => 2500,
           p_tiempo_max     => 90,
           p_hijos          => 0,
           p_edad           => 35,
           p_transporte     => 'publico',
           p_tenencia       => 'compra'
       ));

COMMENT ON TABLE PERFILES_AJUSTES IS
    'Reglas del perfil ciudadano. Replicadas desde src/lodcore/config/perfiles.py; test de sincronizacion obligatorio.';
COMMENT ON FUNCTION f_ranking_ciudadano IS
    'Ranking por perfil. Formula: suma ponderada de sub-indices + techo no compensatorio. Equivalente a m5_recomendador/ranking.py.';
