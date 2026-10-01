# LABORATORIO: pruebas unitarias del reproductor de alertas (cola + marcas de tiempo)
"""
Se usa un reloj falso y una salida falsa: asi se prueba la logica de
tiempos sin esperar de verdad y sin hacer ruido en el salon.
Ejecutar desde la carpeta raiz:  python -m unittest discover -s pruebas -v
"""
import time
import unittest

import config
from alertas.reproductor import Reproductor

T0 = 1000.0


def catalogo_falso():
    """Mismo formato que generar_sonidos(), sin crear archivos."""
    return {
        nombre: {"ruta": f"{nombre}.wav", "duracion": 1.0,
                 "descripcion": s["descripcion"], "prioridad": s["prioridad"]}
        for nombre, s in config.SONIDOS.items()
    }


class SalidaFalsa:
    def __init__(self):
        self.tocados = []

    def __call__(self, ruta):
        self.tocados.append(ruta)


class PruebasReproductor(unittest.TestCase):
    def setUp(self):
        self.salida = SalidaFalsa()
        self.rep = Reproductor(catalogo_falso(), salida=self.salida, silencioso=False)
        self.fin = 1.0 + config.PAUSA_ENTRE_ALERTAS_S     # duracion + pausa

    def test_encolar_no_hace_sonar(self):
        """encolar() solo guarda el nombre: el manejador sigue siendo breve."""
        self.assertTrue(self.rep.encolar("cpu_alta", T0))
        self.assertEqual(self.salida.tocados, [])
        self.assertEqual(list(self.rep.cola), ["cpu_alta"])

    def test_atender_toca_la_primera_alerta(self):
        self.rep.encolar("cpu_alta", T0)
        self.assertEqual(self.rep.atender(T0), "cpu_alta")
        self.assertEqual(self.salida.tocados, ["cpu_alta.wav"])

    def test_no_se_pisan_dos_alertas(self):
        """Mientras suena una alerta, la siguiente espera su turno en la cola."""
        self.rep.encolar("cpu_alta", T0)
        self.rep.encolar("memoria_alta", T0)
        self.rep.atender(T0)
        self.assertIsNone(self.rep.atender(T0 + self.fin / 2))
        self.assertEqual(list(self.rep.cola), ["memoria_alta"])
        self.assertEqual(self.rep.atender(T0 + self.fin), "memoria_alta")

    def test_atender_no_bloquea(self):
        """Con una alerta sonando, atender() regresa enseguida (no espera)."""
        rep = Reproductor(catalogo_falso(), salida=self.salida, silencioso=False)
        rep.encolar("cpu_alta")
        rep.encolar("memoria_alta")
        rep.atender()
        inicio = time.perf_counter()
        resultado = rep.atender()
        transcurrido = time.perf_counter() - inicio
        self.assertIsNone(resultado)
        self.assertLess(transcurrido, config.PAUSA_ENTRE_ALERTAS_S)

    def test_el_ciclo_sigue_mientras_suena(self):
        """Simula el bucle del dashboard: cada REFRESCO_MS se llama atender().
        Mientras dura una alerta, el ciclo da varias vueltas mas."""
        paso = config.REFRESCO_MS / config.MS_POR_SEGUNDO
        alertas = ["cpu_alta", "memoria_alta", "trafico_alto"]
        for nombre in alertas:
            self.rep.encolar(nombre, T0)
        ahora, vueltas, sonaron = T0, 0, []
        while self.rep.cola or self.rep.ocupado(ahora):
            nombre = self.rep.atender(ahora)
            if nombre:
                sonaron.append(nombre)
            vueltas += 1
            ahora += paso
        self.assertEqual(sonaron, alertas)
        # el ciclo dio muchas mas vueltas que alertas sonaron: nunca se detuvo
        self.assertGreaterEqual(vueltas, len(alertas) * int(self.fin / paso))

    def test_alerta_repetida_no_se_duplica_en_cola(self):
        self.rep.encolar("cpu_alta", T0)
        self.assertFalse(self.rep.encolar("cpu_alta", T0))
        self.assertEqual(len(self.rep.cola), 1)

    def test_enfriamiento(self):
        """La misma alerta no vuelve a sonar antes de ENFRIAMIENTO_S."""
        self.rep.encolar("cpu_alta", T0)
        self.rep.atender(T0)
        self.assertFalse(self.rep.encolar("cpu_alta", T0 + config.ENFRIAMIENTO_S / 2))
        self.assertTrue(self.rep.encolar("cpu_alta", T0 + config.ENFRIAMIENTO_S))

    def test_prioridad_red_desconectada_va_primero(self):
        self.rep.encolar("cpu_alta", T0)
        self.rep.encolar("trafico_alto", T0)
        self.rep.encolar("red_desconectada", T0)
        self.assertEqual(self.rep.cola[0], "red_desconectada")

    def test_cola_con_limite(self):
        """deque(maxlen): la cola nunca crece mas de MAX_COLA_ALERTAS."""
        for i in range(config.MAX_COLA_ALERTAS * 2):
            nombre = list(config.SONIDOS)[i % len(config.SONIDOS)]
            self.rep.encolar(nombre, T0 + i * config.ENFRIAMIENTO_S, forzar=True)
        self.assertLessEqual(len(self.rep.cola), config.MAX_COLA_ALERTAS)

    def test_modo_silencioso(self):
        """En silencio la alerta sigue la cola y los tiempos, pero no suena."""
        rep = Reproductor(catalogo_falso(), salida=self.salida, silencioso=True)
        rep.encolar("red_desconectada", T0)
        self.assertEqual(rep.atender(T0), "red_desconectada")
        self.assertEqual(self.salida.tocados, [])
        self.assertTrue(rep.ocupado(T0))

    def test_sin_parlantes_no_se_cae(self):
        def salida_rota(_ruta):
            raise RuntimeError("Failed to play sound")
        rep = Reproductor(catalogo_falso(), salida=salida_rota, silencioso=False)
        rep.encolar("cpu_alta", T0)
        self.assertEqual(rep.atender(T0), "cpu_alta")
        self.assertIn("Failed", rep.estado()["error"])

    def test_sonido_desconocido(self):
        self.assertFalse(self.rep.encolar("no_existe", T0))


if __name__ == "__main__":
    unittest.main()
