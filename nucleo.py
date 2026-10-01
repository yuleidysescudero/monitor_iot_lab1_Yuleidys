"""
nucleo.py
Motor del nodo de telemetria. NO dibuja nada: solo mide, detecta y emite eventos.
Gracias a eso la misma logica sirve para la ventana grafica y para la consola.

Bucle no bloqueante: se llama a paso() una y otra vez; el metodo compara marcas
de tiempo y decide si ya toca muestrear, en lugar de usar time.sleep().
"""
import time

import config
from sensores import SENSORES
from eventos.despachador import Despachador
from eventos import manejadores
from eventos.detectores import (
    DetectorUmbral, DetectorFlanco, DetectorSalto,
    DetectorTiempo, DetectorFalla, DetectorConjunto, VentanaMovil,
)
from almacenamiento import Bitacora
from eventos.conexion import MonitorConexion    # LABORATORIO
from alertas import crear_alertas               # LABORATORIO


class Nucleo:
    def __init__(self, silencioso=None):        # LABORATORIO: parametro del modo silencioso
        self.bitacora = Bitacora()
        self.despachador = Despachador()
        for tipo, funcion in manejadores.TABLA.items():
            self.despachador.registrar(tipo, funcion)
        self.despachador.suscribir(self.bitacora.agregar)
        # LABORATORIO: nueva reaccion a los eventos. El gestor de alertas se
        # suscribe igual que la bitacora; sensores y detectores no cambian.
        self.alertas = crear_alertas(silencioso)                    # LABORATORIO
        self.despachador.suscribir(self.alertas.atender_evento)     # LABORATORIO
        self.conexion = MonitorConexion()                           # LABORATORIO

        # --- detectores por umbral (con histeresis) ---
        self.umbrales = {
            n: DetectorUmbral(n, u["alto"], u["bajo"])
            for n, u in config.UMBRALES.items()
        }
        # --- detectores por flanco ---
        self.flanco_cargador = DetectorFlanco("cargador")
        self.flanco_swap = DetectorFlanco("swap")
        self.saltos = {n: DetectorSalto(n, config.SALTO_ANOMALO) for n in ("cpu", "memoria")}
        self.conjunto_procesos = DetectorConjunto("procesos")
        self.nucleos_saturados = set()
        # --- detector por tiempo ---
        self.temporizador = DetectorTiempo("reporte", config.PERIODO_REPORTE)
        # --- detectores por falla o ausencia ---
        self.fallas = {n: DetectorFalla(n, config.TIEMPO_MAX_SIN_DATOS) for n in SENSORES}

        # ventanas moviles para el resumen estadistico
        self.ventanas = {n: VentanaMovil(config.TAMANO_VENTANA) for n in SENSORES}

        self.lecturas = {}
        self.ultima_muestra = 0.0
        self.ultima_lenta = None          # LABORATORIO: marca de los sensores lentos
        self.pausado = False
        self.bateria_avisada = False

        # Lectura de calentamiento: psutil calcula porcentajes comparando con la
        # lectura anterior, asi que la primera siempre sale distorsionada.
        # Se descarta para no generar alertas falsas al arrancar.
        for modulo in SENSORES.values():
            try:
                modulo.leer()
            except Exception:
                pass
        time.sleep(config.CALENTAMIENTO_S)     # LABORATORIO: el 0.3 paso a config.py
        self.despachador.emitir("inicio", {"sensores": ", ".join(SENSORES)})

    # ------------------------------------------------------------------
    def paso(self):
        """Se llama continuamente. Devuelve True si hubo muestreo en esta pasada."""
        ahora = time.time()
        # LABORATORIO: el reproductor se atiende en CADA llamada, antes de
        # decidir si toca muestrear, y aunque el monitoreo este en pausa.
        self._atender_sonido(ahora)                                 # LABORATORIO
        if self.pausado or (ahora - self.ultima_muestra) < config.INTERVALO_MUESTREO:
            return False
        self.ultima_muestra = ahora
        # LABORATORIO: los sensores caros solo se leen cada PERIODO_LENTO
        toca_lento = (self.ultima_lenta is None
                      or ahora - self.ultima_lenta >= config.PERIODO_LENTO)  # LABORATORIO
        if toca_lento:                                                       # LABORATORIO
            self.ultima_lenta = ahora                                        # LABORATORIO

        for nombre, modulo in SENSORES.items():
            if nombre in config.SENSORES_LENTOS and not toca_lento:         # LABORATORIO
                continue                                                     # LABORATORIO
            lectura = modulo.leer()
            self.lecturas[nombre] = lectura

            # 4) evento por falla o ausencia
            r = self.fallas[nombre].revisar(lectura)
            if r:
                self.despachador.emitir(*r)
            if not lectura.get("ok"):
                continue

            valor = lectura.get("valor")
            self.ventanas[nombre].agregar(valor)

            # 1) evento por umbral con histeresis
            if nombre in self.umbrales:
                r = self.umbrales[nombre].revisar(valor)
                if r:
                    self.despachador.emitir(*r)

            # 2) evento por flanco / variacion brusca
            if nombre in self.saltos:
                r = self.saltos[nombre].revisar(valor)
                if r:
                    self.despachador.emitir(*r)

        self._eventos_especiales()
        self._eventos_conexion(ahora)                               # LABORATORIO

        # 3) evento por tiempo
        r = self.temporizador.revisar(ahora)
        if r:
            self._guardar_reporte()
        return True

    # ------------------------------------------------------------------
    def _eventos_especiales(self):
        bat = self.lecturas.get("bateria", {})
        if bat.get("ok"):
            r = self.flanco_cargador.revisar(bat["enchufado"], {"nivel": bat["valor"]})
            if r:
                self.despachador.emitir(*r)
            if bat["valor"] <= config.BATERIA_BAJA and not bat["enchufado"]:
                if not self.bateria_avisada:
                    self.bateria_avisada = True
                    self.despachador.emitir("bateria_baja", {"valor": bat["valor"]})
            else:
                self.bateria_avisada = False

        mem = self.lecturas.get("memoria", {})
        if mem.get("ok"):
            r = self.flanco_swap.revisar(mem["swap"] > 0)
            if r:
                self.despachador.emitir(*r)

        cpu = self.lecturas.get("cpu", {})
        if cpu.get("ok"):
            for i, v in enumerate(cpu.get("por_nucleo", [])):
                if v >= config.UMBRAL_NUCLEO_SATURADO and i not in self.nucleos_saturados:
                    self.nucleos_saturados.add(i)
                    self.despachador.emitir("nucleo_saturado", {"nucleo": i, "valor": v})
                elif v < config.UMBRAL_NUCLEO_SATURADO - config.HISTERESIS_NUCLEO and i in self.nucleos_saturados:  # LABORATORIO
                    self.nucleos_saturados.discard(i)
                    self.despachador.emitir("nucleo_liberado", {"nucleo": i})

        pro = self.lecturas.get("procesos", {})
        if pro.get("ok"):
            for tipo, datos in self.conjunto_procesos.revisar(pro["pids"], pro["nombres"]):
                self.despachador.emitir(tipo, datos)

    # ------------------------------------------------------------------
    # LABORATORIO: conexion de red y alertas sonoras
    # ------------------------------------------------------------------
    def _eventos_conexion(self, ahora):                             # LABORATORIO
        con = self.lecturas.get("conexion", {})
        if con.get("ok"):
            for tipo, datos in self.conexion.revisar(con["conectado"], ahora,
                                                     con.get("interfaz")):
                self.despachador.emitir(tipo, datos)

    def _atender_sonido(self, ahora):                               # LABORATORIO
        """Si termino la alerta anterior, arranca la siguiente de la cola.
        Regresa enseguida: el sonido lo toca el sistema operativo."""
        reproductor = self.alertas.reproductor
        nombre = reproductor.atender(ahora)
        if nombre:
            self.despachador.emitir("alerta_sonora", {
                "sonido": nombre,
                "descripcion": reproductor.catalogo[nombre]["descripcion"],
                "silencio": reproductor.silencioso,
            })

    def alternar_silencio(self):                                    # LABORATORIO
        return self.alertas.reproductor.alternar_silencio()

    def probar_sonidos(self):                                       # LABORATORIO
        self.alertas.probar()

    def estado_alertas(self):                                       # LABORATORIO
        """Lo que el dashboard necesita saber de la red y del sonido."""
        estado = self.alertas.reproductor.estado()
        estado["conectado"] = self.conexion.conectado()
        estado["red_detalle"] = self.lecturas.get("conexion", {}).get("detalle", "")
        return estado

    # ------------------------------------------------------------------
    def _guardar_reporte(self):
        resumenes = {}
        for nombre, ventana in self.ventanas.items():
            r = ventana.resumen()
            if r:
                resumenes[nombre] = r
        n = self.bitacora.guardar_reporte(resumenes)
        self.despachador.emitir("temporizado", {"metricas": n})
        for ventana in self.ventanas.values():   # vaciar: cierra el ciclo IoT
            ventana.datos.clear()

    # ------------------------------------------------------------------
    def generar_reporte_manual(self):
        self._guardar_reporte()

    def alternar_pausa(self):
        self.pausado = not self.pausado
        return self.pausado

    def instantanea(self):
        """Ultimo valor de cada sensor, listo para dibujar."""
        salida = {}
        for nombre, lectura in self.lecturas.items():
            salida[nombre] = {
                "ok": lectura.get("ok", False),
                "valor": lectura.get("valor"),
                "unidad": lectura.get("unidad", ""),
                "detalle": lectura.get("detalle", lectura.get("error", "")),
            }
        return salida
