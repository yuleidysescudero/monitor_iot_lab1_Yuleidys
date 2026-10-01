# LABORATORIO: archivo nuevo del Laboratorio N.1
"""
Sensor de conexion de red.

red.py mide CUANTO trafico pasa (KB/s), pero no dice SI el equipo esta
conectado: con la red caida tambien marca 0 KB/s, igual que con la red
ociosa. Este sensor responde la otra pregunta: conectado o no.

Tecnica: se "conecta" un socket UDP hacia una IP publica. En UDP,
connect() NO envia ningun paquete: solo le pide al sistema operativo que
elija la ruta de salida. Si no hay ruta (Wi-Fi apagado, cable fuera)
falla al instante con "red inalcanzable". Por eso es inmediato, no genera
trafico y no bloquea el ciclo de monitoreo.

Pero la ruta sola no basta: al desconectar el Wi-Fi, Windows conserva un
tiempo la IP y la ruta. Por eso se exige ademas que el adaptador por el
que sale esa ruta tenga enlace (net_if_stats().isup).

Revisar solo si las interfaces estan "activas" tampoco sirve: los
adaptadores virtuales (VirtualBox, Hyper-V) aparecen activos aunque no
haya red. Las dos condiciones juntas si responden bien.
"""
import socket

import psutil

import config

NOMBRE = "conexion"


def _interfaz_de(ip):
    """Nombre del adaptador que tiene asignada esa IP (Wi-Fi, Ethernet...)."""
    for nombre, direcciones in psutil.net_if_addrs().items():
        if any(d.address == ip for d in direcciones):
            return nombre
    return "desconocida"


def _desconectado(motivo, interfaz=None):
    """No es una falla del sensor: es la lectura "desconectado"."""
    return {
        "ok": True,
        "valor": float(False),
        "unidad": "",
        "conectado": False,
        "interfaz": interfaz,
        "ip": None,
        "detalle": motivo,
    }


def _enlace_activo(interfaz):
    """True si el adaptador tiene enlace. Si no se puede saber, se asume que si."""
    stats = psutil.net_if_stats().get(interfaz)
    return stats is None or stats.isup


def leer():
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.connect(config.DESTINO_RUTA)
            ip, _puerto = s.getsockname()
    except OSError:
        return _desconectado("sin ruta de salida")
    try:
        interfaz = _interfaz_de(ip)
        activo = _enlace_activo(interfaz)
    except Exception:
        interfaz, activo = "desconocida", True
    # Segunda condicion: al desconectar el Wi-Fi, Windows conserva unos
    # segundos (o minutos) la IP y la ruta, asi que connect() sigue
    # funcionando. Lo que si cambia al instante es el enlace del adaptador.
    if not activo:
        return _desconectado(f"{interfaz} sin enlace", interfaz)
    return {
        "ok": True,
        "valor": float(True),          # 1.0 / 0.0: el promedio = fraccion del tiempo con red
        "unidad": "",
        "conectado": True,
        "interfaz": interfaz,
        "ip": ip,
        "detalle": f"{interfaz} | {ip}",
    }
