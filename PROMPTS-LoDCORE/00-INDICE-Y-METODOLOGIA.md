# LoDCORE — Sistema de prompts e investigación para el Datathon

> Búsqueda exhaustiva en Google/GitHub de los mejores prompts, repositorios y metodologías
> aplicables al proyecto **LoDCORE**: *Sistema Predictivo & Recomendador Explicable* para los
> municipios de la Comunidad de Madrid con **menos de 50.000 habitantes**.

---

## Contenido de esta carpeta

| Fichero | Qué contiene |
|---|---|
| `00-INDICE-Y-METODOLOGIA.md` | Este índice: qué se hizo, cómo se hizo, cómo usar los prompts |
| `01-ANALISIS-Y-ARQUITECTURA.md` | Análisis del proyecto, 8 riesgos críticos, arquitectura recomendada, plan por sprints, criterios de aceptación |
| `02-INVENTARIO-GITHUB.md` | **Catálogo de la investigación**: repos, librerías, papers y fuentes oficiales, con URL, estrellas y a qué modelo alimenta |
| `03-PROMPTS-OPERATIVOS.md` | Catálogo de los 14 prompts: cuándo usar cada uno, con qué variables, qué produce |
| `AGENTS.md` | Contexto operativo del repo para agentes de IA (Codex, Claude Code, Cursor, Copilot, Gemini CLI) |
| `.github/prompts/*.prompt.md` | **Los 14 prompts operativos**, listos para copiar y pegar o para instalar en `.github/prompts/` |
| `_assets/TEXTOS-EXTRAIDOS-DE-LOS-PDF.md` | Texto íntegro extraído de los 3 PDF del datathon (fuente de todo el análisis) |
| `_assets/p1_X6.png`, `p1_X8.png`, `p1_X9.png` | Capturas del prototipo de interfaz (mapa, comparador, escenarios) |

---

## Cómo usar este material

### Opción A — Un prompt cada vez (recomendada)
Copia el cuerpo del `.prompt.md` que necesites y pégalo en el chat del agente, sustituyendo las
variables `${input:...}`. Cada prompt es autónomo.

### Opción B — Instalar el kit completo en el repo
```bash
cp -r PROMPTS-LoDCORE/.github/prompts/ <TU_REPO>/.github/prompts/
cp PROMPTS-LoDCORE/AGENTS.md <TU_REPO>/AGENTS.md
```
En GitHub Copilot, los ficheros `.prompt.md` se invocan con `/nombre-del-fichero`.
En Codex / Claude Code / Cursor, `AGENTS.md` se carga automáticamente al abrir el repo.

### Opción C — Pipeline completo sin intervención
Encadena los prompts en este orden (dependencias reales, no arbitrarias):

```
01-ingesta-fuente-oficial      →  datos crudos con procedencia
   └─> 02-auditoria-calidad-y-procedencia
          └─> 03-auditoria-fuga-informacion
                 └─> 04-diseno-validacion-temporal-espacial
                        ├─> 05-modelo-avm-random-forest          (M1)
                        ├─> 06-modelo-indices-pca-isocronas      (M2)
                        │       └─> 07-modelo-proyeccion-demografica (M3)
                        │               └─> 08-modelo-capacidad-acogida-xgboost-shap (M4)
                        │                       └─> 09-cuellos-botilla-no-compensatorios
                        ├─> 10-recomendador-clustering-mcdm      (M5)
                        └─> 11-explicacion-shap-lenguaje-natural
                                └─> 12-publicacion-oracle-y-apex
                                        └─> 13-model-cards-e-informe-tecnico
                                                └─> 14-revision-adversarial-pipeline
```

---

## Los 5 prompts que, si solo pudieras usar 5, son estos

| # | Prompt | Por qué |
|---|---|---|
| 1 | **`09-cuellos-botilla-no-compensatorios`** | Es la tesis del proyecto. XGBoost es compensatorio: sin este prompt, el proyecto demuestra lo contrario de lo que afirma. |
| 2 | **`03-auditoria-fuga-informacion`** | Con 41 municipios, una fuga de información invalida todas las métricas. Unjurado lo detecta reentrenando con `GroupKFold`. |
| 3 | **`04-diseno-validacion-temporal-espacial`** | Sin validación temporal/espacial y bandas de 95 %, cualquier R² es ruido. |
| 4 | **`02-auditoria-calidad-y-procedencia`** | El requisito de distinguir OBSERVADO / IMPUTADO / PROYECTADO / SIMULADO es **explícito** en el PDF de diseño. Sin esto, no hay entregable. |
| 5 | **`14-revision-adversarial-pipeline`** | El control de calidad final. Ejecuta 12 ataques concretos antes de entregar. |

---

## Principios de diseño de los prompts (y por qué los prompts tienen esta forma)

Los prompts no son texto libre. Siguen una estructura derivada de dos fuentes:

