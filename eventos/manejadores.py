"""
Manejadores: una funcion por tipo de evento.
Cada una recibe los datos del detector y devuelve el evento ya formateado
(nivel + mensaje). El despachador es quien decide cual llamar.
"""
import time
import config


def _evento(nivel, mensaje):
    return {"hora": time.strftime("%H:%M:%S"), "nivel": nivel, "mensaje": mensaje}


ETIQUETAS = {
    "cpu": "CPU", "memoria": "Memoria RAM", "disco": "Disco",
    "red": "Red", "procesos": "Procesos", "bateria": "Bateria",
}


def umbral_superado(d):
    nombre = ETIQUETAS.get(d["sensor"], d["sensor"])
    return _evento(config.ALERTA, f"{nombre} al {d['valor']:.1f}% (umbral {d['umbral']:.0f}%)")


def umbral_normalizado(d):
    nombre = ETIQUETAS.get(d["sensor"], d["sensor"])
    return _evento(config.INFO, f"{nombre} volvio a la normalidad ({d['valor']:.1f}%)")


def flanco(d):
    extra = d.get("extra", {})
    if d["sensor"] == "cargador":
        estado = "conectado" if d["estado"] else "desconectado"
        return _evento(config.AVISO, f"Cargador {estado} ({extra.get('nivel', 0):.0f}%)")
    if d["sensor"] == "swap":
        if d["estado"]:
            return _evento(config.AVISO, "El sistema empezo a usar memoria de intercambio")
        return _evento(config.INFO, "El sistema dejo de usar memoria de intercambio")
    estado = "activo" if d["estado"] else "inactivo"
    return _evento(config.AVISO, f"Cambio de estado en {d['sensor']}: {estado}")


def salto_anomalo(d):
    nombre = ETIQUETAS.get(d["sensor"], d["sensor"])
    return _evento(config.AVISO,
                   f"Variacion brusca en {nombre}: de {d['antes']:.1f} a {d['ahora']:.1f}")


def nucleo_saturado(d):
    return _evento(config.AVISO, f"Nucleo {d['nucleo']} saturado ({d['valor']:.1f}%)")


def nucleo_liberado(d):
    return _evento(config.INFO, f"Nucleo {d['nucleo']} liberado")


def temporizado(d):
    return _evento(config.INFO, f"Reporte guardado en {config.ARCHIVO_BITACORA} "
                                f"({d.get('metricas', 0)} metricas)")


def sensor_ausente(d):
    nombre = ETIQUETAS.get(d["sensor"], d["sensor"])
    return _evento(config.ALERTA, f"Sensor {nombre} sin respuesta: {d.get('error', '')}")


def sensor_recuperado(d):
    nombre = ETIQUETAS.get(d["sensor"], d["sensor"])
    return _evento(config.INFO, f"Sensor {nombre} recuperado")


def proceso_nuevo(d):
    return _evento(config.INFO, f"Proceso iniciado: {d['nombre']}")


def proceso_terminado(d):
    return _evento(config.INFO, f"Proceso terminado: {d['nombre']}")


def bateria_baja(d):
    return _evento(config.ALERTA, f"Bateria baja: {d['valor']:.0f}%")


def inicio(d):
    return _evento(config.INFO, f"Nodo {config.NOMBRE_NODO} iniciado | "
                                f"sensores activos: {d.get('sensores', '')}")


def desconocido(d):
    return _evento(config.INFO, f"Evento sin manejador: {d}")


# ---- LABORATORIO: eventos de conexion de red y de alertas sonoras ----
def red_desconectada(d):                                              # LABORATORIO
    origen = f" (salia por {d['interfaz']})" if d.get("interfaz") else ""
    return _evento(config.ALERTA, f"Conexion de red perdida{origen}")


def red_conectada(d):                                                 # LABORATORIO
    return _evento(config.INFO, f"Conexion de red recuperada por {d.get('interfaz')} "
                                f"tras {d['segundos']:.0f} s sin red")


def red_sigue_desconectada(d):                                        # LABORATORIO
    return _evento(config.AVISO, f"La red sigue desconectada "
                                 f"({d['segundos']:.0f} s sin conexion)")


def alerta_sonora(d):                                                 # LABORATORIO
    modo = " [modo silencioso: no suena]" if d.get("silencio") else ""
    return _evento(config.SONIDO, f"Alerta sonora: {d['descripcion']}{modo}")


# ---- tabla que consume el despachador ----
TABLA = {
    "umbral_superado": umbral_superado,
    "umbral_normalizado": umbral_normalizado,
    "flanco": flanco,
    "salto_anomalo": salto_anomalo,
    "nucleo_saturado": nucleo_saturado,
    "nucleo_liberado": nucleo_liberado,
    "temporizado": temporizado,
    "sensor_ausente": sensor_ausente,
    "sensor_recuperado": sensor_recuperado,
    "proceso_nuevo": proceso_nuevo,
    "proceso_terminado": proceso_terminado,
    "bateria_baja": bateria_baja,
    "inicio": inicio,
    "desconocido": desconocido,
    "red_desconectada": red_desconectada,               # LABORATORIO
    "red_conectada": red_conectada,                     # LABORATORIO
    "red_sigue_desconectada": red_sigue_desconectada,   # LABORATORIO
    "alerta_sonora": alerta_sonora,                     # LABORATORIO
}
