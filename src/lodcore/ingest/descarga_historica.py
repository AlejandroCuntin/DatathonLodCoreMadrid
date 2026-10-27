"""Descarga histórica del Padrón municipal (INE, tabla 2881) para el modelo M6.

Escribe un CSV por año con la convención  data/raw/AAAA_raw_ine_padron.csv
(columnas: anio, municipio, clave, codigo_ine, poblacion, fuente, tabla_ine, snapshot).
Además guarda la respuesta cruda del INE en
data/raw/ine/ine_padron_2881_{N}y_snapshot_{AAAAMMDD}.json (misma convención que los snapshots existentes).

Los CSV de data/raw son inmutables: si ya existen no se sobrescriben salvo con --forzar.

Uso (desde la raíz del repositorio):
    python -m src.lodcore.ingest.descarga_historica --anios 30
    python -m src.lodcore.ingest.descarga_historica --desde-snapshot data/raw/ine/ine_padron_2881_6y_snapshot_20261025.json
    python -m src.lodcore.ingest.descarga_historica --inspeccionar data/raw/ine/ine_padron_2881_6y_snapshot_20261025.json

NOTA: el formato de las series (campo "Nombre") se interpreta de forma tolerante, pero no se ha probado
contra la API real. Si el parseo falla, ejecutar --inspeccionar y revisar la salida.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
import unicodedata
from datetime import date
from pathlib import Path

import pandas as pd

INE_URL = "https://servicios.ine.es/wstempus/js/ES/DATOS_TABLA/{tabla}"
TABLA_PADRON = 2881
FUENTE = "INE Padrón continuo"
# Las series del INE llevan en "Nombre" varias dimensiones (municipio, sexo, edad...) en un orden que depende de la
# tabla. Se clasifica cada parte del nombre en lugar de suponer su posición.
SEXO_TOTAL = {"total", "ambos sexos", "ambos"}
SEXO_OTRO = {"hombres", "mujeres", "varones", "hombre", "mujer"}
EDAD_TOTAL = {"todas las edades", "total edades", "todas edades"}
MEDIDAS = {"poblacion", "personas", "habitantes", "dato base", "valor", "numero de personas"}
MUNICIPIOS_NO_VALIDOS = {"total", "total provincia", "total nacional"}
_RE_EDAD = re.compile(r"\b(anos?|edades?)\b|\by mas\b|^\d+\s*(-|a)\s*\d+|^\d+$")
_RE_PREFIJO = re.compile(r"^(sexo|edad|municipios?|periodo|nacionalidad|medida)\s*:\s*")


def raiz_proyecto(inicio: Path | None = None) -> Path:
    """Sube desde este fichero hasta encontrar params.yaml o .git."""
    p = (inicio or Path(__file__).resolve().parent).resolve()
    for cand in [p, *p.parents]:
        if (cand / "params.yaml").exists() or (cand / ".git").exists():
            return cand
    return Path.cwd()


def _plano(s: str) -> str:
    s = unicodedata.normalize("NFD", str(s))
    s = "".join(c for c in s if unicodedata.category(c) != "Mn")
    return re.sub(r"\s+", " ", s).strip().lower()


def normalizar_nombre(nombre: str) -> str:
    """Clave comparable entre fuentes: 'Molar (El)' y 'El Molar' -> 'el molar'."""
    s = _plano(nombre)
    m = re.match(r"^(.*?)\s*\((el|la|los|las)\)$", s) or re.match(r"^(.*?),\s*(el|la|los|las)$", s)
    if m:
        s = f"{m.group(2)} {m.group(1)}"
    s = re.sub(r"[^a-z0-9 ]", " ", s)
    return re.sub(r"\s+", " ", s).strip()


def descargar_tabla_ine(tabla: int, nult: int, timeout: int = 180) -> list:
    import requests  # import tardío: solo hace falta al descargar

    r = requests.get(INE_URL.format(tabla=tabla), params={"nult": nult}, timeout=timeout,
                     headers={"Accept": "application/json"})
    r.raise_for_status()
    datos = r.json()
    if not isinstance(datos, list) or not datos:
        raise RuntimeError(f"Respuesta inesperada del INE para la tabla {tabla} (no es una lista de series)")
    return datos


def guardar_snapshot(datos: list, carpeta: Path, tabla: int, nult: int) -> Path:
    carpeta.mkdir(parents=True, exist_ok=True)
    ruta = carpeta / f"ine_padron_{tabla}_{nult}y_snapshot_{date.today():%Y%m%d}.json"
    ruta.write_text(json.dumps(datos, ensure_ascii=False), encoding="utf-8")
    return ruta


def _partes(nombre: str) -> list[str]:
    partes = [p.strip() for p in re.split(r"\.\s+|\.$", nombre) if p.strip()]
    if len(partes) <= 1:
        partes = [p.strip() for p in nombre.split(",") if p.strip()]
    return partes


def _anio(d: dict) -> int:
    if d.get("Anyo") is not None:
        return int(d["Anyo"])
    if d.get("Fecha") is not None:  # epoch en ms; +12 h para no caer en el 31-dic por la zona horaria
        return int(pd.to_datetime(int(d["Fecha"]) + 12 * 3600 * 1000, unit="ms").year)
    raise ValueError("Dato sin año (ni 'Anyo' ni 'Fecha')")


def clasificar_serie(nombre: str) -> tuple[str | None, bool]:
    """Devuelve (municipio, es_total). municipio es None si no se identifica exactamente uno.
    es_total es False si la serie está desglosada por sexo o por grupo de edad."""
    municipios, es_total = [], True
    for parte in _partes(nombre):
        q = _RE_PREFIJO.sub("", _plano(parte)).strip()
        if not q or q in MEDIDAS or q in SEXO_TOTAL or q in EDAD_TOTAL or q.startswith("total "):
            continue
        if q in SEXO_OTRO or _RE_EDAD.search(q):
            es_total = False
            continue
        municipios.append(re.sub(r"^(sexo|edad|municipios?|periodo|nacionalidad|medida)\s*:\s*", "", parte.strip(), flags=re.I))
    if len(municipios) != 1 or _plano(municipios[0]) in MUNICIPIOS_NO_VALIDOS:
        return None, False
    return municipios[0], es_total


def _muestra_series(series: list, n: int = 8) -> str:
    claves = sorted(series[0].keys()) if series and isinstance(series[0], dict) else type(series[0]).__name__
    nombres = [str(s.get("Nombre")) if isinstance(s, dict) else repr(s)[:80] for s in series[:n]]
    return (f"{len(series)} series; claves de la primera: {claves}\n  - " + "\n  - ".join(nombres))


def parsear_padron(series: list, snapshot: str = "", avisos: list | None = None) -> pd.DataFrame:
    """Series Tempus -> DataFrame largo (municipio, año, población) usando solo las series 'Total'."""
    candidatas: dict[str, list] = {}
    for s in series:
        municipio, es_total = clasificar_serie(str(s.get("Nombre", "")))
        if municipio is None or not es_total:
            continue
        codigo = None
        m = re.match(r"^(\d{5})\s+(.*)$", municipio)
        if m:
            codigo, municipio = int(m.group(1)), m.group(2)
        filas = []
        for d in s.get("Data") or []:
            valor = d.get("Valor")
            if valor is None or d.get("Secreto"):
                continue
            filas.append((_anio(d), municipio, codigo, float(valor)))
        if filas:
            candidatas.setdefault(normalizar_nombre(municipio), []).append((max(f[3] for f in filas), municipio, filas))
    if not candidatas:
        raise ValueError("No se reconoció ninguna serie 'Total' por municipio. Primeras series recibidas del INE:\n  - "
                         + _muestra_series(series) + "\nCopia estas líneas para ajustar el filtro de series.")
    filas = []
    for clave, lst in candidatas.items():
        lst.sort(key=lambda x: x[0])
        if len(lst) > 1:
            if lst[0][0] == lst[1][0]:
                raise ValueError(f"Hay varias series 'Total' idénticas para '{lst[0][1]}'; revisar el filtro de series")
            if avisos is not None:
                avisos.append(f"'{lst[0][1]}' aparece {len(lst)} veces: se usa la de menor población "
                              f"({lst[0][0]:,.0f}) y se descarta la de {lst[-1][0]:,.0f} (total provincial)")
        filas.extend(lst[0][2])
    df = pd.DataFrame(filas, columns=["anio", "municipio", "codigo_ine", "poblacion"])
    df["clave"] = df["municipio"].map(normalizar_nombre)
    df["fuente"] = FUENTE
    df["tabla_ine"] = TABLA_PADRON
    df["snapshot"] = snapshot
    return df[["anio", "municipio", "clave", "codigo_ine", "poblacion", "fuente", "tabla_ine", "snapshot"]] \
        .sort_values(["anio", "clave"]).reset_index(drop=True)


def escribir_csv_por_anio(df: pd.DataFrame, dir_raw: Path, forzar: bool = False, log=print) -> list[Path]:
    dir_raw.mkdir(parents=True, exist_ok=True)
    escritos = []
    for anio, g in df.groupby("anio"):
        ruta = dir_raw / f"{int(anio)}_raw_ine_padron.csv"
        if ruta.exists() and not forzar:
            log(f"  = {ruta.name} ya existe (raw inmutable); usa --forzar para regenerarlo")
            continue
        g.to_csv(ruta, index=False, encoding="utf-8")
        escritos.append(ruta)
    return escritos


def inspeccionar(ruta: Path, log=print) -> None:
    series = json.loads(Path(ruta).read_text(encoding="utf-8"))
    log(f"{len(series)} series en {ruta}")
    for s in series[:8]:
        d = s.get("Data") or []
        log(f"  Nombre={s.get('Nombre')!r}  puntos={len(d)}  claves_dato={sorted(d[0].keys()) if d else []}")
    try:
        avisos: list = []
        df = parsear_padron(series, avisos=avisos)
        log(f"OK: {df['clave'].nunique()} municipios, años {df['anio'].min()}-{df['anio'].max()}")
        for a in avisos:
            log(f"  AVISO: {a}")
    except ValueError as e:
        log(f"FALLO de parseo: {e}")
        log(_muestra_series(series, 15))


def main(argv: list[str] | None = None, log=print) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--anios", type=int, default=30, help="Años de histórico a pedir al INE (nult)")
    ap.add_argument("--desde-snapshot", type=Path, help="Convierte un JSON ya descargado (sin red)")
    ap.add_argument("--inspeccionar", type=Path, help="Muestra la estructura de un JSON y prueba el parseo")
    ap.add_argument("--forzar", action="store_true", help="Sobrescribe los CSV AAAA_raw_ine_padron.csv existentes")
    a = ap.parse_args(argv)

    raiz = raiz_proyecto()
    if a.inspeccionar:
        inspeccionar(a.inspeccionar, log)
        return 0

    if a.desde_snapshot:
        ruta = a.desde_snapshot
        series = json.loads(ruta.read_text(encoding="utf-8"))
    else:
        log(f"Descargando INE tabla {TABLA_PADRON} (últimos {a.anios} años)...")
        series = descargar_tabla_ine(TABLA_PADRON, a.anios)
        ruta = guardar_snapshot(series, raiz / "data" / "raw" / "ine", TABLA_PADRON, a.anios)
        log(f"  snapshot crudo: {ruta}")

    avisos: list = []
    df = parsear_padron(series, snapshot=ruta.name, avisos=avisos)
    for aviso in avisos:
        log(f"  AVISO: {aviso}")
    escritos = escribir_csv_por_anio(df, raiz / "data" / "raw", forzar=a.forzar, log=log)
    log(f"{df['clave'].nunique()} municipios · años {df['anio'].min()}-{df['anio'].max()} · "
        f"{len(escritos)} CSV nuevos en data/raw/")
    return 0


if __name__ == "__main__":
    sys.exit(main())
