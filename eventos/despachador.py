"""
Despachador de eventos.

En vez de una cadena gigante de if/elif, se guarda un diccionario
    { "tipo_de_evento": funcion_que_lo_atiende }
y al ocurrir un evento se busca la funcion en O(1) y se ejecuta.
Agregar un evento nuevo = registrar una funcion mas, sin tocar el bucle.
"""


class Despachador:
    def __init__(self):
        self.manejadores = {}
        self.suscriptores = []      # funciones que reciben TODOS los eventos ya formateados

    def registrar(self, tipo, funcion):
        """Asocia un tipo de evento con la funcion que lo atiende."""
        self.manejadores[tipo] = funcion

    def suscribir(self, funcion):
        """Agrega un observador (la bitacora, la ventana, la consola...)."""
        self.suscriptores.append(funcion)

    def emitir(self, tipo, datos=None):
        """Busca el manejador del tipo y lo ejecuta. Si no existe, usa el generico."""
        datos = datos or {}
        funcion = self.manejadores.get(tipo)
        if funcion is None:
            funcion = self.manejadores.get("desconocido")
        if funcion is None:
            return None
        evento = funcion(datos)
        if evento:
            evento["tipo"] = tipo
            evento["sensor"] = datos.get("sensor")   # LABORATORIO: las alertas sonoras distinguen cpu/memoria/red
            for s in self.suscriptores:
                s(evento)
        return evento

    def tipos_registrados(self):
        return sorted(self.manejadores.keys())
