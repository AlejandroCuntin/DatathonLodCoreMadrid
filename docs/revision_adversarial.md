# Revisión Adversarial del Pipeline — F14
## II Datathon LoDCOREMadrid 2026 · `v1.0.0-F2`

> **Qué es:** los 12 ataques que un evaluador externo haría al proyecto, con la evidencia
> disponible y el veredicto honesto. **Regla:** si no hay evidencia en un artefacto, se dice
> “no calculado” o “parcial”; no se inventa.
> **Fecha:** 24 de octubre de 2026. **Alcance:** piloto de 20 municipios y 8 comarcas.

---

## Resumen de veredictos

| # | Ataque | Veredicto | Riesgo residual |
|---|---|---|---|
| A1 | Consistencia pipeline/publicado | **APTO** | Bajo |
| A2 | Tautología del ICA | **PARCIAL** | Medio (interpretativo) |
| A3 | No-compensatoriedad | **APTO** | Bajo |
| A4 | Caducidad de las fuentes | **APTO CON RESERVAS** | Medio |
| A5 | Backtest temporal | **PARCIAL** | Alto (no hay serie) |
| A6 | Municipios excluidos / sesgo | **PARCIAL** | Medio |
| A7 | Escala relativa vs absoluta | **PARCIAL** | Medio |
| A8 | Credibilidad del what-if | **PARCIAL** | Medio |
| A9 | Reproducibilidad real | **APTO** | Bajo |
| A10 | Correspondencia de municipios | **APTO** | Bajo |
| A11 | Trazabilidad de la narrativa | **APTO (código) / PARCIAL (APEX)** | Bajo |
| A12 | Cumplimiento de claims del PDF | **PARCIAL** | Medio |

**Puntos fuertes:** datos oficiales fechados, 20/20 por código INE, 36 tests, reglas duras
verificadas, pipeline reproducible, dataset y checksums entregables, límites declarados.

---

## A1 — Consistencia pipeline/publicado

**Ataque:** “los números del informe no salen del pipeline”.
**Evidencia:** `python scripts/run_all_models_n1_n2_n3.py` regenera panel, métricas y ONNX;
`pytest` (36 tests); `scripts/check_model_cards.py` cruza las cifras de las fichas con
`metrics.json`; `docs/validacion.md` cita la clave exacta de cada métrica.
**Respuesta:** los números publicados tienen artefacto y clave. El único campo que cambia
entre ejecuciones es `fecha_calculo` (timestamp real), declarado.
**Veredicto:** **APTO.**

## A2 — Tautología del ICA

**Ataque:** “el R² de M4 es alto porque el target es una fórmula de las features”.
**Evidencia:** el ICA es `0,30·vivienda + 0,30·(sanidad+educación)/2 + 0,25·conectividad +
0,15·holgura`; `FEATURES_M4` contiene 4 de esos 5 componentes. R² in-sample = 1,0;
R² OOF = 0,7345. Añadir el target sube el OOF a 0,9218; añadir `nivel_idoneidad`+`ranking_ica`,
a 0,9178. Ridge (lineal) obtiene 0,9264.
**Respuesta:** no es un modelo predictivo: es un **modelo de scoring** que aproxima una fórmula
y aplica reglas. Se publica como tal en `docs/model_cards.md` y `docs/validacion.md`.
**Veredicto:** **PARCIAL** (aceptado y declarado; no se vende como predicción).

## A3 — No-compensatoriedad

**Ataque:** “el ICA compensa un servicio colapsado con vivienda barata”.
**Evidencia:** 10 municipios superan 1.500 hab/médico o 95 % de ocupación; **0 de ellos tienen
ICA ≥ 40**. `tests/unit/test_models.py` verifica el truncamiento a BAJA.
**Respuesta:** la regla dura se aplica y está testeada.
**Veredicto:** **APTO.**

## A4 — Caducidad de las fuentes

**Ataque:** “los datos están obsoletos o no se sabe de cuándo son”.
**Evidencia:** snapshots del **24-10-2026**; INE padrón 2025; CKAN sanidad último año 2024
(metadatos modificados 06-08-2026); CKAN educación (metadatos 05-05-2026). Fechas en
`data/raw/` y en `docs/fuentes_oficiales.md`.
**Respuesta:** cada fuente tiene fecha y snapshot; no hay serie histórica, así que la
“caducidad” se declara, no se resuelve.
**Veredicto:** **APTO CON RESERVAS.**

## A5 — Backtest temporal

**Ataque:** “no pueden demostrar que el modelo funcione en el tiempo”.
**Evidencia:** el panel es un corte transversal único (`fecha_disponible = 2026-10-24`); no hay
dimensión anual. F4 sustituye el split temporal por `GroupKFold` espacial + bootstrap; se declara.
**Respuesta:** no se afirma generalización temporal. Es una limitación estructural, no un fallo
oculto.
**Veredicto:** **PARCIAL** (limitación declarada).

## A6 — Municipios excluidos / sesgo de selección

