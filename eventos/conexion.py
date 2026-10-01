# LABORATORIO: archivo nuevo del Laboratorio N.1
"""
eventos/conexion.py
Eventos de la conexion de red. NO se escribio un detector nuevo: se
reutilizan, sin modificarlos, los dos detectores de detectores.py.

    DetectorFlanco  -> red_desconectada / red_conectada
                       (evento por FLANCO: cambia un estado si/no)
    DetectorTiempo  -> red_sigue_desconectada
                       (evento por TIEMPO: solo existe mientras la red
                        esta caida y se reinicia en cada caida)

revisar() devuelve una LISTA de pares (tipo, datos), igual que
DetectorConjunto, para que el nucleo los emita uno por uno.
"""
import time

import config
from .detectores import DetectorFlanco, DetectorTiempo

SENSOR = "conexion"


class MonitorConexion:
    def __init__(self, periodo=None):
        self.periodo = config.RECORDATORIO_RED_S if periodo is None else periodo
        self.flanco = DetectorFlanco(SENSOR)
        self.recordatorio = None      # DetectorTiempo vivo solo mientras no hay red
        self.caida_desde = None       # marca de tiempo del inicio de la caida
        self.ultima_interfaz = None   # por donde salia el equipo antes de caer

    def conectado(self):
        return self.flanco.anterior

    def revisar(self, conectado, ahora=None, interfaz=None):
        ahora = time.time() if ahora is None else ahora
        primera = self.flanco.anterior is None
        cambio = self.flanco.revisar(conectado)

        # Si el nodo ARRANCA sin red no hay flanco (no hay estado anterior),
        # pero el tecnico igual debe enterarse.
        if cambio or (primera and not conectado):
            evento = self._transicion(conectado, ahora, interfaz)
        elif self.recordatorio and self.recordatorio.revisar(ahora):
            evento = ("red_sigue_desconectada",
                      {"sensor": SENSOR, "segundos": ahora - self.caida_desde})
        else:
            evento = None

        if conectado:
            self.ultima_interfaz = interfaz
        return [evento] if evento else []

    def _transicion(self, conectado, ahora, interfaz):
        if conectado:
            segundos = ahora - self.caida_desde
            self.caida_desde = None
            self.recordatorio = None
            return ("red_conectada",
                    {"sensor": SENSOR, "interfaz": interfaz, "segundos": segundos})
        self.caida_desde = ahora
        self.recordatorio = DetectorTiempo("recordatorio_red", self.periodo)
        self.recordatorio.ultima = ahora    # el periodo cuenta desde la caida
        return ("red_desconectada",
                {"sensor": SENSOR, "interfaz": self.ultima_interfaz})
