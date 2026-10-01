"""
generador.py
Genera carga controlada en el equipo para PROVOCAR cada evento a voluntad
y poder tomar las capturas de pantalla sin esperar a que ocurran solas.

    python generador.py

Se ejecuta en una terminal aparte, con el monitor ya abierto en otra.
"""
import multiprocessing
import os
import time


# ---------------------------------------------------------------
def _quemar(fin):
    while time.time() < fin:
        pass


def cargar_cpu(segundos=15):
    """Ocupa todos los nucleos al 100 %: dispara umbral de CPU y nucleo saturado."""
    n = multiprocessing.cpu_count()
    print(f"Cargando {n} nucleo(s) durante {segundos} s...")
    fin = time.time() + segundos
    procesos = [multiprocessing.Process(target=_quemar, args=(fin,)) for _ in range(n)]
    for p in procesos:
        p.start()
    for p in procesos:
        p.join()
    print("Carga de CPU terminada (observa el evento de variacion brusca al bajar).")


def ocupar_memoria(mb=1500, segundos=15):
    """Reserva memoria RAM para acercarse al umbral de memoria."""
    print(f"Reservando ~{mb} MB durante {segundos} s...")
    bloques = []
    try:
        for _ in range(mb // 50):
            bloques.append(bytearray(50 * 1024 * 1024))
        time.sleep(segundos)
    except MemoryError:
        print("El sistema no permitio reservar mas memoria.")
    finally:
        bloques.clear()
        print("Memoria liberada.")


def llenar_disco(mb=800):
    """Crea y borra un archivo temporal: mueve el porcentaje de disco."""
    ruta = "relleno_temporal.bin"
    print(f"Escribiendo {mb} MB en {ruta}...")
    with open(ruta, "wb") as f:
        for _ in range(mb):
            f.write(os.urandom(1024 * 1024))
    time.sleep(10)
    os.remove(ruta)
    print("Archivo temporal eliminado.")


def abrir_cerrar_procesos(cantidad=5):
    """Abre y cierra procesos: dispara proceso_nuevo / proceso_terminado."""
    print(f"Abriendo {cantidad} procesos temporales...")
    procesos = [multiprocessing.Process(target=time.sleep, args=(6,)) for _ in range(cantidad)]
    for p in procesos:
        p.start()
    time.sleep(7)
    for p in procesos:
        p.join()
    print("Procesos cerrados.")


def secuencia_completa():
    cargar_cpu(12)
    time.sleep(4)
    ocupar_memoria(1200, 12)
    time.sleep(4)
    abrir_cerrar_procesos()
    print("Secuencia completa terminada.")


MENU = """
=== Generador de eventos ===
  1. Cargar CPU                     (evento por umbral)
  2. Ocupar memoria                 (evento por umbral)
  3. Llenar disco temporal          (evento por umbral)
  4. Abrir y cerrar procesos        (evento por aparicion/desaparicion)
  5. Secuencia completa
  0. Salir

Recuerda: el cargador de la laptop se conecta y desconecta a mano;
ese es el evento de flanco y no necesita este programa.
"""


def main():
    while True:
        print(MENU)
        opcion = input("Opcion: ").strip()
        if opcion == "1":
            cargar_cpu()
        elif opcion == "2":
            ocupar_memoria()
        elif opcion == "3":
            llenar_disco()
        elif opcion == "4":
            abrir_cerrar_procesos()
        elif opcion == "5":
            secuencia_completa()
        elif opcion == "0":
            break
        else:
            print("Opcion no valida.")


if __name__ == "__main__":
    multiprocessing.freeze_support()
    main()
