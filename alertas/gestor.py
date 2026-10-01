# LABORATORIO: archivo nuevo del Laboratorio N.1
"""
alertas/gestor.py
La NUEVA REACCION a los eventos que pide el laboratorio.

GestorAlertas se suscribe al despachador igual que la bitacora: recibe
cada evento ya formateado y decide, con un diccionario de config.py, si
le corresponde un sonido. Por eso no fue necesario tocar ni un sensor ni
un detector: los eventos se siguen produciendo igual y aqui solo se
agrega una forma mas de reaccionar a ellos.
"""
import config


class GestorAlertas:
    def __init__(self, reproductor):
        self.reproductor = reproductor

    @staticmethod
    def sonido_para(evento):
        """Busca primero 'tipo:sensor' (umbral_superado:cpu) y luego solo
        'tipo' (red_desconectada). Sin if/elif: un diccionario."""
        tipo = evento.get("tipo")
        especifico = f"{tipo}:{evento.get('sensor')}"
        return config.SONIDO_POR_EVENTO.get(especifico,
                                            config.SONIDO_POR_EVENTO.get(tipo))

    def atender_evento(self, evento):
        """Suscriptor del despachador. Breve: solo encola, nunca suena aqui."""
        nombre = self.sonido_para(evento)
        if nombre:
            self.reproductor.encolar(nombre)
        return nombre

    def probar(self):
        """Encola todos los sonidos, uno tras otro (boton 'Probar sonidos')."""
        for nombre in config.SONIDOS:
            self.reproductor.encolar(nombre, forzar=True)
