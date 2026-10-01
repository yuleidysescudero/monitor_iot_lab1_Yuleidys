"""
main.py
Punto de entrada del nodo de telemetria.

    python main.py             -> panel grafico (tkinter)
    python main.py --consola   -> panel de administracion por consola
    python main.py --silencio  -> modo silencioso: alertas solo visuales (LABORATORIO)
    python -m unittest discover -s pruebas -v   -> pruebas unitarias   (LABORATORIO)
"""
import sys

from nucleo import Nucleo


def main():
    silencio = True if "--silencio" in sys.argv else None      # LABORATORIO: None = lo que diga config.py
    nucleo = Nucleo(silencioso=silencio)                         # LABORATORIO
    if "--consola" in sys.argv:
        from dashboard.consola import ejecutar
        ejecutar(nucleo)
    else:
        from dashboard.ventana import Ventana
        Ventana(nucleo).iniciar()


if __name__ == "__main__":
    main()
