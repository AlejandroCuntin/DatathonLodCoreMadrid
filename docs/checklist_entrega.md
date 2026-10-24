# Checklist de Entrega — F16
## II Datathon LoDCOREMadrid 2026 · 29 de octubre · 10:00

> **Regla:** nada se da por hecho sin comprobarlo. Marcar cada casilla antes de congelar `main`.

---

## 1. Repositorio y código

- [ ] `main` actualizado y sin cambios pendientes (salvo `thresholds.py`, decidir).
- [ ] `python -m pytest tests -q` → **36 passed**.
- [ ] `python scripts/run_all_models_n1_n2_n3.py` → termina sin errores.
- [ ] `python scripts/check_model_cards.py` → OK.
- [ ] `python scripts/audit_f3_leakage.py` → OK.
- [ ] No hay credenciales, tokens ni claves en el repo (`git grep -i "api_key\|token\|password"`).
- [ ] `.gitignore` cubre `__pycache__`, `.pytest_cache`, `.venv`, `mlruns`.
- [ ] Issues reales de GitHub creados o, si no, decisión explícita de no crearlos.

## 2. Dataset y paquete del jurado

- [ ] `data/validated/municipios_panel_validado.csv` es el canónico (20×88, 0 nulos).
- [ ] `data/processed` y `data/output/municipios_completo_ml.csv` coinciden con el validado.
- [ ] `data/output/municipios_comunidad_madrid_completo.json` coincide (20 registros).
- [ ] `entrega/` tiene dataset, diccionario, fuentes, matriz, validación, model cards, ficha y guía Oracle.
- [ ] `entrega/MANIFIESTO.json` y `.sha256` regenerados y verificados.
- [ ] `LoDCORE_Madrid_dataset_2026.zip` regenerado y verificado (CSV = panel canónico).
- [ ] El ZIP está accesible desde el móvil del presentador y desde el portátil del salón.

## 3. Oracle / APEX

- [ ] DDL `01` → `05` ejecutado en el esquema de la demo (no ejecutar `06` después del `02`).
- [ ] Carga del CSV 1:1 en `municipios_procesados` (88 columnas; virtuales generadas).
- [ ] Consultas de comprobación: 20 filas, 200.267 hab., 2 ALTA/6 MEDIA/12 BAJA, 0 colapsos con ICA ≥ 40.
- [ ] ONNX cargados en Oracle y vista `v_onnx_scoring_n2` responde.
- [ ] Endpoint ORDS del mapa responde (`/ords/datathon/lodcore/municipios`).
- [ ] 3 páginas APEX: dashboard+mapa, explorador, ficha+simulador.
- [ ] Vistas con `origen`, `metodo`, `dataset_version`.

## 4. Demo y presentación

- [ ] Guion de 15 min ensayado ×3 (15:00 ± 0:30).
- [ ] Diapositivas cargadas y probadas en el portátil del salón.
- [ ] Simulador probado con Chinchón (+400) y optimizador con Sierra Oeste (2 M€).
- [ ] Plan B probado: `frontend/index.html` offline y tabla de respaldo.
- [ ] Nadie dice: SHAP, ONNX, float32, AVM, gradient boosting, p-valor, “179”.
- [ ] Cifras de la demo coinciden con la pantalla: 37,9 · 5.078 · 35,9 M€ · 1.336 · 1.650.000.

## 5. Seguridad y accesos

- [ ] Rotar la clave de API que se expuso en el chat.
- [ ] Revisar que no haya secretos en el historial reciente de git.
- [ ] Acceso al repositorio y al ZIP comprobado desde una cuenta distinta.

## 6. Congelado

- [ ] Etiqueta `v1.0.0-F2` en el commit final.
- [ ] `main` congelado (no más merges sin justificar).
- [ ] Resumen final publicado en el grupo del equipo (regla §14 de `project_context.md`).
- [ ] Contacto y atribución en `entrega/README_ENTREGA.md`.

---

## Comandos de verificación rápida

```powershell
python -m pytest tests -q
python scripts/run_all_models_n1_n2_n3.py
python scripts/check_model_cards.py
python scripts/audit_f3_leakage.py

# Verificar el ZIP
Get-FileHash LoDCORE_Madrid_dataset_2026.zip -Algorithm SHA256
```