**1. `github/awesome-copilot` → `instructions/prompt.instructions.md`** (el estándar oficial de
ficheros `.prompt.md`): frontmatter YAML con `description`, `agent`, `tools`, `argument-hint`;
cuerpo con *Mission → Scope & Preconditions → Inputs → Workflow → Output Expectations →
Quality Assurance*; *inputs* con placeholders `${input:x}`; *tools* con mínimo privilegio;
*output* con formato exacto; y checklist de QA final.

**2. `ai-boost/awesome-prompts` → `data_analysis.txt`, `data_analyst.txt`,
`ml_systems_architect.txt`, `MLOps_Engineer.txt`, `Data_Governance_Architect.txt`,
`diagnose.txt`, `verification_specialist.txt`, `doubt_driven_development.txt`** (361 prompts
listos para usar): el patrón
*Rol → Contexto → Proceso por fases → Estructura de salida → Estándares de calidad*.

| Decisión de diseño | Justificación |
|---|---|
| **Contexto de dominio explícito** en cada prompt (umbrales, n=41, cadena M1→M5) | Un prompt genérico produce un modelo genérico. El LLM no sabe lo de tu datathon. |
| **Fases numeradas con entregable por fase** | Evita que el agente se salte pasos. |
| **"Obligatorio" explícito** para baselines, bandas, validación y provenance | Lo que no se exige, no se hace. |
| **Formato de salida con plantilla literal** | Permite diff entre ejecuciones y automatizar el informe. |
| **Checklist de QA como criterio de terminación** | Convierte "listo" en algo verificable. |
| **Prohibiciones explícitas** (no CV aleatorio, no leakage, no umbrales duplicados) | Un LLM optimiza el checklist visible; si no lo pones, lo salta. |
| **Semasforización (BLOQUEANTE / MATERIAL / MENOR)** | Unjurado necesita saber qué rompe el proyecto y qué no. |
| **Sección de "puntos fuertes"** en la revisión adversarial | Una revisión solo negativa no genera confianza ni se usa. |
| **Prompts de ataque, no de confirmación** | `doubt_driven_development`: "Una respuesta segura no es una respuesta correcta". |

### Frameworks de prompt incluidos dentro de los prompts

| Framework | Dónde | Qué aporta |
|---|---|---|
| **COSTAR** (Contexto, Objetivo, Estilo, Tono, Audience, Response) | Todos | Estructura base del bloque *Mission + Scope + Inputs + Output + QA* |
| **RTF** (Role, Task, Format) | Todos | Rol explícito + tarea + formato de salida literal |
| **CRISPE** (Capacity/Role, Insight, Statement, Personality, Experiment) | 05, 08, 10 | Capacidad (algoritmos que puede usar) + Statement (restricciones de dominio) |
| **Cadena de *context gap*** (`markoniga/llm-prompts-for-dse`) | 01, 06, 12 | Antes de generar código, el agente debe **declarar qué contexto le falta** y parar si es crítico |
| **Doubt cycle** (CLAIM → EXTRACT → DOUBT → RECONCILE → STOP) | 03, 08, 14 | Cada decisión no trivial se somete a revisión adversarial antes de consolidarse |
| **Verification loop** (`verification_specialist.txt`) | 03, 14 | El agente debe **ejecutar** la comprobación, no decir que funcionó |
| **Diagrama de flujo de dependencias** (`llm-prompts-for-dse`) | 03, 08, 12 | Los datos fluyen en cascada; cada fase declara su entrada y su salida |

---

## Anti-patrones evitados (y por qué)

| Anti-patrón | Por qué se ha evitado |
|---|---|
| "Escribe un modelo de ML" | Sin dataset, sin target y sin protocolo, produce código decorativo. |
| "Optimiza el modelo" | Sin protocolo de validación, "optimizar" es sobreajustar al test. |
| "Haz un EDA" | Sin preguntas de negocio, produce un informe que nadie usa. |
| "Explícame este SHAP" | Sin plantilla y sin test de trazabilidad, produce texto plausible pero falso. |
| "Genera la documentación" | Sin *cross-check* de números contra los artefactos, produce documentación que miente. |
| Poner umbrales en varios sitios | Divergen. Todos los umbrales van en `thresholds.py`. |
| Un único prompt gigante | Se degrada: el modelo optimiza la sección más larga. 14 prompts cortos funcionan mejor. |

---

## Nota sobre reproducibilidad de esta investigación

- **Búsqueda**: Google (integración web) + API de GitHub (`api.github.com/search/repositories`
  y `repos/*/contents`) + lectura directa de repos vía `raw.githubusercontent.com`.
- **Limitación encontrada**: la API de GitHub sin token está limitada a **10 peticiones/minuto**
  y **60/hora** por IP, y este entorno comparte IP. Las búsquedas por *tema* (`topic:gtfs`,
  `topic:oracle-apex`, …) funcionaron; las búsquedas por frase larga devolvieron 0 resultados
  porque GitHub hace AND de todos los términos. **Recomendación**: si vas a repetir esta
  investigación, usa un `GITHUB_TOKEN` (aumenta los límites a 30/min y 5000/hora).
- Los recursos de mayor valor se han **verificado** (contenido de `README`/fichero raw leído),
  no solo por título.
