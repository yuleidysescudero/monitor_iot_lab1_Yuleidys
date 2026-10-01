# LABORATORIO: pruebas unitarias de los sonidos y de la reaccion a los eventos
import ast
import os
import pathlib
import tempfile
import unittest
import wave

import config
from alertas import GestorAlertas, Reproductor, generar_sonidos
from alertas.sonidos import duracion_s
from eventos import manejadores
from eventos.despachador import Despachador

RAIZ = pathlib.Path(__file__).resolve().parent.parent


class ReproductorEspia(Reproductor):
    """Reproductor que solo recuerda lo que le pidieron encolar."""
    def __init__(self):
        super().__init__({}, silencioso=True)
        self.pedidos = []

    def encolar(self, nombre, ahora=None, forzar=False):
        self.pedidos.append(nombre)
        return True


class PruebasSonidos(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory()
        cls.catalogo = generar_sonidos(cls.tmp.name)

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    def test_sonidos_obligatorios(self):
        """CPU, memoria, trafico de red y conexion tienen su propio sonido."""
        for nombre in ("cpu_alta", "memoria_alta", "trafico_alto",
                       "red_desconectada", "red_conectada", "red_sigue_desconectada"):
            self.assertIn(nombre, self.catalogo)

    def test_todos_los_sonidos_son_distintos(self):
        melodias = [tuple(s["notas"]) for s in config.SONIDOS.values()]
        self.assertEqual(len(melodias), len(set(melodias)))

    def test_wav_valido_y_con_la_duracion_de_config(self):
        for nombre, sonido in self.catalogo.items():
            with self.subTest(sonido=nombre):
                self.assertTrue(os.path.exists(sonido["ruta"]))
                with wave.open(sonido["ruta"], "rb") as w:
                    self.assertEqual(w.getframerate(), config.FRECUENCIA_MUESTREO_AUDIO)
                    self.assertEqual(w.getsampwidth(), config.BYTES_POR_MUESTRA)
                    segundos = w.getnframes() / w.getframerate()
                esperado = duracion_s(config.SONIDOS[nombre]["notas"])
                self.assertAlmostEqual(segundos, esperado, places=2)
                self.assertAlmostEqual(sonido["duracion"], esperado)


class PruebasGestor(unittest.TestCase):
    def setUp(self):
        self.gestor = GestorAlertas(ReproductorEspia())

    def evento(self, tipo, sensor=None):
        return {"tipo": tipo, "sensor": sensor, "nivel": config.ALERTA, "mensaje": ""}

    def test_cada_umbral_tiene_su_sonido(self):
        casos = {"cpu": "cpu_alta", "memoria": "memoria_alta", "red": "trafico_alto"}
        for sensor, sonido in casos.items():
            with self.subTest(sensor=sensor):
                self.assertEqual(self.gestor.atender_evento(
                    self.evento("umbral_superado", sensor)), sonido)

    def test_eventos_de_conexion(self):
        for tipo in ("red_desconectada", "red_conectada", "red_sigue_desconectada"):
            self.assertEqual(self.gestor.atender_evento(self.evento(tipo, "conexion")), tipo)

    def test_eventos_sin_sonido(self):
        """Disco, normalizaciones y procesos no suenan: solo se ven."""
        for tipo, sensor in (("umbral_superado", "disco"), ("umbral_normalizado", "cpu"),
                             ("proceso_nuevo", None), ("alerta_sonora", None)):
            self.assertIsNone(self.gestor.atender_evento(self.evento(tipo, sensor)))
        self.assertEqual(self.gestor.reproductor.pedidos, [])

    def test_todo_evento_con_sonido_apunta_a_un_sonido_existente(self):
        for sonido in config.SONIDO_POR_EVENTO.values():
            self.assertIn(sonido, config.SONIDOS)


class PruebasDespachador(unittest.TestCase):
    """De punta a punta: detector -> despachador -> manejador -> sonido."""

    def setUp(self):
        self.d = Despachador()
        for tipo, funcion in manejadores.TABLA.items():
            self.d.registrar(tipo, funcion)
        self.gestor = GestorAlertas(ReproductorEspia())
        self.d.suscribir(self.gestor.atender_evento)

    def test_nuevos_eventos_tienen_manejador(self):
        for tipo in ("red_desconectada", "red_conectada",
                     "red_sigue_desconectada", "alerta_sonora"):
            self.assertIn(tipo, self.d.tipos_registrados())

    def test_umbral_de_cpu_llega_hasta_el_sonido(self):
        evento = self.d.emitir("umbral_superado", {"sensor": "cpu", "valor": 91.0,
                                                   "umbral": config.UMBRALES["cpu"]["alto"]})
        self.assertEqual(evento["sensor"], "cpu")
        self.assertEqual(self.gestor.reproductor.pedidos, ["cpu_alta"])

    def test_red_desconectada_llega_hasta_el_sonido(self):
        evento = self.d.emitir("red_desconectada", {"sensor": "conexion", "interfaz": "Wi-Fi"})
        self.assertEqual(evento["nivel"], config.ALERTA)
        self.assertEqual(self.gestor.reproductor.pedidos, ["red_desconectada"])


class PruebasSinNumerosLiterales(unittest.TestCase):
    """Consideracion G.6: sonidos, tiempos y umbrales solo en config.py.
    Se revisan los archivos nuevos del laboratorio con el modulo ast."""

    ARCHIVOS = ["alertas/__init__.py", "alertas/sonidos.py", "alertas/reproductor.py",
                "alertas/gestor.py", "sensores/conexion.py", "eventos/conexion.py"]

    def test_archivos_nuevos_sin_numeros(self):
        for ruta in self.ARCHIVOS:
            with self.subTest(archivo=ruta):
                arbol = ast.parse((RAIZ / ruta).read_text(encoding="utf-8"))
                numeros = [n.lineno for n in ast.walk(arbol)
                           if isinstance(n, ast.Constant) and type(n.value) in (int, float)]
                self.assertEqual(numeros, [], f"numeros literales en las lineas {numeros}")


if __name__ == "__main__":
    unittest.main()
