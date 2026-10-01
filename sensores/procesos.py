"""
Sensor de procesos.
Devuelve cuantos hay, cuales consumen mas y el CONJUNTO de PIDs activos.
El conjunto (set) permite detectar procesos que aparecen o desaparecen
usando diferencia de conjuntos, sin recorrer listas a mano.
"""
import psutil

NOMBRE = "procesos"


def leer():
    try:
        lista = []
        pids = {}
        for p in psutil.process_iter(["pid", "name", "cpu_percent", "memory_percent"]):
            try:
                info = p.info
                pids[info["pid"]] = info["name"] or "?"
                lista.append({
                    "pid": info["pid"],
                    "nombre": info["name"] or "?",
                    "cpu": info["cpu_percent"] or 0.0,
                    "ram": info["memory_percent"] or 0.0,
                })
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        lista.sort(key=lambda d: d["cpu"], reverse=True)
        top = lista[:7]
        mayor = top[0] if top else {"nombre": "-", "cpu": 0.0}
        return {
            "ok": True,
            "valor": float(len(lista)),
            "unidad": "procs",
            "top": top,
            "pids": set(pids.keys()),
            "nombres": pids,
            "detalle": f"mayor: {mayor['nombre']} ({mayor['cpu']:.0f}%)",
        }
    except Exception as e:
        return {"ok": False, "valor": None, "error": str(e)}
