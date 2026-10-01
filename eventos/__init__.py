"""
Paquete eventos
---------------
despachador.py : la tabla (diccionario) que asocia tipo de evento -> funcion
detectores.py  : las clases que deciden CUANDO ocurre un evento
manejadores.py : las funciones que deciden QUE hacer con cada evento
"""
from .despachador import Despachador
