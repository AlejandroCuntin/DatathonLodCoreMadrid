CREATE OR REPLACE VIEW V_MAPA_MUNICIPIOS AS
SELECT
    m.id_municipio,
    m.codigo_ine,
    m.nombre,
    m.comarca,
    m.tipologia,
    m.latitud,
    m.longitud,
    m.poblacion_actual,
    m.precio_m2_compra,
    m.score_conectividad,
    m.score_servicios,
    m.indice_capacidad_global,
    INITCAP(m.nivel_idoneidad)               AS nivel_idoneidad,
    m.personas_absorbibles_sin_colapso,
    CASE UPPER(TRIM(m.factor_limitante))
         WHEN 'SANIDAD'   THEN 'Sanidad'
         WHEN 'EDUCACION' THEN 'Educación'
         WHEN 'EDUCACIÓN' THEN 'Educación'
         WHEN 'VIVIENDA'  THEN 'Vivienda'
         ELSE m.factor_limitante
    END                                      AS factor_limitante,
    CASE UPPER(TRIM(m.factor_limitante))
         WHEN 'SANIDAD'   THEN m.sanidad_detalle
         WHEN 'EDUCACION' THEN m.educacion_detalle
         WHEN 'EDUCACIÓN' THEN m.educacion_detalle
         WHEN 'VIVIENDA'  THEN m.vivienda_detalle
    END                                      AS detalle_limitante,
    m.tiempo_medio_madrid_minutos,
    m.hab_por_medico,
    m.ocupacion_escolar_pct,
    m.cobertura_fibra_pct,
    m.restriccion_ambiental,
    m.patrimonio_entorno,
    m.observaciones_acogida,
    m.alerta_planificacion,
    m.origen,
    m.metodo,
    m.dataset_version
FROM municipios_procesados m
WHERE m.latitud  IS NOT NULL
  AND m.longitud IS NOT NULL
  -- AND m.poblacion_actual < 50000   -- descomentar si la tabla incluye municipios mayores
WITH READ ONLY;