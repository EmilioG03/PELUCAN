"""Genera un respaldo de PostgreSQL usando pg_dump.

La conexión se configura con las variables estándar PGHOST, PGPORT, PGUSER y
PGPASSWORD. Ejemplo: python scripts/backup_bd.py --database pelucan
"""

import argparse
from datetime import datetime
from pathlib import Path
import shutil
import subprocess
import sys


def construir_comando(database, destino, pg_dump="pg_dump"):
    return [
        pg_dump,
        "--format=custom",
        "--no-owner",
        f"--file={destino}",
        database,
    ]


def crear_backup(database="pelucan", carpeta="backups", pg_dump="pg_dump"):
    ejecutable = shutil.which(pg_dump)
    if ejecutable is None:
        raise RuntimeError(
            "No se encontró pg_dump. Instalá las herramientas de PostgreSQL "
            "y agregalas al PATH."
        )

    directorio = Path(carpeta)
    directorio.mkdir(parents=True, exist_ok=True)
    marca_tiempo = datetime.now().strftime("%Y%m%d_%H%M%S")
    destino = directorio / f"{database}_{marca_tiempo}.backup"
    subprocess.run(
        construir_comando(database, destino, ejecutable),
        check=True,
    )
    return destino


def main():
    parser = argparse.ArgumentParser(description="Respalda la base de datos de PELUCAN.")
    parser.add_argument("--database", default="pelucan", help="Nombre de la base de datos")
    parser.add_argument("--output", default="backups", help="Carpeta de destino")
    argumentos = parser.parse_args()

    try:
        destino = crear_backup(argumentos.database, argumentos.output)
    except (RuntimeError, subprocess.CalledProcessError) as error:
        print(f"No se pudo generar el backup: {error}", file=sys.stderr)
        return 1

    print(f"Backup generado correctamente: {destino}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
