# Especificación Técnica: Asignación Presupuestaria Óptima por Comarca (M4-OPT)
> **Rol responsable**: P1 (Datos + Reglas de negocio + Optimizador M4)  
> **Fecha**: 23 de octubre de 2026  
> **Estado**: IMPLEMENTACIÓN DETERMINISTA MVP (Sin alegar spillover continuo)

---

## 1. Contexto y Decisión de Diseño
El simulador What-If actual evalúa el impacto de inversiones aisladas por municipio, pero los gestores públicos de la Comunidad de Madrid y los consorcios comarcales disponen de una **partida presupuestaria agregada** (ej. 1 M€, 3 M€, 5 M€) y necesitan responder:
> *¿En qué municipio(s) exacto(s) de la comarca debemos asignar este presupuesto para maximizar el incremento neto de acogida sin provocar colapsos?*

Se implementa un **algoritmo de optimización determinista (Knapsack / Greedy acotado)** sobre los municipios candidatos de la comarca.  
El efecto "spillover geográfico continuo con matriz origen-destino y gravedad espacial" se declara con honestidad metodológica en el **Roadmap Fase 2**.

---

## 2. Definición Matemática del Problema

### 2.1 Variables de Entrada y Candidatos
- **Comarca objetivo**: $C \in \{\text{Sierra Norte}, \text{Sierra Oeste}, \text{Las Vegas}, \dots\}$.
- **Municipios candidatos**: Conjunto de municipios pertenecientes a la comarca $M_C = \{m_1, m_2, \dots, m_k\}$.
- **Presupuesto comarcal disponible**: $B \in \mathbb{R}^+$ (euros).
- **Costes paramétricos unitarios de CAPEX**:
  - Coste por dotación médica AP: $C_{\text{med}} = 450.000\text{ €}$ (médico + módulo de consulta).
  - Coste por dotación escolar: $C_{\text{esc}} = 12.000\text{ €}$ (plaza escolar en CEIP/IES).

### 2.2 Variables de Decisión
Para cada municipio $i \in M_C$:
- $x_i \in \mathbb{N}_0$: número de médicos de AP adicionales asignados.
- $y_i \in \mathbb{N}_0$: número de plazas escolares adicionales creadas.

### 2.3 Función Objetivo
Maximizar la ganancia neta en capacidad de acogida poblacional efectiva en toda la comarca:
$$\max_{\{x_i, y_i\}} \sum_{i \in M_C} \Delta \text{PersonasAcogibles}_i(x_i, y_i)$$

donde $\Delta \text{PersonasAcogibles}_i(x_i, y_i) = \text{AcogidaEfectiva}_i(x_i, y_i) - \text{AcogidaBase}_i$.

### 2.4 Restricciones Obligatorias
1. **Restricción presupuestaria dura**:
   $$\sum_{i \in M_C} \left( C_{\text{med}} \cdot x_i + C_{\text{esc}} \cdot y_i \right) \le B$$

2. **Resolución de Cuello de Botella (Principio de No Compensatoriedad)**:
   - Si el municipio $i$ tiene cuello de botella en **Sanidad** ($\text{hab/médico} > 1.500$), la inversión debe priorizar $x_i$ hasta situar el ratio en zona segura ($\le 1.500$). Invertir en educación o vivienda sin resolver la sanidad produce $\Delta = 0$ debido al truncamiento a BAJA ($<40$).
   - Si el cuello de botella es **Educación** ($\text{ocupación} > 95\%$), debe priorizarse $y_i$ hasta devolver la ocupación por debajo del $95\%$.

3. **Techo de absorción residencial**:
   $$\text{PersonasAcogibles}_i(x_i, y_i) \le \text{CapacidadResidencial}_i$$
   No tiene sentido sobredotar servicios si no hay vivienda vacía movilizable o suelo vacante disponible.

4. **No negatividad e integralidad**:
   $$x_i \in \mathbb{N}_0, \quad y_i \in \mathbb{N}_0, \quad \forall i \in M_C$$

---

## 3. Algoritmo de Resolución
Dado que el espacio de búsqueda por comarca es pequeño ($k \le 7$ municipios por comarca, $n=20$ total), el algoritmo:
1. Identifica el cuello de botella limitante de cada municipio mediante `factor_limitante`.
2. Calcula la eficiencia marginal por euro invertido:
   $$e_i = \frac{\Delta \text{PersonasAcogibles}_i}{\text{CosteTotal}_i}$$
3. Asigna de forma voraz y exhaustiva (Knapsack exacto por programación dinámica / branch-and-bound) las combinaciones factibles respetando el presupuesto $B$.
4. Aplica la salvaguarda de no compensatoriedad (`aplicar_salvaguarda_no_compensatoria`).

---

## 4. Salida Producida (Contrato para APEX y API FastAPI)
```json
{
  "comarca": "Sierra Oeste",
  "presupuesto_total_eur": 2000000.0,
  "presupuesto_utilizado_eur": 1824000.0,
  "remanente_eur": 176000.0,
  "incremento_acogida_comarcal": 1634,
  "asignaciones": [
    {
      "codigo_ine": "28125",
      "municipio": "Robledo de Chavela",
      "medicos_asignados": 1,
      "plazas_escolares_asignadas": 41,
      "coste_eur": 942000.0,
      "ganancia_personas": 817,
      "nuevo_ica": 72.15,
      "semaforo": "ALTA"
    }
  ],
  "roadmap_fase_2": "Spillover territorial continuo mediante matriz de accesibilidad intermunicipal."
}
```
