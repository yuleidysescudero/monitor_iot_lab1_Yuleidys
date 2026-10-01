"""
Paquete sensores
----------------
Un modulo por cada magnitud fisica que mide el nodo.
Todos exponen la misma funcion leer() que devuelve un diccionario,
de modo que el nucleo los puede tratar a todos por igual.
"""
from . import cpu, memoria, disco, red, procesos, bateria
from . import conexion          # LABORATORIO: nuevo sensor (conectado si/no)

SENSORES = {
    "cpu": cpu,
    "memoria": memoria,
    "disco": disco,
    "red": red,
    "procesos": procesos,
    "bateria": bateria,
    "conexion": conexion,       # LABORATORIO
}
