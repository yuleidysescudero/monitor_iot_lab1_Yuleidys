"""
dashboard/consola.py
Panel de administracion por consola. Usa EXACTAMENTE el mismo nucleo.py
que la ventana grafica: eso demuestra que la logica esta desacoplada
de la presentacion.
"""
import os
import time

import config

ANCHO_BARRA = 26


def _barra(porcentaje):
    porcentaje = max(0.0, min(porcentaje, 100.0))
    llenos = int(ANCHO_BARRA * porcentaje / 100)
    return "[" + "#" * llenos + "-" * (ANCHO_BARRA - llenos) + "]"


def _limpiar():
    os.system("cls" if os.name == "nt" else "clear")


FILAS = [
    ("cpu", "Uso de CPU"), ("memoria", "Memoria RAM"), ("disco", "Disco"),
    ("red", "Red"), ("procesos", "Procesos"), ("bateria", "Bateria"),
]


def ejecutar(nucleo):
    print("Iniciando nodo... Ctrl+C para terminar")
    try:
        while True:
            if nucleo.paso():
                _limpiar()
                datos = nucleo.instantanea()
                print(f" {config.ESTUDIANTE} | Cedula {config.CEDULA} | Grupo {config.SALON}")
                print("=" * 70)
                for clave, titulo in FILAS:
                    d = datos.get(clave)
                    if not d or not d["ok"]:
                        print(f" {titulo:<14}{'[' + '-' * ANCHO_BARRA + ']':<30} N/D")
                        print(f" {'':<14}{d['detalle'] if d else 'sin lectura'}")
                        continue
                    v = d["valor"]
                    if clave == "procesos":
                        pct, texto = min(v / 5.0, 100), f"{v:.0f} procs"
                    elif clave == "red":
                        pct = min(v / config.UMBRALES["red"]["alto"] * 100, 100)
                        texto = f"{v:.1f} KB/s"
                    else:
                        pct, texto = v, f"{v:.1f} %"
                    print(f" {titulo:<14}{_barra(pct):<30}{texto:>10}")
                    print(f" {'':<14}{d['detalle']}")
                print("-" * 70)
                print(" Ultimos eventos:")
                for e in nucleo.bitacora.ultimos(5):
                    print(f"  {e['hora']} [{e['nivel']:<6}] {e['mensaje'][:60]}")
                print("-" * 70)
                print(" Ctrl+C para terminar")
            time.sleep(0.2)
    except KeyboardInterrupt:
        print("\nNodo detenido por el usuario.")