**Ataque:** “han elegido los municipios que les convenían”.
**Evidencia:** 20 de 155 municipios <50k (12,9 %); mediana del piloto 8.219 hab. frente a 2.964
del universo; 14/20 en 5–20k frente a 46/155; 4/20 <5k frente a 96/155.
**Respuesta:** no es *survivorship* (no se excluyó por falta de datos), pero **sí hay sesgo de
selección** hacia municipios medianos. Se declara; la ampliación estratificada es la siguiente fase.
**Veredicto:** **PARCIAL.**

## A7 — Escala relativa vs absoluta

**Ataque:** “un 100 en el índice no significa capacidad absoluta”.
**Evidencia:** PCA + MinMax sobre 20 municipios; el 100 es el máximo de la muestra. M2 se usa
como auditoría; el ICA se calcula con la fórmula y las reglas.
**Respuesta:** los subíndices son relativos a la muestra; no son comparables con municipios
fuera del panel. Declarado en `docs/model_cards.md` (M2).
**Veredicto:** **PARCIAL.**

## A8 — Credibilidad del what-if

**Ataque:** “el simulador inventa el impacto de una inversión”.
**Evidencia:** el what-if usa sensibilidades lineales (`0,05` puntos por hab/médico recuperado,
`0,85` por % de ocupación, `2,5` puntos por 250.000 € de conectividad) y `2,4` hab/hogar para
consumo de vivienda. No es un modelo causal; es una simulación determinista.
**Respuesta:** se presenta como **simulación**, no como predicción causal; las sensibilidades
están en `thresholds.py` y el resultado lleva `origen=SIMULADO`.
**Veredicto:** **PARCIAL** (declarado).

## A9 — Reproducibilidad real

**Ataque:** “no se puede reproducir”.
**Evidencia:** `python scripts/run_all_models_n1_n2_n3.py` + `pytest` (36 tests); semillas fijas;
`requirements.txt`; `dvc.yaml`; snapshots inmutables; `scripts/audit_f3_leakage.py` y
`scripts/check_model_cards.py` reproducen las cifras. `fecha_calculo` cambia, declarado.
**Respuesta:** reproducible en un entorno con las dependencias; el dataset y el ZIP llevan checksums.
**Veredicto:** **APTO.**

## A10 — Correspondencia de municipios

**Ataque:** “han cruzado por nombre y han mezclado municipios”.
**Evidencia:** cruce por `codigo_ine` de 5 dígitos; 20/20; 0 duplicados; nombres solo para mostrar.
**Respuesta:** la clave es el código INE; no hay ambigüedad toponímica.
**Veredicto:** **APTO.**

## A11 — Trazabilidad de la narrativa

**Ataque:** “los textos dicen cosas que el modelo no ha calculado”.
**Evidencia:** `redaccion_natural.py` evita causalidad y jerga; tests de redacción; las plantillas
están en `plantillas_es.md`; los números salen de `metrics.json`/panel.
**Respuesta:** el código está auditado; la integración en APEX está pendiente (F12), por lo que
la trazabilidad visual es **PARCIAL** hasta que se monte la ficha.
**Veredicto:** **APTO (código) / PARCIAL (APEX).**

## A12 — Cumplimiento de claims del PDF de diseño

| Claim del diseño | Estado | Evidencia |
|---|---|---|
| MVP funcional | **APTO** | 20 municipios, API, panel, dataset |
| 20 municipios / 8 comarcas | **APTO** | panel validado |
| Oracle Database + ONNX | **APTO** | DDL 01–05, ONNX, scoring N2 |
| Oracle APEX (9 páginas) | **NO CUMPLIDO** | 3 páginas MVP pendientes; 9 es roadmap |
| Fuentes: INE + CKAN | **APTO** | snapshots 24-10 |
| Fuentes: Catastro, CRTM, Notariado | **NO CUMPLIDO** | roadmap; variables estimadas |
| Simulador what-if | **APTO** | `/whatif` |
| Optimizador comarcal | **APTO** | heurística voraz `/optimizar-presupuesto` |
| Spillover continuo | **NO CUMPLIDO** | roadmap Fase 2 |
| Validación temporal | **NO CUMPLIDO** | sin serie histórica; declarado |
| Datos reales de médicos/plazas | **NO CUMPLIDO** | calibración sintética declarada |

**Respuesta:** el MVP cumple el núcleo (datos, índice, reglas, simulación, optimizador, Oracle);
lo que no cumple se declara como roadmap. No se presenta como terminado.
**Veredicto:** **PARCIAL** (honesto).

---

## Puntos fuertes (F14.2)

1. **Datos oficiales fechados y trazables:** INE + CKAN con snapshot y código INE.
2. **Regla no compensatoria verificada:** 10 colapsos, 0 con ICA alto.
3. **Optimizador que sabe no gastar:** Navalcarnero recibe 0 € porque la vivienda limita.
4. **Rigor declarado:** F3 (0 bloqueantes, 2 materiales), F4 (baselines + bootstrap), model cards.
5. **Entrega verificable:** dataset + diccionario + fuentes + checksums + ZIP.

## Plan de corrección priorizado

1. Montar las 3 páginas APEX (P3) — F12.
2. Regenerar `arquetipo_nombre` del panel desde `clustering.json` (M5) — coherencia visual.
3. Informe técnico y glosario (F13.2) — en curso.
4. Diapositivas y ensayo (F15) — P3.
5. Issues reales de GitHub y congelado de `main` (F16).
