# Metrología: Definición Operativa de la Capacidad de Acogida (M4)
## Proyecto LoDCORE Madrid • II Datathon 2026

---

### 1. Definición Formal de la Capacidad de Acogida Neta ($C_{neta}$)

La **Capacidad de Acogida Neta** de un municipio representa el número máximo de nuevos residentes permanentes que el municipio puede absorber sin requerir la construcción inmediata de nuevas infraestructuras públicas ni provocar el colapso de los ratios de calidad de servicio vigentes en la Comunidad de Madrid.

Matemáticamente, se define como el valor mínimo (*cuello de botella de Liebig*) entre los vectores de absorción sectoriales:

$$C_{neta} = \min \left( C_{sanidad}, C_{educacion}, C_{vivienda} \right)$$

Donde:

1. **Capacidad Sanitaria ($C_{sanidad}$):**
   $$C_{sanidad} = \max \left( 0, \, \left( N_{medicos} \times 1.250 \right) - P_{actual} \right)$$
   Basada en el ratio óptimo del Servicio Madrileño de Salud (SERMAS) de 1 médico de familia/pediatra por cada 1.250 habitantes.

2. **Capacidad Educativa ($C_{educacion}$):**
   $$C_{educacion} = \frac{\max \left( 0, \, Plazas_{escolares} \times 0.95 - Alumnos_{actuales} \right)}{0.16}$$
   Asumiendo que la población escolar (3 a 16 años) representa aproximadamente el 16% del contingente demográfico entrante y respetando un techo de ocupación máxima del 95%.

3. **Capacidad Habitacional ($C_{vivienda}$):**
   $$C_{vivienda} = \left( Viviendas_{vacias} \times 0.60 \times 2.4 \right) + \left( \frac{Suelo_{urbano\_vacante}}{120} \times 2.4 \right)$$
   Considera la movilización del 60% del parque de vivienda desocupada/secundaria censada y el aprovechamiento de suelo urbano no consolidado disponible (a razón de 120 m² de suelo por vivienda y 2.4 habitantes por hogar, ratio medio INE).

---

### 2. Índice Global de Capacidad de Acogida (ICA)

El **Índice ICA** es una magnitud normalizada en escala 0–100 que pondera la robustez integral del territorio mediante 4 sub-índices construidos con análisis de componentes principales (PCA) y escalado MinMaxScaler:

$$ICA = 0.35 \cdot S_{sanidad\_educacion} + 0.25 \cdot S_{conectividad} + 0.25 \cdot S_{vivienda\_asequibilidad} + 0.15 \cdot S_{sostenibilidad\_presupuestos}$$

*Sujeto a la cláusula de salvaguarda no compensatoria:*
Si $\frac{P_{actual}}{N_{medicos}} > 1.500$ o $\frac{Alumnos}{Plazas} > 0.95$, entonces $ICA \leftarrow \min(ICA, 39.0)$.
