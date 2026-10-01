"""Sensor de procesador."""
import psutil

NOMBRE = "cpu"


def leer():
    """Devuelve el uso global de CPU, el uso por nucleo y la frecuencia."""
    try:
        global_pct = psutil.cpu_percent(interval=None)
        por_nucleo = psutil.cpu_percent(interval=None, percpu=True)
        try:
            freq = psutil.cpu_freq()
            mhz = round(freq.current) if freq else 0
        except Exception:
            mhz = 0
        return {
            "ok": True,
            "valor": global_pct,              # valor principal que vigilan los detectores
            "unidad": "%",
            "nucleos": psutil.cpu_count(logical=True),
            "por_nucleo": por_nucleo,
            "mhz": mhz,
            "detalle": f"{psutil.cpu_count(logical=True)} nucleos | {mhz} MHz",
        }
    except Exception as e:
        return {"ok": False, "valor": None, "error": str(e)}
