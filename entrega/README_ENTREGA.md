# Entrega del Dataset — LoDCORE Madrid
## II Datathon LoDCOREMadrid 2026 · UC3M + Comunidad de Madrid

> **Qué es:** el dataset municipal integrado que usa la herramienta LoDCORE para diagnosticar
> la capacidad de acogida de los municipios de la Comunidad de Madrid y para simular inversiones.
> **Qué no es:** un registro oficial ni un padrón. Es una elaboración propia sobre fuentes
> oficiales, con las estimaciones declaradas una por una.

## Contenido de esta carpeta

| Archivo | Qué contiene |
|---|---|
| `dataset/municipios_panel_validado.csv` | **Dataset principal**: 20 municipios × 88 variables, UTF-8 |
| `dataset/municipios_panel_validado.json` | El mismo dataset en JSON (array de registros) |
| `FICHA_DATASET.md` | Ficha de una página: cobertura, calidad, resultados y límites |
| `CARGA_ORACLE.md` | Cómo cargarlo en Oracle Database 23ai / Oracle APEX |
| `docs/diccionario_datos.md` | Diccionario de las 88 variables (tipo, unidad, origen, descripción) |
| `docs/fuentes_oficiales.md` | Fuentes, licencias y atribución (INE y CKAN CAM) |
| `docs/matriz_procedencia_variables.md` | Procedencia variable a variable |
| `docs/validacion.md` | Informe de validación y métricas de los modelos |
| `docs/limite_no_compensatorio.md` | Reglas duras y umbrales del MVP |
| `MANIFIESTO.json` / `MANIFIESTO.sha256` | Metadatos y checksums para verificar la entrega |

## Cómo abrirlo

- **CSV:** está en UTF-8. En Excel, usar *Datos → Obtener datos → Desde texto/CSV* y elegir
  **UTF-8** para que los acentos salgan bien (doble clic puede mostrarlos mal).
- **JSON:** cualquier editor o `json.load()` en Python. Cada elemento es un municipio con las
  mismas 88 claves que el CSV.
- **Clave primaria:** `codigo_ine` (5 dígitos, 28xxx). No usar `nombre` para cruzar.

## Atribución y licencia

- **Población:** Instituto Nacional de Estadística (Padrón Municipal continuo, tabla 2881, 2025).
  Reutilización con atribución (Ley 37/2007 y RD 1495/2011).
- **Centros sanitarios y educativos:** Comunidad de Madrid, Datos Abiertos, **CC BY 4.0**.
- **Resto de variables:** estimaciones calibradas o referencias curadas del equipo, declaradas en
  la matriz de procedencia.
- **Texto de atribución sugerido:** «Dataset elaborado por el equipo LoDCORE Madrid para el
  II Datathon LoDCOREMadrid 2026, a partir del INE y de Datos Abiertos de la Comunidad de Madrid
  (CC BY 4.0). Las estimaciones propias se declaran en la matriz de procedencia.»

## Cómo citar

> Equipo LoDCORE Madrid (2026). *Panel Municipal Integrado LoDCORE Madrid, v1.0.0-F2*
> [Dataset]. II Datathon LoDCOREMadrid. 20 municipios, 8 comarcas.

## Límites (leer antes de usar)

Este dataset es un **piloto de 20 municipios**. La población y los recuentos de centros son
oficiales; la dotación de médicos, plazas, alumnado, vivienda y precios es **calibración sintética**.
No debe usarse para una decisión administrativa real sin sustituir esas estimaciones por los
registros de SERMAS, la Consejería de Educación, Catastro y Notariado. Los detalles están en
`FICHA_DATASET.md` y en `docs/matriz_procedencia_variables.md`.

## Verificación

Cada archivo tiene su SHA-256 en `MANIFIESTO.sha256`. Para comprobarlo:

```powershell
# Windows PowerShell
Get-FileHash dataset/municipios_panel_validado.csv -Algorithm SHA256
# Linux / macOS
sha256sum -c MANIFIESTO.sha256
```
