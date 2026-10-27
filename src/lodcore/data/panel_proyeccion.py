"""Panel municipio-año para el modelo M6 (proyección de población).

Lee data/raw/AAAA_raw_ine_padron.csv, valida (puertas de calidad), construye las características
en el año de origen t usando SOLO datos <= t (control punto-en-tiempo) y los pares de entrenamiento
(municipio, t, h) con objetivo y = ln(P[t+h] / P[t]).
"""
from __future__ import annotations

import re
from pathlib import Path

import numpy as np
import pandas as pd

from ..ingest.descarga_historica import normalizar_nombre

VENTANA = 5
FEATURES_ORIGEN = ["ln_pob", "g1", "g3", "g5", "vol5"]
FEATURES = FEATURES_ORIGEN + ["h"]
_PATRON = re.compile(r"^(\d{4})_raw_ine_padron\.csv$")


def cargar_padron_raw(dir_raw: Path) -> pd.DataFrame:
    ficheros = sorted(p for p in Path(dir_raw).glob("*_raw_ine_padron.csv") if _PATRON.match(p.name))
    if not ficheros:
        raise FileNotFoundError(f"No hay ficheros AAAA_raw_ine_padron.csv en {dir_raw}. "
                                "Ejecuta la descarga (descarga_historica.py).")
    return pd.concat((pd.read_csv(p, dtype={"clave": str}) for p in ficheros), ignore_index=True)


def recortar_a_tramo_contiguo(df: pd.DataFrame) -> tuple[pd.DataFrame, list[int]]:
    """Si la serie tiene huecos de años (el INE no publica el Padrón de 1997), se usa solo el tramo contiguo
    más reciente en lugar de inventar los años que faltan. Devuelve (datos, años_descartados)."""
    anios = sorted(int(a) for a in df["anio"].unique())
    inicio = anios[-1]
    for a in reversed(anios[:-1]):
        if a != inicio - 1:
            break
        inicio = a
    return df[df["anio"] >= inicio].copy(), [a for a in anios if a < inicio]


def validar_padron(df: pd.DataFrame, min_anios: int = 12, min_municipios: int = 100,
                   max_vacios: float = 0.05, max_salto: float = 0.7) -> dict:
    """Puertas de calidad. Lanza ValueError con todos los problemas encontrados."""
    errores = []
    faltan = {"anio", "clave", "poblacion"} - set(df.columns)
    if faltan:
        raise ValueError(f"Faltan columnas en el padrón: {sorted(faltan)}")
    if df["poblacion"].isna().any():
        errores.append("hay poblaciones nulas")
    if (df["poblacion"] <= 0).any():
        errores.append("hay poblaciones <= 0")
    if df.duplicated(["clave", "anio"]).any():
        errores.append("hay pares municipio-año duplicados")
    anios = sorted(df["anio"].unique())
    if len(anios) < min_anios:
        errores.append(f"solo {len(anios)} años de histórico (mínimo {min_anios}); descarga más años")
    if anios and anios != list(range(anios[0], anios[-1] + 1)):
        errores.append("faltan años intermedios en la serie")
    n_mun = df["clave"].nunique()
    if n_mun < min_municipios:
        errores.append(f"solo {n_mun} municipios (mínimo {min_municipios}) para entrenar con garantías")
    P = a_ancho(df)
    vacios = float(P.isna().mean().mean()) if P.size else 1.0
    if vacios > max_vacios:
        errores.append(f"{vacios:.1%} de celdas municipio-año vacías (máximo {max_vacios:.0%})")
    saltos = np.abs(np.log(P.astype(float).where(P > 0)).diff(axis=1)).to_numpy()
    n_saltos = int(np.nansum(saltos > max_salto))
    if n_saltos > 0.01 * max(P.size, 1):
        errores.append(f"{n_saltos} saltos anuales > {max_salto} en log (posibles errores de datos)")
    if errores:
        raise ValueError("Puertas de calidad del padrón no superadas: " + "; ".join(errores))
    return {"municipios": int(n_mun), "anio_min": int(anios[0]), "anio_max": int(anios[-1]),
            "celdas_vacias_pct": round(100 * vacios, 2), "saltos_anuales_extremos": n_saltos}


