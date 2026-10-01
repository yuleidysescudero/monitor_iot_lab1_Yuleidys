# LABORATORIO: paquete nuevo del Laboratorio N.1
"""
Paquete alertas
---------------
Alertas sonoras del nodo: un sonido distinto para cada tipo de problema,
sin congelar el dashboard.

    sonidos.py     convierte las notas de config.py en archivos WAV y los
                   entrega al sistema operativo (reproduccion asincrona)
    reproductor.py cola deque + marcas de tiempo: decide CUANDO suena
                   cada alerta sin bloquear el ciclo
    gestor.py      suscriptor del despachador: decide QUE sonido le toca
                   a cada evento
"""
from .sonidos import generar_sonidos
from .reproductor import Reproductor
from .gestor import GestorAlertas


def crear_alertas(silencioso=None, carpeta=None):
    """Genera los sonidos y devuelve el gestor listo para suscribirse."""
    catalogo = generar_sonidos(carpeta)
    return GestorAlertas(Reproductor(catalogo, silencioso=silencioso))
