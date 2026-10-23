# Metrología: Definición Operativa de la Capacidad de Acogida (M4)
## Proyecto LoDCORE Madrid • II Datathon 2026

---

### 1. Definición Formal de la Capacidad de Acogida Neta ($C_{neta}$)

La **Capacidad de Acogida Neta** de un municipio representa el número máximo de nuevos residentes permanentes que el municipio puede absorber sin requerir la construcción inmediata de nuevas infraestructuras públicas ni provocar el colapso de los ratios de calidad de servicio vigentes en la Comunidad de Madrid.

Matemáticamente, se define como el valor mínimo (*cuello de botella de Liebig*) entre los vectores de absorción sectoriales:

$$C_{neta} = \min \left( C_{sanidad}, C_{educacion}, C_{vivienda} \right)$$

Donde:

1. **Capacidad Sanitaria ($C_{sanidad}$):**
   $$C_{sanidad} = \max \left( 0, \, \left( N_{medicos} \times 1.500 \right) - P_{actual} \right)$$
   Basada en el umbral crítico de saturación de 1.500 habitantes por médico de
   Atención Primaria (`MAX_HABITANTES_POR_MEDICO_AP`).

2. **Capacidad Educativa ($C_{educacion}$):**
   $$C_{educacion} = \frac{\max \left( 0, \, Plazas_{escolares} \times 0.95 - Alumnos_{actuales} \right)}{0.17}$$
   Asumiendo que la población escolar (3 a 16 años) representa aproximadamente el
   17% del contingente entrante y respetando un techo de ocupación máxima del 95%.

3. **Capacidad Habitacional ($C_{vivienda}$):**
   $$C_{vivienda} = 0.75 \cdot Viviendas_{vacias} + 0.00375 \cdot Suelo_{urbano\_disponible\_m2}$$
   Calibración vigente del panel F2 (reproduce `personas_absorb_vivienda`).
   La versión anterior de este documento usaba 60% de movilización y 2,4 hab/hogar;
   esos coeficientes **no** son los que genera el dataset actual.

---

### 2. Índice Global de Capacidad de Acogida (ICA)

El **Índice ICA** es una magnitud normalizada en escala 0–100 que pondera la robustez integral del territorio mediante 4 componentes construidos a partir de 5 sub-índices normalizados (`score_sanidad`, `score_educacion`, `score_conectividad`, `score_vivienda` y `score_holgura`). M2 calcula además una síntesis PCA por bloque (`subindice_*`) con fines de auditoría; no sustituye a los sub-índices del panel F2 que alimentan el ICA.

$$ICA = 0.30 \cdot S_{vivienda} + 0.30 \cdot \frac{S_{sanidad}+S_{educacion}}{2} + 0.25 \cdot S_{conectividad} + 0.15 \cdot S_{holgura}$$

*Sujeto a la cláusula de salvaguarda no compensatoria:*
Si $\frac{P_{actual}}{N_{medicos}} > 1.500$ o $\frac{Alumnos}{Plazas} > 0.95$, entonces $ICA \leftarrow \min(ICA, 39.0)$.
