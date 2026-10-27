#!/usr/bin/env python
"""Pipeline M6 de extremo a extremo: descarga -> validación -> entrenamiento -> ONNX.

Uso (desde la raíz del repositorio):
    python scripts/run_pipeline_proyeccion.py                     # descarga 30 años y entrena
    python scripts/run_pipeline_proyeccion.py --sin-descarga      # usa los data/raw/AAAA_raw_ine_padron.csv existentes
    python scripts/run_pipeline_proyeccion.py --desde-snapshot data/raw/ine/ine_padron_2881_..._snapshot_AAAAMMDD.json

Códigos de salida: 0 correcto · 1 datos/validación · 2 faltan dependencias · 3 otro error.
Resultado: oracle/onnx/m6_proyeccion.onnx (+ .metadata.json) listo para cargar en la base de datos.
"""
from __future__ import annotations

import argparse
import sys
import time
import traceback
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))


def _importar():
    try:
        from src.lodcore.ingest import descarga_historica as desc
        from src.lodcore.models.m6_proyeccion import train as m6
    except ModuleNotFoundError:
        sys.path.insert(0, str(RAIZ / "src"))
        from lodcore.ingest import descarga_historica as desc
        from lodcore.models.m6_proyeccion import train as m6
    return desc, m6


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--anios", type=int, default=30, help="Años de histórico a descargar del INE")
    ap.add_argument("--sin-descarga", action="store_true", help="No descargar: usar los CSV de data/raw")
    ap.add_argument("--desde-snapshot", type=Path, help="Generar los CSV desde un JSON ya descargado (sin red)")
    ap.add_argument("--forzar", action="store_true", help="Sobrescribir los CSV AAAA_raw_ine_padron.csv")
    a = ap.parse_args(argv)
    t0 = time.time()

    try:
        desc, m6 = _importar()
        print("\n[Pipeline 1/2] Datos de origen")
        if a.sin_descarga:
            print("  descarga omitida (--sin-descarga)")
        else:
            args = ["--desde-snapshot", str(a.desde_snapshot)] if a.desde_snapshot else ["--anios", str(a.anios)]
            if a.forzar:
                args.append("--forzar")
            desc.main(args)
        print("\n[Pipeline 2/2] Validación, entrenamiento y exportación")
        res = m6.ejecutar(raiz=RAIZ)
    except (ValueError, FileNotFoundError) as e:
        print(f"\nERROR de datos: {e}", file=sys.stderr)
        return 1
    except ImportError as e:
        print(f"\nFALTA una dependencia: {e}\n  Instala:  python -m pip install skl2onnx onnxruntime requests pyyaml scikit-learn pandas",
              file=sys.stderr)
        return 2
    except Exception:  # noqa: BLE001
        traceback.print_exc()
        return 3

    print(f"\nPipeline completado en {time.time() - t0:.0f} s")
    print(f"  ONNX:      {res['onnx']}")
    print(f"  Metadatos: {Path(res['onnx']).with_suffix('.metadata.json')}")
    print(f"  Datos actuales: {RAIZ / 'data' / 'validated' / 'm6_entradas_actuales.csv'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
