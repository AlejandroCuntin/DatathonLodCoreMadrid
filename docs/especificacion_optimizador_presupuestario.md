# Especificación Técnica: Asignación Presupuestaria por Comarca (M4-OPT)
> **Rol responsable**: P1 (Datos + Reglas de negocio + Optimizador M4)  
> **Fecha**: 24 de octubre de 2026  
> **Naturaleza del Módulo**: Heurística Voraz Acotada Determinista (MVP Fase 1)  
> **Roadmap Fase 2**: Difusión territorial continua (Spillover por matrices origen-destino)

---

## 1. Contexto Operativo y Alcance Honesto
El simulador What-If evalúa el impacto de inversiones municipales aisladas. Los gestores públicos de la Comunidad de Madrid y los consorcios comarcales disponen de partidas presupuestarias cerradas (ej. 1 M€, 2 M€, 5 M€) y requieren una herramienta para responder:
> *¿En qué municipios de una comarca conviene asignar la dotación médica y educativa para maximizar el incremento neto en capacidad de acogida efectiva sin provocar saturaciones?*

Para la Fase 1, se implementa una **heurística voraz acotada (Greedy) con poda de ineficiencia residencial**, determinista y auditable.  
El efecto *spillover continuo mediante matrices de movilidad origen-destino y gravedad territorial* se declara con honestidad metodológica como **Roadmap Fase 2**.

---

## 2. Formulación Matemática de la Heurística

### 2.1 Parámetros y Entradas
- **Comarca**: $C \in \{\text{Sierra Oeste}, \text{Sierra Norte}, \text{Las Vegas}, \dots\}$.
- **Municipios Candidatos**: Conjunto de municipios de la comarca $M_C = \{m_1, m_2, \dots, m_k\}$.
- **Presupuesto Disponible**: $B \in \mathbb{R}^+$ (euros).
- **Costes Unitarios de CAPEX**:
  - $C_{\text{med}} = 450.000\text{ €}$ por médico de Atención Primaria (módulo de consulta).
  - $C_{\text{esc}} = 12.000\text{ €}$ por plaza escolar pública (CEIP / IES).

### 2.2 Variables de Asignación Discreta
Para cada municipio $i \in M_C$:
- $x_i \in \mathbb{N}_0$: Médicos de AP asignados.
- $y_i \in \mathbb{N}_0$: Plazas escolares asignadas.

### 2.3 Regla de Capacidad Efectiva y Poda de Ineficiencia Residencial
La acogida neta efectiva de un municipio viene regida por el principio del mínimo de Liebig:
$$\text{AcogidaEfectiva}_i(x_i, y_i) = \min \left( \text{abs\_sanidad}_i(x_i), \, \text{abs\_educacion}_i(y_i), \, \text{abs\_vivienda}_i \right)$$

donde:
- $\text{abs\_sanidad}_i(x_i) = \max \left( 0, \, (\text{medicos}_i + x_i) \cdot 1.500 - \text{poblacion}_i \right)$
- $\text{abs\_educacion}_i(y_i) = \max \left( 0, \, \frac{(\text{plazas}_i + y_i) \cdot 0.95 - \text{alumnos}_i}{0.17} \right)$
- $\text{abs\_vivienda}_i = \text{capacidad habitacional fija en suelo y vivienda vacía}$

$$\Delta \text{Personas}_i(x_i, y_i) = \max \left( 0, \, \text{AcogidaEfectiva}_i(x_i, y_i) - \text{AcogidaBase}_i \right)$$

**Condición de Poda**:  
Si un municipio está saturado por vivienda ($\text{factor\_limitante} == \text{"VIVIENDA"}$ y $\text{abs\_vivienda} \le \text{AcogidaBase}$), $\Delta \text{Personas}_i = 0$. El algoritmo **NO asigna presupuesto sanitario ni educativo** a dicho municipio, evitando gastos ineficientes (ej. caso Comarca Sur / Navalcarnero).

### 2.4 Criterio Voraz de Selección
Los municipios con ganancia neta factible se priorizan por **eficiencia marginal**:
$$e_i = \frac{\Delta \text{Personas}_i}{\text{CosteTotal}_i}$$
Se asignan partidas en orden decreciente de $e_i$ mientras $\sum \text{Coste}_i \le B$.

---

## 3. Contrato JSON Devuelto (FastAPI / APEX)

```json
{
  "comarca": "Sierra Oeste",
  "presupuesto_total_eur": 2000000.0,
  "presupuesto_utilizado_eur": 1650000.0,
  "remanente_eur": 350000.0,
  "incremento_acogida_comarcal": 1336,
  "municipios_evaluados": 3,
  "asignaciones": [
    {
      "codigo_ine": "28171",
      "municipio": "Villa del Prado",
      "comarca": "Sierra Oeste",
      "medicos_asignados": 1,
      "plazas_escolares_asignadas": 0,
      "coste_eur": 450000.0,
      "ganancia_personas": 830,
      "nuevo_ica": 37.57,
      "semaforo": "BAJA",
      "motivo_asignacion": "Resolución de cuello de botella en SANIDAD y absorción de hasta 830 residentes"
    }
  ],
  "metodologia": "Heurística voraz acotada por comarca con poda de ineficiencia residencial (MVP determinista)",
  "origen": "SIMULADO",
  "metodo": "HEURISTICA_VORAZ_PRESUPUESTO_COMARCAL",
  "dataset_version": "v1.0.0-F2",
  "roadmap_fase_2": "Spillover territorial continuo mediante matriz de accesibilidad intermunicipal."
}
```
