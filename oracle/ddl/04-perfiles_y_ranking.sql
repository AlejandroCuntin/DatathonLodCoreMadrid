-- =============================================================================
-- LoDCORE Madrid - 04-perfiles_y_ranking.sql
-- Perfil ciudadano en Oracle: reglas como datos + pesos + ranking + asequibilidad.
--
-- SINCRONIZACION OBLIGATORIA:
--   Los valores de esta cabecera se replican desde src/lodcore/config/perfiles.py
--   y src/lodcore/config/thresholds.py. El test
--   tests/unit/test_perfiles_sql_sync.py compara ambos lados y falla si divergen.
--
-- SCRIPT REEJECUTABLE: borra y recrea sus propios objetos al principio.
-- Orden de ejecucion: 01 -> 02 -> 03 (ONNX) -> 04 (este)
-- =============================================================================

-- ---------------------------------------------------------------------------
-- 0. Limpieza idempotente (permite relanzar el script sin errores)
--    Sentencias individuales: no se recorre user_objects mientras se borran
--    objetos (eso puede invalidar el cursor).
-- ---------------------------------------------------------------------------
BEGIN EXECUTE IMMEDIATE 'DROP VIEW v_ranking_ciudadano_demo'; EXCEPTION WHEN OTHERS THEN NULL; END;
/
BEGIN EXECUTE IMMEDIATE 'DROP FUNCTION f_ranking_ciudadano'; EXCEPTION WHEN OTHERS THEN NULL; END;
/
BEGIN EXECUTE IMMEDIATE 'DROP FUNCTION f_pesos_ciudadano'; EXCEPTION WHEN OTHERS THEN NULL; END;
/
BEGIN EXECUTE IMMEDIATE 'DROP TABLE perfiles_ajustes CASCADE CONSTRAINTS'; EXCEPTION WHEN OTHERS THEN NULL; END;
/
BEGIN EXECUTE IMMEDIATE 'DROP TABLE perfiles_base CASCADE CONSTRAINTS'; EXCEPTION WHEN OTHERS THEN NULL; END;
/
BEGIN EXECUTE IMMEDIATE 'DROP TABLE perfiles_parametros CASCADE CONSTRAINTS'; EXCEPTION WHEN OTHERS THEN NULL; END;
/

BEGIN EXECUTE IMMEDIATE 'DROP TYPE t_ranking FORCE'; EXCEPTION WHEN OTHERS THEN NULL; END;
/
BEGIN EXECUTE IMMEDIATE 'DROP TYPE t_ranking_row FORCE'; EXCEPTION WHEN OTHERS THEN NULL; END;
/
BEGIN EXECUTE IMMEDIATE 'DROP TYPE t_pesos FORCE'; EXCEPTION WHEN OTHERS THEN NULL; END;
/
BEGIN EXECUTE IMMEDIATE 'DROP TYPE t_peso FORCE'; EXCEPTION WHEN OTHERS THEN NULL; END;
/

-- ---------------------------------------------------------------------------
-- 1. Parametros (numeros unicos, en datos y no escondidos en codigo)
-- ---------------------------------------------------------------------------
CREATE TABLE PERFILES_PARAMETROS (
    nombre      VARCHAR2(50) PRIMARY KEY,
    valor       NUMBER NOT NULL,
    descripcion VARCHAR2(200)
);

