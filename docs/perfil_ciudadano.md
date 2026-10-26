# Perfil Ciudadano — especificación funcional (C1)

> Contrato de entrada del perfil ciudadano y traducción **documentada** a pesos y filtros.
> Regla: ninguna ponderación es arbitraria; cada campo del formulario tiene un efecto explícito.

---

## 1. Entradas del formulario

| Campo | Tipo | Rango | Obligatorio | Para qué se usa |
|---|---|---|---|---|
| `presupuesto_max_m2_eur` | €/m² | 300–6.000 | Sí | Filtro duro de precio |
| `ingresos_netos_hogar_eur` | €/mes | 500–20.000 | Sí | Esfuerzo financiero (cuota/ingresos) |
| `tiempo_max_commute_min` | minutos | 10–120 | Sí | Filtro duro de tiempo a Madrid |
| `modo_transporte` | `publico` / `privado` | — | Sí | Peso de conectividad |
| `num_hijos` | entero | 0–6 | Sí | Peso de educación |
| `edad` | años | 18–90 | Sí | Peso de sanidad / educación |
| `tenencia` | `compra` / `alquiler` | — | Sí | Qué precio se evalúa |
| `m2_deseados` | m² | 40–250 | Sí (def. 90) | Cálculo de la cuota |

**Privacidad:** no se persiste ningún dato personal. El cálculo se hace en la sesión (APEX / FastAPI) y el resultado no se almacena.

---

## 2. Pesos base del perfil ciudadano

Los pesos se aplican sobre los **4 sub-índices** de M2 (0–100).

| Dimensión | Peso base |
|---|---|
| Vivienda | 0,30 |
| Educación | 0,25 |
| Conectividad | 0,25 |
| Sanidad | 0,20 |

---

## 3. Ajustes personales (y por qué)

| Condición | Ajuste | Justificación |
|---|---|---|
| `num_hijos` > 0 | Educación **+0,10 por hijo** (máx. +0,20) | La escolarización es la primera restricción de una familia |
| `edad` ≥ 65 | Sanidad **+0,10** | Uso sanitario creciente |
| `edad` ≤ 45 | Educación **+0,05** | Etapa de formación de hogar |
| 46 ≤ `edad` < 65 | Sanidad **+0,05** | Transición |
| `modo_transporte` = público | Conectividad **+0,05** | Dependencia real de la red |
| `tenencia` = alquiler | Vivienda **+0,05** | Sensibilidad al mercado de alquiler |

Tras los ajustes, **los pesos se normalizan para sumar 1,0**. Ningún ajuste puede dejar un peso negativo.

**Regla intocable:** estos pesos solo afectan al **ranking**. Nunca al ICA ni a la regla no compensatoria.

---

## 4. Filtros duros (antes de ordenar)

| Filtro | Condición | Efecto |
|---|---|---|
| Precio | `precio_m2_compra` ≤ `presupuesto_max_m2_eur` (o alquiler si aplica) | Se excluye |
| Tiempo | `tiempo_medio_madrid_minutos` ≤ `tiempo_max_commute_min` | Se excluye |
| Colapso | `indice_capacidad_global` < 40 o alerta no compensatoria | **No se excluye**: se muestra marcado en rojo |

Decisión de producto: **informar, no ocultar**. Un municipio colapsado aparece con etiqueta y su motivo.

---

## 5. Esfuerzo financiero

Para compra:
```
precio_vivienda      = precio_m2 × m2_deseados
importe_financiado   = precio_vivienda × 0,80          (20 % entrada)
cuota_mensual        = importe_financiado × factor(3,5 % anual, 30 años)
esfuerzo_pct         = cuota_mensual / ingresos_netos_hogar × 100
```

Factor de la cuota (sistema francés):
```
r = 0,035 / 12        n = 360
factor = r / (1 − (1 + r)^(−n))
```

Baremos de lectura:

| Esfuerzo | Etiqueta |
|---|---|
| ≤ 30 % | Asequible |
| 30–35 % | Ajustado |
| 35–45 % | Alto |
| > 45 % | No asequible |

Para alquiler: se usa `precio_m2_alquiler × m2_deseados × 12 / 12` como cuota mensual.

---

## 6. Salida por municipio

```json
{
  "nombre": "Robledo de Chavela",
  "afinidad_pct": 0.0,
  "desglose": {"vivienda": 0.0, "educacion": 0.0, "conectividad": 0.0, "sanidad": 0.0},
  "esfuerzo_financiero_pct": 0.0,
  "etiqueta_esfuerzo": "Ajustado",
  "gap_mercado_pct": 0.0,
  "semaforo_ica": "ALTA",
  "alerta_no_compensatoria": false,
  "motivo_colapso": null,
  "fortalezas": ["..."],
  "carencias": ["..."],
  "riesgo_futuro": {"poblacion_2031": 0, "anio_saturacion": null, "alerta": "ESTABLE"},
  "motivo_recomendacion": "texto en español sin causalidad"
}
```

---

## 7. Criterios de aceptación

- [ ] Los pesos suman 1,0 para cualquier combinación de entradas.
- [ ] Un perfil con 3 hijos y 30 años tiene más peso en educación que uno sin hijos.
- [ ] Un perfil de 70 años tiene más peso en sanidad.
- [ ] Bajar el presupuesto nunca incorpora municipios más caros.
- [ ] Un municipio colapsado aparece marcado y nunca sin motivo.
- [ ] El esfuerzo financiero se explica con la fórmula y el tipo declarado.
- [ ] El ranking no cambia el ICA ni la regla no compensatoria (test explícito).
