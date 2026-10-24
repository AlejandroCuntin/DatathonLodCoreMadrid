DECLARE
    v_fuera_de_rango NUMBER;
BEGIN
    -- Contar registros fuera del rango geográfico de la Comunidad de Madrid
    SELECT COUNT(*)
      INTO v_fuera_de_rango
      FROM MUNICIPIOS_PROCESADOS
     WHERE latitud NOT BETWEEN 39.88 AND 41.17 
        OR longitud NOT BETWEEN -4.58 AND -3.05
        OR latitud IS NULL
        OR longitud IS NULL;

    -- Si hay al menos uno defectuoso, lanzamos el error
    IF v_fuera_de_rango > 0 THEN
        RAISE_APPLICATION_ERROR(-20001, 
            'TEST FALLIDO: Se han encontrado ' || v_fuera_de_rango || ' registros con latitud/longitud fuera de baremo.');
    END IF;
END;
/