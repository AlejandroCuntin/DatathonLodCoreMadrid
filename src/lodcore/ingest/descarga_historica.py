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
# Partes del nombre de la serie que significan "sin desglose" (se descartan las series por sexo, edad, etc.)
TOTALES = {"total", "todas las edades", "ambos sexos", "poblacion", "habitantes", "personas"}
MUNICIPIOS_NO_VALIDOS = {"total", "total provincia", "total nacional"}


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


def parsear_padron(series: list, snapshot: str = "") -> pd.DataFrame:
    """Series Tempus -> DataFrame largo (municipio, año, población) usando solo las series 'Total'."""
    filas = []
    for s in series:
        partes = _partes(str(s.get("Nombre", "")))
        if not partes:
            continue
        municipio, resto = partes[0], partes[1:]
        if _plano(municipio) in MUNICIPIOS_NO_VALIDOS:
            continue
        if any(_plano(p) not in TOTALES for p in resto):
            continue
        codigo = None
        m = re.match(r"^(\d{5})\s+(.*)$", municipio)
        if m:
            codigo, municipio = int(m.group(1)), m.group(2)
        for d in s.get("Data") or []:
            valor = d.get("Valor")
            if valor is None or d.get("Secreto"):
                continue
            filas.append((_anio(d), municipio, codigo, float(valor)))
    if not filas:
        raise ValueError("No se reconoció ninguna serie 'Total' por municipio. Ejecuta --inspeccionar sobre el JSON "
                         "y revisa el formato del campo 'Nombre'.")
    df = pd.DataFrame(filas, columns=["anio", "municipio", "codigo_ine", "poblacion"])
    df["clave"] = df["municipio"].map(normalizar_nombre)
    dup = df[df.duplicated(["clave", "anio"], keep=False)]
    if not dup.empty:
        ej = dup.sort_values(["clave", "anio"]).head(6)[["municipio", "anio", "poblacion"]].to_string(index=False)
        raise ValueError("Hay varias series 'Total' para el mismo municipio y año; revisar el filtro de series:\n" + ej)
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
        df = parsear_padron(series)
        log(f"OK: {df['clave'].nunique()} municipios, años {df['anio'].min()}-{df['anio'].max()}")
    except ValueError as e:
        log(f"FALLO de parseo: {e}")


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

    df = parsear_padron(series, snapshot=ruta.name)
    escritos = escribir_csv_por_anio(df, raiz / "data" / "raw", forzar=a.forzar, log=log)
    log(f"{df['clave'].nunique()} municipios · años {df['anio'].min()}-{df['anio'].max()} · "
        f"{len(escritos)} CSV nuevos en data/raw/")
    return 0


if __name__ == "__main__":
    sys.exit(main())
