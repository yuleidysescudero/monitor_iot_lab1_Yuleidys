"""
Detectores: los cuatro patrones de deteccion vistos en clase.

1. DetectorUmbral  -> umbral con histeresis
2. DetectorFlanco  -> cambio de un estado discreto (si/no)
3. DetectorTiempo  -> cada N segundos, sin bloquear el programa
4. DetectorFalla   -> el sensor no responde o desaparece
(+ DetectorSalto y DetectorConjunto como variantes de flanco)
"""
import time
from collections import deque


class DetectorUmbral:
    """
    Histeresis: se activa al pasar 'alto' y solo se apaga al bajar de 'bajo'.
    Asi un valor que oscila alrededor del umbral no genera decenas de alertas.
    """

    def __init__(self, nombre, alto, bajo):
        self.nombre = nombre
        self.alto = alto
        self.bajo = bajo
        self.activo = False

    def revisar(self, valor):
        if valor is None:
            return None
        if not self.activo and valor >= self.alto:
            self.activo = True
            return ("umbral_superado", {"sensor": self.nombre, "valor": valor, "umbral": self.alto})
        if self.activo and valor <= self.bajo:
            self.activo = False
            return ("umbral_normalizado", {"sensor": self.nombre, "valor": valor, "umbral": self.bajo})
        return None


class DetectorFlanco:
    """Dispara solo cuando un estado discreto CAMBIA (falso->verdadero o al reves)."""

    def __init__(self, nombre):
        self.nombre = nombre
        self.anterior = None

    def revisar(self, estado, extra=None):
        if estado is None:
            return None
        if self.anterior is None:
            self.anterior = estado
            return None
        if estado != self.anterior:
            self.anterior = estado
            return ("flanco", {"sensor": self.nombre, "estado": estado, "extra": extra or {}})
        return None


class DetectorSalto:
    """Variacion brusca entre dos muestras consecutivas."""

    def __init__(self, nombre, delta):
        self.nombre = nombre
        self.delta = delta
        self.anterior = None

    def revisar(self, valor):
        if valor is None:
            return None
        if self.anterior is None:
            self.anterior = valor
            return None
        salto = abs(valor - self.anterior)
        previo = self.anterior
        self.anterior = valor
        if salto >= self.delta:
            return ("salto_anomalo", {"sensor": self.nombre, "antes": previo, "ahora": valor})
        return None


class DetectorTiempo:
    """
    Evento periodico SIN time.sleep(): compara marcas de tiempo.
    Asi el programa sigue atendiendo la interfaz mientras espera.
    """

    def __init__(self, nombre, periodo):
        self.nombre = nombre
        self.periodo = periodo
        self.ultima = time.time()

    def revisar(self, ahora=None):
        ahora = ahora or time.time()
        if ahora - self.ultima >= self.periodo:
            self.ultima = ahora
            return ("temporizado", {"sensor": self.nombre, "periodo": self.periodo})
        return None


class DetectorFalla:
    """Si el sensor devuelve error o no entrega datos durante N segundos, avisa una sola vez."""

    def __init__(self, nombre, tiempo_max):
        self.nombre = nombre
        self.tiempo_max = tiempo_max
        self.ultima_ok = time.time()
        self.en_falla = False

    def revisar(self, lectura):
        ahora = time.time()
        if lectura.get("ok"):
            self.ultima_ok = ahora
            if self.en_falla:
                self.en_falla = False
                return ("sensor_recuperado", {"sensor": self.nombre})
            return None
        if not self.en_falla and (ahora - self.ultima_ok) >= self.tiempo_max:
            self.en_falla = True
            return ("sensor_ausente", {"sensor": self.nombre,
                                       "error": lectura.get("error", "sin datos")})
        return None


class DetectorConjunto:
    """Procesos que aparecen o desaparecen, usando diferencia de conjuntos."""

    def __init__(self, nombre):
        self.nombre = nombre
        self.anterior = None

    def revisar(self, actual, nombres=None):
        nombres = nombres or {}
        if self.anterior is None:
            self.anterior = actual
            return []
        nuevos = actual - self.anterior
        idos = self.anterior - actual
        self.anterior = actual
        salida = []
        for pid in list(nuevos)[:3]:
            salida.append(("proceso_nuevo", {"pid": pid, "nombre": nombres.get(pid, "?")}))
        for pid in list(idos)[:3]:
            salida.append(("proceso_terminado", {"pid": pid, "nombre": "proceso " + str(pid)}))
        return salida


class VentanaMovil:
    """deque(maxlen=N): guarda solo las ultimas N muestras y descarta el resto sola."""

    def __init__(self, n):
        self.datos = deque(maxlen=n)

    def agregar(self, valor):
        if valor is not None:
            self.datos.append(valor)

    def resumen(self):
        if not self.datos:
            return None
        return {
            "n": len(self.datos),
            "min": round(min(self.datos), 2),
            "max": round(max(self.datos), 2),
            "prom": round(sum(self.datos) / len(self.datos), 2),
        }
