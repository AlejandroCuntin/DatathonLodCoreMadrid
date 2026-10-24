# Plantillas de Explicabilidad Auditada en Lenguaje Natural (Español de España)
## Proyecto LoDCORE Madrid • Explicabilidad sin Causalidad

### Regla Estricta de Redacción
Las contribuciones marginales del modelo describen su comportamiento funcional estadístico, **nunca** una relación causal en la realidad física.
- **Términos prohibidos**: *causa*, *provoca*, *produce*, *genera*, *origina*, *determina causalmente*.
- **Términos permitidos**: *el modelo asocia*, *presenta una contribución marginal*, *se correlaciona en la estimación con*, *pondera positivamente/negativamente*.

### Plantillas Oficiales
1. **Resumen Principal**:
   > En la evaluación estadística de **{municipio}**, el modelo estima un índice de **{score_predicho}** puntos (banda de incertidumbre al 95 %: [{ic_inf}, {ic_sup}]) frente al valor base regional de **{base_value}**.

2. **Factores Asociados Positivamente**:
   > El modelo asocia una mayor puntuación con **{feature_top_pos}** (valor observado: {val_top_pos}, aportación marginal: +{shap_top_pos} puntos).

3. **Factores Asociados Negativamente (Cuello de Botella)**:
   > En sentido opuesto, el modelo asocia una menor puntuación con **{feature_top_neg}** (valor observado: {val_top_neg}, aportación marginal: {shap_top_neg} puntos).

4. **Advertencia No-Compensatoria (si aplica)**:
   > Se activa la cláusula de límite duro no compensatorio debido a **{motivo_colapso}**, restringiendo el nivel del semáforo ICA a **BAJA** con independencia del resto de contribuciones marginales.