INSERT INTO PERFILES_PARAMETROS VALUES ('max_transferencia_total', 0.20, 'Tope de masa que un perfil puede transferir');
INSERT INTO PERFILES_PARAMETROS VALUES ('peso_min', 0.05, 'Peso minimo de una dimension');
INSERT INTO PERFILES_PARAMETROS VALUES ('peso_max', 0.60, 'Peso maximo de una dimension');
INSERT INTO PERFILES_PARAMETROS VALUES ('max_hab_por_medico', 1500, 'Colapso sanitario si se supera');
INSERT INTO PERFILES_PARAMETROS VALUES ('max_ocupacion_escolar_pct', 95, 'Colapso educativo si se supera');
INSERT INTO PERFILES_PARAMETROS VALUES ('umbral_ica_baja', 40, 'Por debajo, semaforo BAJA');
INSERT INTO PERFILES_PARAMETROS VALUES ('umbral_ica_media', 60, 'Desde aqui, semaforo ALTA');
INSERT INTO PERFILES_PARAMETROS VALUES ('techo_afinidad_alerta', 39, 'Techo de afinidad si colapsa');
INSERT INTO PERFILES_PARAMETROS VALUES ('entrada_pct', 0.20, 'Fraccion del precio no financiada');
INSERT INTO PERFILES_PARAMETROS VALUES ('esfuerzo_maximo_pct', 30, 'Esfuerzo maximo para el precio sostenible');
INSERT INTO PERFILES_PARAMETROS VALUES ('tipo_interes_anual', 0.035, 'Tipo fijo declarado de la hipoteca');
INSERT INTO PERFILES_PARAMETROS VALUES ('anios_hipoteca', 30, 'Plazo de la hipoteca en anios');
INSERT INTO PERFILES_PARAMETROS VALUES ('financiacion_pct', 0.80, 'Fraccion del precio financiada');
INSERT INTO PERFILES_PARAMETROS VALUES ('umbral_asequible', 30, 'Esfuerzo <= 30: Asequible');
INSERT INTO PERFILES_PARAMETROS VALUES ('umbral_ajustado', 35, 'Esfuerzo <= 35: Ajustado');
INSERT INTO PERFILES_PARAMETROS VALUES ('umbral_alto', 45, 'Esfuerzo <= 45: Alto; por encima: No asequible');

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

INSERT INTO PERFILES_BASE VALUES ('ciudadano', 'vivienda', 0.25);
INSERT INTO PERFILES_BASE VALUES ('ciudadano', 'educacion', 0.25);
INSERT INTO PERFILES_BASE VALUES ('ciudadano', 'conectividad', 0.25);
INSERT INTO PERFILES_BASE VALUES ('ciudadano', 'sanidad', 0.25);

-- ---------------------------------------------------------------------------
-- 3. Reglas de ajuste personal (supuestos declarados, no verdades)
-- ---------------------------------------------------------------------------
CREATE TABLE PERFILES_AJUSTES (
    regla              VARCHAR2(30) PRIMARY KEY,
    dimension          VARCHAR2(20) NOT NULL,
    delta              NUMBER NOT NULL,
    tope               NUMBER,
    rango_sensibilidad NUMBER NOT NULL,
    justificacion      VARCHAR2(200)
);

