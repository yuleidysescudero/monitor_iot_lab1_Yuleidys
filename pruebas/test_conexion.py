# LABORATORIO: pruebas unitarias de los eventos de conexion de red
import socket
import unittest
from unittest import mock

import config
from eventos.conexion import MonitorConexion
from sensores import conexion

T0 = 1000.0
P = config.RECORDATORIO_RED_S


def tipos(eventos):
    return [tipo for tipo, _datos in eventos]


class PruebasMonitorConexion(unittest.TestCase):
    def setUp(self):
        self.m = MonitorConexion()

    def test_arranque_con_red_no_genera_evento(self):
        self.assertEqual(self.m.revisar(True, T0, "Wi-Fi"), [])

    def test_arranque_sin_red_avisa(self):
        self.assertEqual(tipos(self.m.revisar(False, T0)), ["red_desconectada"])

    def test_flanco_de_bajada_y_subida(self):
        self.m.revisar(True, T0, "Wi-Fi")
        caida = self.m.revisar(False, T0 + 1)
        self.assertEqual(tipos(caida), ["red_desconectada"])
        self.assertEqual(caida[0][1]["interfaz"], "Wi-Fi")
        vuelta = self.m.revisar(True, T0 + 31, "Wi-Fi")
        self.assertEqual(tipos(vuelta), ["red_conectada"])
        self.assertAlmostEqual(vuelta[0][1]["segundos"], 30)

    def test_estado_estable_no_repite_eventos(self):
        """Evento por flanco: mientras el estado no cambia, no pasa nada."""
        self.m.revisar(True, T0, "Wi-Fi")
        for i in range(10):
            self.assertEqual(self.m.revisar(True, T0 + i, "Wi-Fi"), [])

    def test_recordatorio_por_tiempo(self):
        self.m.revisar(True, T0, "Wi-Fi")
        self.m.revisar(False, T0)
        self.assertEqual(self.m.revisar(False, T0 + P / 2), [])
        primero = self.m.revisar(False, T0 + P)
        self.assertEqual(tipos(primero), ["red_sigue_desconectada"])
        self.assertAlmostEqual(primero[0][1]["segundos"], P)
        self.assertEqual(self.m.revisar(False, T0 + P * 1.5), [])
        self.assertEqual(tipos(self.m.revisar(False, T0 + P * 2)), ["red_sigue_desconectada"])

    def test_sin_recordatorio_despues_de_reconectar(self):
        self.m.revisar(True, T0, "Wi-Fi")
        self.m.revisar(False, T0)
        self.m.revisar(True, T0 + 1, "Wi-Fi")
        self.assertEqual(self.m.revisar(True, T0 + P * 3, "Wi-Fi"), [])

    def test_cada_caida_reinicia_el_recordatorio(self):
        self.m.revisar(True, T0, "Wi-Fi")
        self.m.revisar(False, T0)
        self.m.revisar(True, T0 + P * 0.9, "Wi-Fi")
        self.m.revisar(False, T0 + P * 0.95)
        self.assertEqual(self.m.revisar(False, T0 + P * 1.1), [])
        self.assertEqual(tipos(self.m.revisar(False, T0 + P * 1.95)),
                         ["red_sigue_desconectada"])


class PruebasSensorConexion(unittest.TestCase):
    def test_lectura_real_tiene_el_formato_comun(self):
        lectura = conexion.leer()
        self.assertTrue(lectura["ok"])
        self.assertIn(lectura["conectado"], (True, False))
        self.assertIn("detalle", lectura)

    def test_sin_ruta_es_desconectado(self):
        """Simula Wi-Fi apagado: connect() falla con 'red inalcanzable'."""
        with mock.patch.object(socket.socket, "connect",
                               side_effect=OSError("red inalcanzable")):
            lectura = conexion.leer()
        self.assertTrue(lectura["ok"])
        self.assertFalse(lectura["conectado"])
        self.assertEqual(lectura["valor"], 0.0)


if __name__ == "__main__":
    unittest.main()
