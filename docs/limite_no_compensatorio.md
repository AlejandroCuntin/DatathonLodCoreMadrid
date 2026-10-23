# Reglas Duras de No-Compensatoriedad y Semáforo ICA
## Proyecto LoDCORE Madrid • II Datathon 2026

---

### 1. Justificación de la Hipótesis Central
En la planificación territorial de servicios esenciales (sanidad, educación y habitabilidad básica), **las carencias severas no son compensables**. 

Un municipio no puede ser calificado con alta capacidad de acogida si sus consultorios médicos o sus escuelas públicas están al borde del colapso asistencial, por muy bajo que sea el precio de su suelo o por muy elevado que sea su superávit presupuestario.

### 2. Umbrales Duros de Activación de Colapso

| Factor Crítico | Métrica Operativa | Umbral de Alerta | Fuente Normativa | Acción No Compensatoria |
|---|---|---|---|---|
| **Sanidad de Atención Primaria** | Habitantes por Médico AP | **> 1.500 hab/médico** | SERMAS / Criterios OMS | Techo ICA fijado en **39.0** (Alerta Baja) |
| **Educación Obligatoria** | Tasa de Ocupación Escolar | **> 95.0 %** | Consejería de Educación CAM | Techo ICA fijado en **39.0** (Alerta Baja) |
| **Vivienda Asequible** | Tasa de Esfuerzo Familiar | **> 40.0 % de la renta** | Banco de España / INE | Techo ICA fijado en **45.0** (Alerta Media) |

### 3. Semáforo ICA (Índice de Capacidad de Acogida)

- **🟢 Alta Capacidad (ICA ≥ 60.0)**: Municipio en zona de confort dotacional. Posee holgura escolar (<80% ocupación) y cobertura sanitaria adecuada para recibir nuevos residentes de forma inmediata.
- **🟡 Capacidad Media (40.0 ≤ ICA < 60.0)**: Municipio equilibrado pero próximo a umbrales de saturación. Requiere planificación y partidas presupuestarias moderadas antes de acoger contingentes superiores.
- **🔴 Alerta de Saturación (ICA < 40.0)**: Municipio en cuello de botella crítico o penalizado por regla no compensatoria. Exige inversión previa obligatoria (CAPEX) en ampliación de aulas o contratación de facultativos médicos.

### 4. Implementación en Pipeline
La regla se materializa en el módulo:
`src/lodcore/models/m4_capacidad/reglas_no_compensatorias.py`
y se refleja de forma idéntica en las vistas de Oracle APEX:
`oracle/ddl/03-vistas_apex.sql`
