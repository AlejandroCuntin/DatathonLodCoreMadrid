# Diapositivas — Guion visual de 15 minutos (F15)
## II Datathon LoDCOREMadrid 2026 · 29 de octubre · UC3M Leganés

> **Uso:** contenido listo para pasar a PowerPoint/APEX. Cada diapositiva indica título,
> bullets, visual sugerido, quién habla y minutos. El texto literal está en
> `docs/guion_presentacion_15min.md`.

---

## Diapositiva 1 — Portada (00:00–00:20) · P3
**Título:** LoDCORE Madrid · Capacidad de acogida municipal
**Subtítulo:** II Datathon LoDCOREMadrid 2026 · UC3M + Comunidad de Madrid
**Visual:** mapa de la CAM con 20 puntos; logos UC3M / CAM.
**Pie:** “No es un ranking de municipios bonitos: es una herramienta para decidir dónde invertir.”

---

## Diapositiva 2 — El reto (00:20–02:00) · P3
**Título:** Repartir población sin romper servicios
**Bullets:**
- 179 municipios en la CAM; **155** con menos de 50.000 habitantes.
- Presión en el área metropolitana; capacidad ociosa en la corona exterior.
- La pregunta: ¿dónde caben más personas **sin colapsar** sanidad, escuela o vivienda?
**Visual:** mapa de Madrid con dos zonas (presión / capacidad).
**Cifras:** 20 municipios piloto · 8 comarcas · 200.267 hab. · ICA medio 37,9.

---

## Diapositiva 3 — Qué hemos construido (02:00–03:30) · P2
**Título:** Una herramienta de decisión, no un adivino
**Bullets:**
- Datos oficiales fechados → panel municipal → índice + reglas → Oracle → APEX/FastAPI.
- **Qué es real:** población (INE) y centros (CAM). **Qué es estimado:** médicos, plazas, vivienda, precios.
- Regla dura: un servicio colapsado no se compensa.
**Visual:** diagrama de 4 cajas (Datos → Panel → Modelo/Reglas → Oracle/APEX).
**Frase:** “Si un servicio está roto, nada lo compensa.”

---

## Diapositiva 4 — El mapa semafórico (03:30–05:30) · P3
**Título:** Dónde se puede acoger hoy
**Bullets:**
- **2 ALTA · 6 MEDIA · 12 BAJA**.
- **10** bloqueados por sanidad; **9** por educación; **1** por vivienda.
- Top: Robledo 66,7 · Buitrago 62,5 · Montejo 59,9.
- Navalcarnero 24,5: 1.667 hab./médico y aulas al 95 %.
**Visual:** captura del mapa APEX con filtro “ALTA” y ficha de Robledo.
**Frase:** “El mapa dice dónde hay que invertir.”

---

## Diapositiva 5 — Capacidad y coste (05:30–06:30) · P3
**Título:** Cuánta gente cabe y cuánto cuesta
**Bullets:**
- **5.078 personas** de capacidad inmediata sin colapso.
- **35,9 M€** de refuerzo para los 12 municipios en alerta.
- 10 municipios en colapso y **0 con ICA alto**.
**Visual:** barras por comarca (capacidad) + tabla de coste.
**Frase:** “No es una opinión: es una factura.”

---

## Diapositiva 6 — Simulador what-if (06:30–09:00) · P2 (opera) + P1
**Título:** ¿Qué pasa si llegan 400 vecinos?
**Bullets:**
- Se elige municipio y escenario (+400 hab., médicos, plazas, conectividad).
- El sistema dice **qué servicio se satura primero** y cuánto cuesta evitarlo.
- Chinchón: 5.800 hab., ICA 49,5, cupo 578, límite educación.
**Visual:** captura de la ficha + simulador (antes/después).
**Frase:** “No dice ‘habrá tensión’: dice qué se rompe primero.”

---

## Diapositiva 7 — Optimizador comarcal (09:00–11:30) · P1
**Título:** Dónde invertir con 2 M€
**Bullets:**
- Sierra Oeste: **1 médico en Villa del Prado** (450.000 €, +830 personas).
- **50 plazas** en San Martín (+279) y **50** en Robledo (+227).
- Total: **1.650.000 €**, **+1.336 personas**, **350.000 € sin gastar**.
- Navalcarnero: **0 €**; el límite es la vivienda, no el dinero.
**Visual:** tabla de asignación (municipio, medida, coste, personas).
**Frase:** “También sabe decir: aquí no hay que gastar.”

---

## Diapositiva 8 — El tiempo (11:30–13:00) · P2
**Título:** Qué pasa en 2030 y 2035
**Bullets:**
- 200.267 → **216.597** (2030) → **234.336** (2035).
- 12 municipios con refuerzo urgente; Navalcarnero y Ciempozuelos ya saturados en 2025.
- Bandas del 95 % y escenarios +5 % / +10 %.
**Visual:** línea de población con banda + semáforo de saturación.
**Frase:** “No es una previsión lejana: es una factura de este año.”

---

## Diapositiva 9 — Rigor y límites (13:00–14:00) · P3
**Título:** Lo que hemos auditado (y lo que no)
**Bullets:**
- **F3:** 0 fugas bloqueantes; 2 materiales (target determinista y sesgo de selección).
- **F4:** GroupKFold por comarca, 4 baselines, bootstrap B=1000.
- **36 tests**; dataset con checksums; modelo reproducible.
- Lo que falta: APEX (3 páginas), datos reales de dotación, spillover, validación temporal.
**Visual:** tabla de 3 columnas: “hecho / parcial / roadmap”.
**Frase:** “Nos corregimos nosotros antes de que nos corrija nadie.”

---

## Diapositiva 10 — Cierre y pedido (14:00–15:00) · P3
**Título:** Qué pedimos
**Bullets:**
- Acceso a los registros oficiales de **SERMAS** y **Consejería de Educación**.
- Ampliar de 20 a **155 municipios**.
- Pasar del piloto a la planificación real con Oracle APEX.
**Visual:** mapa completo de la CAM + logo institucional.
**Frase final:** “No os pedimos que nos creáis: os damos el dataset y las fuentes para que lo comprobéis.”

---

## Diapositiva 11 — Backup / preguntas (oculta)
**Título:** Datos para preguntas
**Contenido:** métricas M1–M5, tabla de asignación de Sierra Oeste, direcciones de artefactos
(`docs/validacion.md`, `docs/model_cards.md`, `entrega/`), y las 7 respuestas del guion.

---

## Notas de diseño
- **Formato:** 16:9; tipografía institucional; azul CAM + verde/ámbar/rojo del semáforo.
- **Una idea por diapositiva**; máximo 6 bullets; cifras grandes.
- **No incluir:** SHAP, ONNX, float32, AVM, gradient boosting, p-valor, “179”.
- **Cada diapositiva debe poder explicarse en 30 segundos** sin leer.
