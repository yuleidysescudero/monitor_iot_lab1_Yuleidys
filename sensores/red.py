"""
Sensor de red.
psutil entrega contadores acumulados; aqui se convierten en velocidad (KB/s)
guardando la lectura anterior. Es el mismo truco que usa un sensor de flujo.
"""
import time
import psutil

NOMBRE = "red"

_anterior = None
_t_anterior = None


def leer():
    global _anterior, _t_anterior
    try:
        c = psutil.net_io_counters()
        ahora = time.time()
        if _anterior is None:
            _anterior, _t_anterior = c, ahora
            return {"ok": True, "valor": 0.0, "unidad": "KB/s", "sube": 0.0,
                    "baja": 0.0, "total_mb": round((c.bytes_sent + c.bytes_recv) / 1048576),
                    "detalle": "midiendo..."}
        dt = max(ahora - _t_anterior, 0.001)
        sube = (c.bytes_sent - _anterior.bytes_sent) / 1024 / dt
        baja = (c.bytes_recv - _anterior.bytes_recv) / 1024 / dt
        _anterior, _t_anterior = c, ahora
        total_mb = round((c.bytes_sent + c.bytes_recv) / 1048576)
        return {
            "ok": True,
            "valor": round(sube + baja, 1),
            "unidad": "KB/s",
            "sube": round(sube, 1),
            "baja": round(baja, 1),
            "total_mb": total_mb,
            "detalle": f"sube {sube:.1f} | baja {baja:.1f} KB/s | total {total_mb} MB",
        }
    except Exception as e:
        return {"ok": False, "valor": None, "error": str(e)}
