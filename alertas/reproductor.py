# LABORATORIO: archivo nuevo del Laboratorio N.1
"""
alertas/reproductor.py
Reproductor de alertas que NUNCA bloquea el ciclo de monitoreo.

Se apoya en dos ideas ya vistas en el curso:

  1. Una COLA deque(maxlen=N). Cuando ocurre un evento, encolar() solo
     agrega el nombre del sonido y regresa: el manejador sigue siendo
     breve. Las alertas urgentes entran por el frente (appendleft).

  2. MARCAS DE TIEMPO, igual que nucleo.paso(). atender() se llama en
     cada vuelta del ciclo: si la alerta en curso todavia no termina
     (ahora < libre_desde) regresa enseguida sin esperar; si ya termino,
     saca la siguiente de la cola y la entrega al sistema operativo, que
     la toca en segundo plano. Nunca hay time.sleep().

El reloj y la salida de audio se pueden reemplazar, lo que permite
probar toda la logica en las pruebas unitarias sin hacer ruido.
"""
import time
from collections import deque

import config
from . import sonidos as audio


class Reproductor:
    def __init__(self, catalogo, salida=None, silencioso=None, reloj=None):
        self.catalogo = catalogo
        self.salida = salida or audio.reproducir
        self.silencioso = config.MODO_SILENCIOSO if silencioso is None else silencioso
        self.reloj = reloj or time.time
        self.cola = deque(maxlen=config.MAX_COLA_ALERTAS)
        self.actual = None            # alerta sonando en este momento
        self.libre_desde = None       # marca: cuando termina la alerta en curso
        self.ultima_vez = {}          # nombre -> marca, para el enfriamiento
        self.error = None             # ultimo problema con el dispositivo de audio

    # ------------------------------------------------------------------
    def encolar(self, nombre, ahora=None, forzar=False):
        """Agrega una alerta a la cola y regresa de inmediato.
        Devuelve True si se acepto. Se descarta si el sonido no existe,
        si ya esta esperando en la cola, o si sono hace muy poco.
        forzar=True (boton 'Probar sonidos') ignora el enfriamiento y la
        prioridad, para que suenen todos en el orden de config.py."""
        ahora = self.reloj() if ahora is None else ahora
        sonido = self.catalogo.get(nombre)
        if sonido is None or nombre in self.cola:
            return False
        ultima = self.ultima_vez.get(nombre)
        enfriando = ultima is not None and ahora - ultima < config.ENFRIAMIENTO_S
        if enfriando and not (forzar or sonido["prioridad"]):
            return False
        self.ultima_vez[nombre] = ahora
        if sonido["prioridad"] and not forzar:     # la prueba manual respeta el orden
            self.cola.appendleft(nombre)
        else:
            self.cola.append(nombre)
        return True

    # ------------------------------------------------------------------
    def atender(self, ahora=None):
        """Una vuelta del reproductor. No espera nunca.
        Devuelve el nombre de la alerta que empezo a sonar, o None."""
        ahora = self.reloj() if ahora is None else ahora
        if self.ocupado(ahora):
            return None
        self.actual = None
        if not self.cola:
            return None
        nombre = self.cola.popleft()
        sonido = self.catalogo[nombre]
        if not self.silencioso:
            try:
                self.salida(sonido["ruta"])
                self.error = None
            except Exception as e:      # sin parlantes no debe caerse el nodo
                self.error = str(e)
        self.actual = nombre
        self.libre_desde = ahora + sonido["duracion"] + config.PAUSA_ENTRE_ALERTAS_S
        return nombre

    def ocupado(self, ahora=None):
        ahora = self.reloj() if ahora is None else ahora
        return self.libre_desde is not None and ahora < self.libre_desde

    # ------------------------------------------------------------------
    def alternar_silencio(self):
        self.silencioso = not self.silencioso
        if self.silencioso:
            audio.detener()
        return self.silencioso

    def estado(self):
        return {
            "silencioso": self.silencioso,
            "actual": self.actual if self.ocupado() else None,
            "pendientes": list(self.cola),
            "error": self.error,
        }