INSERT INTO PERFILES_AJUSTES VALUES ('hijo', 'educacion', 0.05, 0.15, 0.02, 'La escolarizacion es la primera restriccion de una familia');
INSERT INTO PERFILES_AJUSTES VALUES ('edad_joven', 'educacion', 0.05, NULL, 0.02, 'Etapa de formacion de hogar (edad <= 45)');
INSERT INTO PERFILES_AJUSTES VALUES ('edad_senior', 'sanidad', 0.10, NULL, 0.03, 'Uso sanitario creciente (edad >= 65)');
INSERT INTO PERFILES_AJUSTES VALUES ('edad_media', 'sanidad', 0.05, NULL, 0.02, 'Transicion (46 <= edad < 65)');
INSERT INTO PERFILES_AJUSTES VALUES ('transporte_publico', 'conectividad', 0.05, NULL, 0.02, 'Dependencia real de la red de transporte');
INSERT INTO PERFILES_AJUSTES VALUES ('alquiler', 'vivienda', 0.05, NULL, 0.02, 'Sensibilidad al mercado de alquiler');

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
    codigo_ine              VARCHAR2(10),
    comarca                 VARCHAR2(100),
    afinidad                NUMBER,
    desglose_vivienda       NUMBER,
    desglose_educacion      NUMBER,
    desglose_conectividad   NUMBER,
    desglose_sanidad        NUMBER,
    indice_ica_ajustado     NUMBER,
    semaforo_ica            VARCHAR2(10),
    alerta_no_compensatoria CHAR(1),
    factor_limitante        VARCHAR2(50),
    precio_m2               NUMBER,
    cuota_mensual_eur       NUMBER,
    entrada_eur             NUMBER,
    ingresos_necesarios_eur NUMBER,
    precio_max_sostenible_m2 NUMBER,
    esfuerzo_pct            NUMBER,
    etiqueta_esfuerzo       VARCHAR2(20),
    precio_avm_eur_m2       NUMBER,
    gap_mercado_pct         NUMBER,
    diagnostico_mercado     VARCHAR2(50)
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

    IF p_hijos > 0 THEN
        SELECT delta, tope INTO v_delta, v_tope FROM PERFILES_AJUSTES WHERE regla = 'hijo';
        v_inc_edu := v_inc_edu + LEAST(NVL(v_tope, 99), v_delta * p_hijos);
    END IF;

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

    IF LOWER(p_transporte) = 'publico' THEN
        SELECT delta INTO v_delta FROM PERFILES_AJUSTES WHERE regla = 'transporte_publico';
        v_inc_con := v_inc_con + v_delta;
    END IF;
    IF LOWER(p_tenencia) = 'alquiler' THEN
        SELECT delta INTO v_delta FROM PERFILES_AJUSTES WHERE regla = 'alquiler';
        v_inc_viv := v_inc_viv + v_delta;
    END IF;

    -- Tope individual de la dimension receptora
    IF v_inc_viv > 0 AND v_viv + v_inc_viv > v_peso_max THEN v_inc_viv := GREATEST(0, v_peso_max - v_viv); END IF;
    IF v_inc_edu > 0 AND v_edu + v_inc_edu > v_peso_max THEN v_inc_edu := GREATEST(0, v_peso_max - v_edu); END IF;
    IF v_inc_con > 0 AND v_con + v_inc_con > v_peso_max THEN v_inc_con := GREATEST(0, v_peso_max - v_con); END IF;
    IF v_inc_san > 0 AND v_san + v_inc_san > v_peso_max THEN v_inc_san := GREATEST(0, v_peso_max - v_san); END IF;

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
        IF v_inc_viv > 0 THEN v_viv := v_viv + v_inc_viv; ELSE v_viv := v_viv - v_total * (v_viv / v_pool); END IF;
        IF v_inc_edu > 0 THEN v_edu := v_edu + v_inc_edu; ELSE v_edu := v_edu - v_total * (v_edu / v_pool); END IF;
        IF v_inc_con > 0 THEN v_con := v_con + v_inc_con; ELSE v_con := v_con - v_total * (v_con / v_pool); END IF;
        IF v_inc_san > 0 THEN v_san := v_san + v_inc_san; ELSE v_san := v_san - v_total * (v_san / v_pool); END IF;
    ELSIF v_total > 0 THEN
        v_viv := v_viv + v_inc_viv;
        v_edu := v_edu + v_inc_edu;
        v_con := v_con + v_inc_con;
        v_san := v_san + v_inc_san;
    END IF;

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
-- 6. Ranking del perfil ciudadano con asequibilidad
--    Formula: suma ponderada de los 4 sub-indices (igual que ranking.py).
--    Presupuesto efectivo = minimo(declarado, sostenible segun ingresos).
-- ---------------------------------------------------------------------------
CREATE OR REPLACE FUNCTION f_ranking_ciudadano (
    p_presupuesto_m2 IN NUMBER,
    p_tiempo_max     IN NUMBER,
    p_hijos          IN NUMBER   DEFAULT 0,
    p_edad           IN NUMBER   DEFAULT 35,
    p_transporte     IN VARCHAR2 DEFAULT 'publico',
    p_tenencia       IN VARCHAR2 DEFAULT 'compra',
    p_ingresos       IN NUMBER   DEFAULT 2500,
    p_m2             IN NUMBER   DEFAULT 90
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
    v_entrada_pct NUMBER;
    v_esf_max NUMBER;
    v_tipo NUMBER;
    v_anios NUMBER;
    v_financiacion NUMBER;
    v_u_aseq NUMBER;
    v_u_ajus NUMBER;
    v_u_alto NUMBER;
    v_ingresos NUMBER;
    v_m2 NUMBER;
    v_tenencia VARCHAR2(20);
    v_factor NUMBER;
    v_cuota_max NUMBER;
    v_precio_max NUMBER;
    v_presupuesto NUMBER;
    v_precio NUMBER;
    v_cuota NUMBER;
    v_entrada NUMBER;
    v_esf NUMBER;
    v_ing_nec NUMBER;
    v_etiqueta VARCHAR2(20);
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

    SELECT valor INTO v_max_hab       FROM PERFILES_PARAMETROS WHERE nombre = 'max_hab_por_medico';
    SELECT valor INTO v_max_ocup      FROM PERFILES_PARAMETROS WHERE nombre = 'max_ocupacion_escolar_pct';
    SELECT valor INTO v_umbral_baja   FROM PERFILES_PARAMETROS WHERE nombre = 'umbral_ica_baja';
    SELECT valor INTO v_umbral_media  FROM PERFILES_PARAMETROS WHERE nombre = 'umbral_ica_media';
    SELECT valor INTO v_techo         FROM PERFILES_PARAMETROS WHERE nombre = 'techo_afinidad_alerta';
    SELECT valor INTO v_entrada_pct   FROM PERFILES_PARAMETROS WHERE nombre = 'entrada_pct';
    SELECT valor INTO v_esf_max       FROM PERFILES_PARAMETROS WHERE nombre = 'esfuerzo_maximo_pct';
    SELECT valor INTO v_tipo          FROM PERFILES_PARAMETROS WHERE nombre = 'tipo_interes_anual';
    SELECT valor INTO v_anios         FROM PERFILES_PARAMETROS WHERE nombre = 'anios_hipoteca';
    SELECT valor INTO v_financiacion  FROM PERFILES_PARAMETROS WHERE nombre = 'financiacion_pct';
    SELECT valor INTO v_u_aseq        FROM PERFILES_PARAMETROS WHERE nombre = 'umbral_asequible';
    SELECT valor INTO v_u_ajus        FROM PERFILES_PARAMETROS WHERE nombre = 'umbral_ajustado';
    SELECT valor INTO v_u_alto        FROM PERFILES_PARAMETROS WHERE nombre = 'umbral_alto';

    v_ingresos := NVL(p_ingresos, 2500);
    IF v_ingresos <= 0 THEN v_ingresos := 2500; END IF;
    v_m2 := NVL(p_m2, 90);
    IF v_m2 <= 0 THEN v_m2 := 90; END IF;
    v_tenencia := LOWER(NVL(p_tenencia, 'compra'));

    -- Cuota por euro prestado (sistema frances)
    v_factor := (v_tipo / 12) / (1 - POWER(1 + (v_tipo / 12), -1 * v_anios * 12));

    -- Precio maximo sostenible y presupuesto efectivo
    v_cuota_max := v_ingresos * (v_esf_max / 100);
    IF v_tenencia = 'compra' THEN
        v_precio_max := (v_cuota_max / v_factor) / v_financiacion / v_m2;
    ELSE
        v_precio_max := v_cuota_max / v_m2;
    END IF;
    v_presupuesto := LEAST(p_presupuesto_m2, v_precio_max);

    FOR r IN (
        SELECT * FROM (
            SELECT m.nombre,
                   m.codigo_ine,
                   m.comarca,
                   m.score_vivienda,
                   m.score_educacion,
                   m.score_conectividad,
                   m.score_sanidad,
                   m.hab_por_medico,
                   m.ocupacion_escolar_pct,
                   m.indice_capacidad_global,
                   m.factor_limitante,
                   m.precio_m2_compra,
                   m.precio_m2_alquiler,
                   m.precio_predicho_avm_m2,
                   m.gap_mercado_pct,
                   m.diagnostico_mercado,
                   (v_viv * m.score_vivienda
                    + v_edu * m.score_educacion
                    + v_con * m.score_conectividad
                    + v_san * m.score_sanidad) AS afinidad
              FROM municipios_procesados m
             WHERE (CASE WHEN v_tenencia = 'compra'
                         THEN m.precio_m2_compra
                         ELSE m.precio_m2_alquiler END) <= v_presupuesto
               AND m.tiempo_medio_madrid_minutos <= p_tiempo_max
        )
        ORDER BY CASE WHEN hab_por_medico > v_max_hab OR ocupacion_escolar_pct > v_max_ocup
                      THEN LEAST(afinidad, v_techo)
                      ELSE afinidad END DESC,
                 indice_capacidad_global DESC,
                 nombre
    ) LOOP
        -- Asequibilidad
        IF v_tenencia = 'compra' THEN
            v_precio := r.precio_m2_compra;
            v_cuota := v_precio * v_m2 * v_financiacion * v_factor;
            v_entrada := v_precio * v_m2 * v_entrada_pct;
        ELSE
            v_precio := r.precio_m2_alquiler;
            v_cuota := v_precio * v_m2;
            v_entrada := 0;
        END IF;
        v_esf := (v_cuota / v_ingresos) * 100;
        v_ing_nec := v_cuota / (v_esf_max / 100);

        IF v_esf <= v_u_aseq THEN v_etiqueta := 'Asequible';
        ELSIF v_esf <= v_u_ajus THEN v_etiqueta := 'Ajustado';
        ELSIF v_esf <= v_u_alto THEN v_etiqueta := 'Alto';
        ELSE v_etiqueta := 'No asequible'; END IF;

        -- Regla no compensatoria
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
            r.codigo_ine,
            r.comarca,
            ROUND(v_af, 2),
            ROUND(v_viv * r.score_vivienda, 2),
            ROUND(v_edu * r.score_educacion, 2),
            ROUND(v_con * r.score_conectividad, 2),
            ROUND(v_san * r.score_sanidad, 2),
            ROUND(v_ica, 2),
            v_semaforo,
            v_alerta,
            r.factor_limitante,
            ROUND(v_precio, 2),
            ROUND(v_cuota, 2),
            ROUND(v_entrada, 2),
            ROUND(v_ing_nec, 2),
            ROUND(v_precio_max, 2),
            ROUND(v_esf, 2),
            v_etiqueta,
            ROUND(r.precio_predicho_avm_m2, 2),
            ROUND(r.gap_mercado_pct, 2),
            r.diagnostico_mercado
        ));
    END LOOP;
    RETURN;
