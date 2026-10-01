"""
main.py
Punto de entrada del nodo de telemetria.

    python main.py             -> panel grafico (tkinter)
    python main.py --consola   -> panel de administracion por consola
"""
import sys

from nucleo import Nucleo


def main():
    nucleo = Nucleo()
    if "--consola" in sys.argv:
        from dashboard.consola import ejecutar
        ejecutar(nucleo)
    else:
        from dashboard.ventana import Ventana
        Ventana(nucleo).iniciar()


if __name__ == "__main__":
    main()
