# Ficha del Dataset — Panel Municipal Integrado LoDCORE Madrid

## Identificación

| Campo | Valor |
|---|---|
| Nombre | Panel Municipal Integrado LoDCORE Madrid |
| Versión | `v1.0.0-F2` |
| Fecha de disponibilidad | `2026-10-24` |
| Ámbito | Comunidad de Madrid · municipios < 50.000 habitantes |
| Cobertura | **20 municipios · 8 comarcas** (piloto) |
| Dimensiones | **20 filas × 88 variables** |
| Población cubierta | **200.267 habitantes** |
| Formato | CSV UTF-8 (principal) + JSON (equivalente) |
| Unidad de observación | Municipio (código INE de 5 dígitos) |

## Calidad verificada

| Comprobación | Resultado |
|---|---|
| Valores nulos | **0** |
| Códigos INE duplicados | **0** |
| Quality gates del pipeline | **PASSED (20/20)** |
| Coherencia del ICA (reconstruido desde subíndices) | diferencia máxima **0,0045** (redondeo) |
| Coherencia de capacidad sanitaria | diferencia **0** |
| Regla no compensatoria | **10 municipios en colapso → 0 con ICA ≥ 40** |
| Copias `validated` / `processed` / `output` | **idénticas** (mismo SHA-256) |

## Resultados clave del piloto

- **ICA medio:** 37,9 / 100.
- **Semáforo:** 2 municipios ALTA · 6 MEDIA · **12 BAJA**.
- **Capacidad de acogida inmediata:** **5.078 personas** sin colapsar servicios.
- **Inversión de refuerzo estimada:** **35,9 M€** para los municipios en alerta.
- **Factor limitante:** 10 municipios por sanidad, 9 por educación, 1 por vivienda.
- **Top 3:** Robledo de Chavela (66,74), Buitrago del Lozoya (62,49), Montejo de la Sierra (59,94).
- **Alertas de saturación:** 12 municipios con refuerzo urgente, 5 con atención media, 3 estables.

## Procedencia (resumen)

- **Observado:** población y año de padrón (INE); recuentos de centros sanitarios y educativos (CKAN Comunidad de Madrid).
- **Simulado (seed 2026):** médicos de AP, plazas escolares, alumnado, vivienda y precios.
- **Estimado:** scores, ICA, salidas de M1/M5.
- **Proyectado:** población 2027/2029/2031 y año de saturación (M3).
- Detalle variable a variable: `docs/diccionario_datos.md` y `docs/matriz_procedencia_variables.md`.

## Límites que deben declararse al usar el dataset

1. **Piloto de 20 municipios** de los 179 de la CAM; no es representativo de toda la región.
2. **La dotación de médicos, plazas, alumnado, vivienda y precios es calibración sintética**, no registro oficial. Sirve para el diagnóstico y el prototipo, no para una decisión administrativa real.
3. **No incluye efecto spillover** entre municipios vecinos (roadmap).
4. **Las proyecciones** del panel son 2027/2029/2031; las métricas agregadas de M3 se publican a 2030/2035. No mezclar horizontes en una misma afirmación.
5. **Dos columnas de camas hospitalarias** (`camas_hospitalarias_cercanas` y `camas_hospital`) están sin conciliar y no entran en el ICA.
6. **`fecha_calculo`** cambia en cada ejecución del pipeline; no es contenido del dataset.

## Cómo verificar

```powershell
# Requisitos: Python 3.11+ y requirements.txt
python -m pip install -r requirements.txt
python scripts/run_all_models_n1_n2_n3.py
python -m pytest tests -q
```

El pipeline reescribe `data/validated/municipios_panel_validado.csv` y deja las métricas en
`src/lodcore/models/*/metrics.json`. Los checksums de esta entrega están en `MANIFIESTO.sha256`.
