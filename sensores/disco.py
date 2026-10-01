"""Sensor de disco: porcentaje ocupado de la particion principal."""
import os
import psutil

NOMBRE = "disco"
RAIZ = os.path.abspath(os.sep)   # "C:\\" en Windows, "/" en Linux


def leer():
    try:
        u = psutil.disk_usage(RAIZ)
        gb = 1024 ** 3
        return {
            "ok": True,
            "valor": u.percent,
            "unidad": "%",
            "libre_gb": round(u.free / gb, 1),
            "total_gb": round(u.total / gb, 1),
            "detalle": f"{round(u.free/gb,1)} GB libres de {round(u.total/gb,1)} GB",
        }
    except Exception as e:
        return {"ok": False, "valor": None, "error": str(e)}
