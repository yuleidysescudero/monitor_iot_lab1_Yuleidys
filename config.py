"""
config.py
Configuracion central del nodo de telemetria.
TODO lo personalizable esta aqui: si cambias tu nombre o los umbrales,
no tienes que tocar ningun otro archivo del proyecto.
"""

# ---------------------------------------------------------------
# 1. DATOS DEL ESTUDIANTE  
# ---------------------------------------------------------------
ESTUDIANTE = "Yuleidys Escudero"
CEDULA = "8-1025-889"
SALON = "1GS134"
NOMBRE_NODO = "Equipo-ThinkPad"         
UBICACION = "Laboratorio 3 - FISC"

# ---------------------------------------------------------------
# 2. TIEMPOS DEL BUCLE (en segundos)
# ---------------------------------------------------------------
INTERVALO_MUESTREO = 1.0      # cada cuanto se leen los sensores
PERIODO_REPORTE = 30.0        # cada cuanto se guarda el resumen en JSON  (evento por TIEMPO)
TIEMPO_MAX_SIN_DATOS = 5.0    # si un sensor no responde en este tiempo -> evento por FALLA
TAMANO_VENTANA = 25           # cuantas muestras guarda la ventana movil (deque)

# ---------------------------------------------------------------
# 3. UMBRALES CON HISTERESIS (evento por UMBRAL)
#    "alto" dispara la alerta, "bajo" la apaga. La separacion entre
#    ambos evita que el evento se dispare 100 veces seguidas.
# ---------------------------------------------------------------
UMBRALES = {
    "cpu":     {"alto": 70.0, "bajo": 60.0, "unidad": "%"},
    "memoria": {"alto": 85.0, "bajo": 78.0, "unidad": "%"},
    "disco":   {"alto": 90.0, "bajo": 85.0, "unidad": "%"},
    "red":     {"alto": 500.0, "bajo": 300.0, "unidad": "KB/s"},
}

# Variacion brusca entre dos muestras consecutivas (evento por FLANCO)
SALTO_ANOMALO = 30.0          # puntos porcentuales
UMBRAL_NUCLEO_SATURADO = 95.0 # % por nucleo individual
BATERIA_BAJA = 20.0           # % para avisar bateria baja

# ---------------------------------------------------------------
# 4. ARCHIVOS
# ---------------------------------------------------------------
ARCHIVO_BITACORA = "bitacora.json"
MAX_EVENTOS_MEMORIA = 200     # cuantos eventos se conservan en pantalla

# ---------------------------------------------------------------
# 5. NIVELES DE EVENTO
# ---------------------------------------------------------------
INFO = "INFO"
AVISO = "AVISO"
ALERTA = "ALERTA"
