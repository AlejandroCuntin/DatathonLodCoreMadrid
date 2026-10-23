"""
thresholds.py - Única fuente de verdad de umbrales operativos para LoDCORE Madrid.
Regla AGENTS.md: ningún umbral debe estar hardcodeado en los modelos o en la UI.
"""

# Umbrales de saturación sanitaria (SERMAS / OMS)
MAX_HABITANTES_POR_MEDICO_AP = 1500     # Ratio crítico de saturación asistencial
MEDICOS_AP_OBJETIVO_POR_1000 = 0.8       # 1 médico cada 1.250 hab. (óptimo SERMAS)

# Umbrales de saturación educativa (Consejería de Educación CAM)
MAX_OCUPACION_ESCOLAR_PCT = 95.0         # Por encima de 95%, el centro se considera colapsado
RATIO_ALUMNOS_POR_AULA = 25              # Ratio estándar por unidad de Infantil/Primaria

# Umbrales del Semáforo ICA (Índice de Capacidad de Acogida)
UMBRAL_ICA_BAJA = 40.0                   # < 40.0: Capacidad Baja / Cuello de Botella Severo
UMBRAL_ICA_MEDIA = 60.0                  # 40.0 - 59.9: Capacidad Media / Requiere Inversión
                                         # >= 60.0: Capacidad Alta / Zona de Confort

# Criterio Municipio de 30 minutos (Movilidad y Transporte)
TIEMPO_MAXIMO_POLO_EMPLEO_MIN = 30       # Isócrona de acceso a hospitales o nodos metropolitanos

# Escenarios de estrés demográfico (Modelo M3)
ESCENARIO_ESTRES_MODERADO_PCT = 5.0      # +5% de población proyectada
ESCENARIO_ESTRES_SEVERO_PCT = 10.0       # +10% de población proyectada

# Módulos de costes de inversión dotacional (CAPEX estándar Comunidad de Madrid)
COSTE_UNITARIO_PLAZA_ESCOLAR_EUR = 2400.0   # Coste por módulo escolar ampliado
COSTE_AMPLIACION_CONSULTA_MEDICA_EUR = 120000.0 # Coste módulo de consulta AP y equipamiento
