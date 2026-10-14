#!/usr/bin/env python3
"""Lee FC101.PV y FC101.SP desde Matrikon OPC DA en Windows.

Ejecutar en el mismo Windows donde Matrikon OPC Explorer ya funciona.
Instalacion (con el mismo interprete que ejecutara este archivo):
    python -m pip install OpenOPC-DA==1.5.1 pywin32 Pyro5

Uso:
    python leer_matrikon_opc_da.py
    python leer_matrikon_opc_da.py --once
    python leer_matrikon_opc_da.py --list-servers
    python leer_matrikon_opc_da.py --interval 0.5

La arquitectura de Python debe ser compatible con la DLL OPC Automation
registrada. Si esa DLL es de 32 bits, ejecutar con Python de 32 bits.
Los tiempos OPC son los del servidor; no son el SimTime de DYNSIM.
Este cliente solo lee: no modifica el SP ni escribe en Matrikon.

Referencias:
https://github.com/j3mg/openopc
https://openopc.sourceforge.net/api.html
"""

import argparse
import math
import platform
import struct
import sys
import time

SERVER = "Matrikon.OPC.Simulation.1"
HOST = "localhost"
TAGS = [
    "Process.Plant01.Control.FC101.PV",
    "Process.Plant01.Control.FC101.SP",
]
GROUP = "Python_FC101_Lectura"


def positive_seconds(value):
    seconds = float(value)
    if not math.isfinite(seconds) or seconds <= 0:
        raise argparse.ArgumentTypeError("El intervalo debe ser finito y mayor que cero.")
    return seconds


def show_rows(rows):
    if not rows:
        raise RuntimeError("El servidor no devolvio datos para los tags solicitados.")
    for tag, value, quality, timestamp, error in rows:
        displayed = f"{value:.6f}" if isinstance(value, float) else str(value)
        print(f"{tag} | valor={displayed} | calidad={quality} | hora_OPC={timestamp}")
        if str(quality).lower() != "good":
            print(f"  Lectura con calidad {quality}. Detalle: {error}", file=sys.stderr)
    print(flush=True)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--interval", type=positive_seconds, default=1.0,
                        help="Intervalo entre lecturas en segundos (predeterminado: 1).")
    parser.add_argument("--once", action="store_true", help="Leer una vez y terminar.")
    parser.add_argument("--list-servers", action="store_true",
                        help="Listar servidores OPC DA locales y terminar.")
    parser.add_argument("--server", default=SERVER, help="ProgID del servidor OPC DA.")
    args = parser.parse_args(argv)

    if platform.system() != "Windows":
        print("Ejecuta este script en Windows, en la maquina donde esta Matrikon.",
              file=sys.stderr)
        return 1
    try:
        import OpenOPC
    except ImportError as exc:
        print(f"Falta una dependencia: {exc}\nInstala con:\n"
              "python -m pip install OpenOPC-DA==1.5.1 pywin32 Pyro5", file=sys.stderr)
        return 1

    opc = None
    group_created = False
    try:
        print(f"Python {platform.python_version()} / {struct.calcsize('P') * 8} bits")
        opc = OpenOPC.client()
        if args.list_servers:
            for server in opc.servers():
                print(server)
            return 0
        if opc.connect(args.server, HOST) is False:
            raise RuntimeError(f"No se pudo conectar a {args.server} en {HOST}.")
        print(f"Conectado a {args.server} en {HOST}. Ctrl+C para terminar.")
        # Crear el grupo una vez y reutilizarlo. Leer del dispositivo mediante
        # OPC DA sincrono evita depender de callbacks asincronos de Python.
        rows = opc.read(TAGS, group=GROUP, sync=True, source="device", include_error=True)
        group_created = True
        while True:
            show_rows(rows)
            if args.once:
                return 0
            time.sleep(args.interval)
            rows = opc.read(group=GROUP, sync=True, source="device", include_error=True)
    except KeyboardInterrupt:
        print("\nLectura finalizada.")
        return 0
    except Exception as exc:
        print(f"Error OPC DA: {exc}", file=sys.stderr)
        print("Comprueba que Matrikon este activo y que los Item ID coincidan con Explorer.\n"
              "Si falla al crear el cliente COM, comprueba que OPC Automation este\n"
              "instalado/registrado y que su arquitectura coincida con Python.", file=sys.stderr)
        return 1
    finally:
        if opc is not None:
            if group_created:
                try:
                    opc.remove(GROUP)
                except Exception as exc:
                    print(f"Aviso al liberar el grupo OPC: {exc}", file=sys.stderr)
            try:
                opc.close()
            except Exception as exc:
                print(f"Aviso al cerrar el cliente OPC: {exc}", file=sys.stderr)


if __name__ == "__main__":
    raise SystemExit(main())
