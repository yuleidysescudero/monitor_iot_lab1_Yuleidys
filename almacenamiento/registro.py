"""
registro.py
Estrategia de datos de un dispositivo IoT: MEDIR -> ACUMULAR -> RESUMIR -> ENVIAR -> VACIAR.
Aqui "enviar" es escribir en bitacora.json, que hace de servidor local.
"""
import json
import os
import time
from collections import deque

import config


class Bitacora:
    def __init__(self, archivo=None):
        self.archivo = archivo or config.ARCHIVO_BITACORA
        self.eventos = deque(maxlen=config.MAX_EVENTOS_MEMORIA)
        self.reportes = 0

    # ---------- eventos ----------
    def agregar(self, evento):
        self.eventos.append(evento)

    def ultimos(self, n=12):
        return list(self.eventos)[-n:]

    def limpiar(self):
        self.eventos.clear()

    # ---------- reportes ----------
    def guardar_reporte(self, resumenes):
        """Escribe el resumen del periodo y devuelve cuantas metricas guardo."""
        reporte = {
            "nodo": config.NOMBRE_NODO,
            "ubicacion": config.UBICACION,
            "estudiante": config.ESTUDIANTE,
            "cedula": config.CEDULA,
            "hora": time.strftime("%Y-%m-%d %H:%M:%S"),
            "metricas": resumenes,
        }
        historial = []
        if os.path.exists(self.archivo):
            try:
                with open(self.archivo, "r", encoding="utf-8") as f:
                    historial = json.load(f)
                if not isinstance(historial, list):
                    historial = [historial]
            except (json.JSONDecodeError, OSError):
                historial = []
        historial.append(reporte)
        with open(self.archivo, "w", encoding="utf-8") as f:
            json.dump(historial, f, indent=2, ensure_ascii=False)
        self.reportes += 1
        return len(resumenes)

    def exportar_eventos(self, archivo="eventos.json"):
        with open(archivo, "w", encoding="utf-8") as f:
            json.dump(list(self.eventos), f, indent=2, ensure_ascii=False)
        return archivo
