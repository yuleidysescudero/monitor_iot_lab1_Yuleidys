# LABORATORIO: archivo nuevo del Laboratorio N.1
"""
alertas/sonidos.py
Convierte la descripcion de cada sonido de config.py (lista de notas) en
un archivo WAV, y entrega ese archivo al sistema operativo para que suene.

Por que WAV + SND_ASYNC y no winsound.Beep():
    winsound.Beep(frecuencia, duracion) CONGELA el programa durante toda
    la nota, igual que time.sleep(). En cambio
    PlaySound(ruta, SND_FILENAME | SND_ASYNC) le pasa el archivo a Windows
    y regresa de inmediato: el sonido lo toca el sistema operativo
    mientras el ciclo de monitoreo sigue trabajando.

En macOS o Linux no existe winsound: se usa la campana del sistema.
"""
import math
import os
import sys
import wave
from array import array

import config

try:
    import winsound
except ImportError:          # macOS / Linux
    winsound = None

# 'h' = entero con signo de 16 bits, coincide con config.BYTES_POR_MUESTRA
TIPO_MUESTRA = "h"


def duracion_s(notas):
    """Cuanto dura una melodia, en segundos."""
    return sum(ms for _frecuencia, ms in notas) / config.MS_POR_SEGUNDO


def _onda(frecuencia, duracion_ms):
    """Muestras de una nota senoidal con rampa de entrada y salida.
    Con frecuencia = config.SILENCIO el seno vale cero: es una pausa."""
    tasa = config.FRECUENCIA_MUESTREO_AUDIO
    total = int(tasa * duracion_ms / config.MS_POR_SEGUNDO)
    rampa = int(tasa * config.FUNDIDO_MS / config.MS_POR_SEGUNDO) or total
    amplitud = config.AMPLITUD_MAXIMA * config.VOLUMEN
    return [
        int(amplitud * min(i, total - i, rampa) / rampa
            * math.sin(math.tau * frecuencia * i / tasa))
        for i in range(total)
    ]


def generar_wav(notas, ruta):
    """Escribe la melodia completa en un archivo WAV mono de 16 bits."""
    muestras = array(TIPO_MUESTRA)
    for frecuencia, ms in notas:
        muestras.extend(_onda(frecuencia, ms))
    with wave.open(ruta, "wb") as w:
        w.setnchannels(config.CANALES_AUDIO)
        w.setsampwidth(config.BYTES_POR_MUESTRA)
        w.setframerate(config.FRECUENCIA_MUESTREO_AUDIO)
        w.writeframes(muestras.tobytes())
    return ruta


def generar_sonidos(carpeta=None):
    """Genera un WAV por cada sonido de config.SONIDOS.

    Se hace UNA sola vez al arrancar (no dentro del ciclo). Como se
    regeneran en cada inicio, cambiar una nota en config.py cambia el
    sonido sin tocar nada mas.
    Devuelve {nombre: {ruta, duracion, descripcion, prioridad}}.
    """
    carpeta = carpeta or config.CARPETA_SONIDOS
    os.makedirs(carpeta, exist_ok=True)
    catalogo = {}
    for nombre, sonido in config.SONIDOS.items():
        ruta = os.path.abspath(os.path.join(carpeta, f"{nombre}.wav"))
        generar_wav(sonido["notas"], ruta)
        catalogo[nombre] = {
            "ruta": ruta,
            "duracion": duracion_s(sonido["notas"]),
            "descripcion": sonido["descripcion"],
            "prioridad": sonido["prioridad"],
        }
    return catalogo


def reproducir(ruta):
    """Empieza a sonar y regresa ENSEGUIDA (no espera a que termine)."""
    if winsound is not None:
        winsound.PlaySound(ruta, winsound.SND_FILENAME | winsound.SND_ASYNC
                           | winsound.SND_NODEFAULT)
    else:
        sys.stdout.write("\a")       # campana del sistema
        sys.stdout.flush()


def detener():
    """Corta el sonido que este en curso (al activar el modo silencioso)."""
    if winsound is not None:
        winsound.PlaySound(None, winsound.SND_PURGE)