def a_ancho(df: pd.DataFrame) -> pd.DataFrame:
    P = df.pivot(index="clave", columns="anio", values="poblacion").sort_index(axis=1)
    P.columns = P.columns.astype(int)
    return P


def features_en(P: pd.DataFrame, t: int) -> pd.DataFrame:
    """Características en el año de origen t. Usa únicamente columnas <= t."""
    anios = list(range(t - VENTANA, t + 1))
    if any(a not in P.columns for a in anios):
        return pd.DataFrame(columns=FEATURES_ORIGEN)
    lp = np.log(P[anios].astype(float))
    anual = lp.diff(axis=1).iloc[:, 1:]  # 5 crecimientos anuales: t-4 .. t
    X = pd.DataFrame({
        "ln_pob": lp[t],
        "g1": lp[t] - lp[t - 1],
        "g3": (lp[t] - lp[t - 3]) / 3,
        "g5": (lp[t] - lp[t - 5]) / 5,
        "vol5": anual.std(axis=1, ddof=0),
    })
    X = X.replace([np.inf, -np.inf], np.nan).dropna()
    X.index.name = "clave"
    return X


def pares_entrenamiento(P: pd.DataFrame, h_max: int) -> pd.DataFrame:
    """Un registro por (municipio, año de origen, horizonte h). y = ln(P[t+h]/P[t])."""
    ultimo, primero = int(P.columns.max()), int(P.columns.min())
    bloques = []
    for t in range(primero + VENTANA, ultimo):
        X = features_en(P, t)
        if X.empty:
            continue
        for h in range(1, h_max + 1):
            if t + h > ultimo:
                break
            b = X.copy()
            b["h"] = h
            b["anio_origen"] = t
            b["y"] = np.log(P.loc[X.index, t + h].astype(float)) - X["ln_pob"]
            bloques.append(b.dropna().reset_index())
    if not bloques:
        raise ValueError("No se pudo construir ningún par de entrenamiento (histórico insuficiente)")
    return pd.concat(bloques, ignore_index=True)


def entradas_actuales(P: pd.DataFrame, df_raw: pd.DataFrame) -> pd.DataFrame:
    """Características del último año disponible: son los 'datos actuales' que se proyectan con M6."""
    t = int(P.columns.max())
    X = features_en(P, t).copy()
    X["anio_origen"] = t
    X["poblacion_actual"] = P.loc[X.index, t].round().astype(int)
    cols = ["clave", "municipio"] + (["codigo_ine"] if "codigo_ine" in df_raw.columns else [])
    nombres = df_raw.drop_duplicates("clave")[cols].set_index("clave")
    return X.join(nombres).reset_index()


def unir_codigo_ine(entradas: pd.DataFrame, ruta_panel: Path) -> tuple[pd.DataFrame, list[str]]:
    """Completa codigo_ine cruzando por nombre con el panel de 20 municipios. Devuelve (entradas, sin_cruce)."""
    ruta_panel = Path(ruta_panel)
    if not ruta_panel.exists():
        return entradas, []
    panel = pd.read_csv(ruta_panel, usecols=["codigo_ine", "nombre"])
    panel["clave"] = panel["nombre"].map(normalizar_nombre)
    mapa = panel.drop_duplicates("clave").set_index("clave")["codigo_ine"]
    out = entradas.copy()
    if "codigo_ine" not in out.columns:
        out["codigo_ine"] = np.nan
    out["codigo_ine"] = out["codigo_ine"].fillna(out["clave"].map(mapa))
    sin_cruce = sorted(set(panel["clave"]) - set(out["clave"]))
    return out, sin_cruce
