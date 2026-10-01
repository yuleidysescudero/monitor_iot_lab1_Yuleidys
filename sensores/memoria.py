"""Sensor de memoria RAM y memoria de intercambio (swap)."""
import psutil

NOMBRE = "memoria"


def leer():
    try:
        v = psutil.virtual_memory()
        s = psutil.swap_memory()
        gb = 1024 ** 3
        return {
            "ok": True,
            "valor": v.percent,
            "unidad": "%",
            "usada_gb": round(v.used / gb, 1),
            "total_gb": round(v.total / gb, 1),
            "swap": s.percent,
            "detalle": f"{round(v.used/gb,1)} de {round(v.total/gb,1)} GB | swap {s.percent:.0f}%",
        }
    except Exception as e:
        return {"ok": False, "valor": None, "error": str(e)}