END;
/

-- ---------------------------------------------------------------------------
-- 7. Vista de apoyo para APEX (parametros por defecto)
-- ---------------------------------------------------------------------------
CREATE OR REPLACE VIEW v_ranking_ciudadano_demo AS
SELECT nombre, codigo_ine, comarca, afinidad, semaforo_ica, alerta_no_compensatoria,
       factor_limitante, indice_ica_ajustado, precio_m2, cuota_mensual_eur,
       entrada_eur, esfuerzo_pct, etiqueta_esfuerzo, gap_mercado_pct
  FROM TABLE(f_ranking_ciudadano(
           p_presupuesto_m2 => 2500,
           p_tiempo_max     => 90,
           p_hijos          => 0,
           p_edad           => 35,
           p_transporte     => 'publico',
           p_tenencia       => 'compra',
           p_ingresos       => 2500,
           p_m2             => 90
       ));

COMMENT ON TABLE PERFILES_AJUSTES IS
    'Reglas del perfil ciudadano. Replicadas desde src/lodcore/config/perfiles.py; test de sincronizacion obligatorio.';
COMMENT ON FUNCTION f_ranking_ciudadano IS
    'Ranking por perfil con asequibilidad. Equivalente a m5_recomendador/ranking.py y config/perfiles.py.';
