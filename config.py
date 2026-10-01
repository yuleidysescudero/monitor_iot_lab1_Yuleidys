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
HISTERESIS_NUCLEO = 15.0      # LABORATORIO: antes era un 15 escrito dentro de nucleo.py
BATERIA_BAJA = 20.0           # % para avisar bateria baja

# LABORATORIO: tiempos que antes estaban escritos dentro de otros archivos
CALENTAMIENTO_S = 0.3         # LABORATORIO: espera tras la lectura de calentamiento (nucleo.py)
REFRESCO_MS = 500             # LABORATORIO: cada cuanto se redibuja la ventana (ventana.py)
PAUSA_CONSOLA_S = 0.2         # LABORATORIO: pausa entre vueltas del panel de consola (consola.py)
# LABORATORIO: leer los procesos tarda ~0.5 s. Leerlos cada segundo trababa
# el dashboard medio segundo de cada segundo; se leen con un periodo lento.
PERIODO_LENTO = 5.0           # LABORATORIO
SENSORES_LENTOS = ("procesos",)  # LABORATORIO

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
SONIDO = "SONIDO"             # LABORATORIO: nivel para anotar en la bitacora cada alerta que suena


# ===============================================================
# LABORATORIO N.1 - ALERTAS SONORAS PARA EL NODO DE TELEMETRIA
# Todo lo que sigue es nuevo. Ningun otro archivo del laboratorio
# contiene numeros: sonidos, tiempos y umbrales viven solo aqui.
# ===============================================================

# ---------------------------------------------------------------
# 6. CONEXION DE RED                                   # LABORATORIO
# ---------------------------------------------------------------
# IP publica que se usa SOLO para preguntarle al sistema operativo si
# existe una ruta de salida. Con UDP, connect() no envia ningun paquete.
DESTINO_RUTA = ("8.8.8.8", 80)                         # LABORATORIO
# Mientras la red siga caida, cada cuanto se recuerda (evento por TIEMPO).
RECORDATORIO_RED_S = 20.0                              # LABORATORIO

# ---------------------------------------------------------------
# 7. REPRODUCTOR DE ALERTAS                            # LABORATORIO
# ---------------------------------------------------------------
# Modo silencioso (obligatorio en el salon): la alerta pasa por la cola
# igual que siempre, se anota y se muestra, pero no suena.
# Tambien se activa con:  python main.py --silencio
MODO_SILENCIOSO = False                                # LABORATORIO
PAUSA_ENTRE_ALERTAS_S = 0.4   # silencio entre dos alertas de la cola       # LABORATORIO
ENFRIAMIENTO_S = 10.0         # una misma alerta no se repite antes de esto # LABORATORIO
MAX_COLA_ALERTAS = 6          # deque(maxlen): si se llena, sale la mas vieja # LABORATORIO

# ---------------------------------------------------------------
# 8. SINTESIS DE LOS SONIDOS (archivos WAV)            # LABORATORIO
# ---------------------------------------------------------------
CARPETA_SONIDOS = "alertas/generados"                  # LABORATORIO
FRECUENCIA_MUESTREO_AUDIO = 22050  # muestras por segundo del WAV    # LABORATORIO
CANALES_AUDIO = 1                  # mono                            # LABORATORIO
BYTES_POR_MUESTRA = 2              # 16 bits                         # LABORATORIO
AMPLITUD_MAXIMA = 32767            # tope de una muestra de 16 bits  # LABORATORIO
VOLUMEN = 0.6                      # 0.0 a 1.0                       # LABORATORIO
FUNDIDO_MS = 8                     # rampa al inicio/fin de cada nota: evita "clics" # LABORATORIO
MS_POR_SEGUNDO = 1000.0                                # LABORATORIO
SILENCIO = 0                       # una nota con frecuencia 0 es una pausa # LABORATORIO

# Cada sonido es una lista de notas (frecuencia en Hz, duracion en ms).
# "prioridad": True -> entra al FRENTE de la cola (appendleft) y no
# respeta el enfriamiento, porque perder la red es lo mas urgente.
SONIDOS = {                                            # LABORATORIO
    # Tres tonos agudos que SUBEN rapido: la carga del procesador sube.
    "cpu_alta": {
        "descripcion": "CPU alta",
        "prioridad": False,
        "notas": [(880, 110), (SILENCIO, 40), (1047, 110), (SILENCIO, 40), (1319, 220)],
    },
    # Dos tonos GRAVES y largos: sensacion de algo pesado / lleno.
    "memoria_alta": {
        "descripcion": "Memoria RAM alta",
        "prioridad": False,
        "notas": [(392, 350), (SILENCIO, 120), (392, 350)],
    },
    # Rafaga de cinco "chirridos" muy cortos: paquetes pasando por la red.
    "trafico_alto": {
        "descripcion": "Trafico de red alto",
        "prioridad": False,
        "notas": [(1760, 50), (SILENCIO, 40)] * 4 + [(1760, 50)],
    },
    # Melodia que CAE (de agudo a grave): algo se perdio.
    "red_desconectada": {
        "descripcion": "Red desconectada",
        "prioridad": True,
        "notas": [(988, 180), (784, 180), (523, 180), (392, 420)],
    },
    # La misma idea al reves: melodia que SUBE, corta y alegre.
    "red_conectada": {
        "descripcion": "Red recuperada",
        "prioridad": True,
        "notas": [(523, 100), (659, 100), (784, 100), (1047, 240)],
    },
    # Doble golpe grave y breve: recordatorio discreto, no alarma nueva.
    "red_sigue_desconectada": {
        "descripcion": "La red sigue caida",
        "prioridad": False,
        "notas": [(330, 120), (SILENCIO, 90), (330, 120)],
    },
}

# Que sonido corresponde a cada evento. La clave es "tipo:sensor" o
# solo "tipo". Agregar una alerta nueva es agregar una linea aqui.
SONIDO_POR_EVENTO = {                                  # LABORATORIO
    "umbral_superado:cpu": "cpu_alta",
    "umbral_superado:memoria": "memoria_alta",
    "umbral_superado:red": "trafico_alto",
    "red_desconectada": "red_desconectada",
    "red_conectada": "red_conectada",
    "red_sigue_desconectada": "red_sigue_desconectada",
}

# ---------------------------------------------------------------
# 9. GENERADOR DE EVENTOS (pruebas en vivo)            # LABORATORIO
# ---------------------------------------------------------------
MARGEN_MEMORIA_PCT = 3.0      # cuanto pasar el umbral de RAM al ocuparla   # LABORATORIO
TOPE_MEMORIA_PCT = 92.0       # nunca ocupar la RAM por encima de esto       # LABORATORIO
URL_TRAFICO = "https://speed.cloudflare.com/__down?bytes=60000000"         # LABORATORIO
