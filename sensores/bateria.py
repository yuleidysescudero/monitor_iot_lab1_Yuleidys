"""
Sensor de bateria.
En equipos de escritorio psutil devuelve None: ese caso se reporta como
sensor AUSENTE, que es justamente uno de los eventos que pide la actividad.
"""
import psutil

NOMBRE = "bateria"


def leer():
    try:
        b = psutil.sensors_battery()
        if b is None:
            return {"ok": False, "valor": None, "error": "sensor de bateria no disponible"}
        if b.power_plugged:
            detalle = "conectado a la corriente"
        elif b.secsleft and b.secsleft > 0:
            h, m = divmod(int(b.secsleft) // 60, 60)
            detalle = f"en bateria | quedan {h}h {m}m"
        else:
            detalle = "en bateria"
        return {
            "ok": True,
            "valor": round(b.percent, 1),
            "unidad": "%",
            "enchufado": bool(b.power_plugged),
            "detalle": detalle,
        }
    except Exception as e:
        return {"ok": False, "valor": None, "error": str(e)}
