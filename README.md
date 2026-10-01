# Laboratorio N.°1 — Alertas sonoras para el nodo de telemetría

**Desarrollo de Software VIII · UTP-FISC**
Yuleidys Escudero · 8-1025-889 · 1GS134 · Docente: Kexy Rodríguez

Ampliación del nodo de telemetría del Trabajo en Clase N.°3: la computadora emite
un **sonido distinto para cada problema** y detecta la **pérdida y recuperación de
la red**, sin congelar el dashboard. Todo lo agregado o modificado está marcado con
`# LABORATORIO`.

## Ejecución

```bash
python -m venv entorno
entorno\Scripts\activate          # Windows
pip install -r requirements.txt

python main.py                    # dashboard gráfico
python main.py --silencio         # modo silencioso (uso en el salón)
python main.py --consola          # dashboard de texto
python generador.py               # (otra terminal) provoca los eventos
python -m unittest discover -s pruebas -v   # pruebas unitarias
```

## Qué se agregó

| Archivo | Qué hace |
|---|---|
| `alertas/sonidos.py` | Convierte las notas de `config.py` en archivos WAV y los reproduce con `PlaySound(..., SND_ASYNC)`, que regresa de inmediato |
| `alertas/reproductor.py` | Cola `deque(maxlen=N)` + marcas de tiempo: decide **cuándo** suena cada alerta sin `time.sleep()` |
| `alertas/gestor.py` | Suscriptor del despachador: decide **qué** sonido corresponde a cada evento |
| `sensores/conexion.py` | Nuevo sensor: ¿hay ruta de salida a la red? (socket UDP, no envía paquetes) |
| `eventos/conexion.py` | `red_desconectada` / `red_conectada` (flanco) y `red_sigue_desconectada` (tiempo), reutilizando `DetectorFlanco` y `DetectorTiempo` sin modificarlos |
| `pruebas/` | 32 pruebas con `unittest` |

## Alertas sonoras

| Evento | Sonido | Idea |
|---|---|---|
| CPU alta | 3 tonos agudos que suben (880→1047→1319 Hz) | la carga sube |
| Memoria alta | 2 tonos graves y largos (392 Hz) | algo pesado, lleno |
| Tráfico de red alto | ráfaga de 5 chirridos cortos (1760 Hz) | paquetes pasando |
| Red desconectada | melodía que cae (988→392 Hz) · prioritaria | algo se perdió |
| Red recuperada | melodía que sube (523→1047 Hz) · prioritaria | todo volvió |
| Red sigue caída | doble golpe grave (330 Hz) | recordatorio discreto |

Todos los sonidos, tiempos y umbrales están en `config.py`.

## Pruebas en vivo

| Evento | Cómo provocarlo |
|---|---|
| CPU alta | `generador.py` → opción 1 |
| Memoria alta | `generador.py` → opción 6 (ocupa RAM hasta pasar el umbral) |
| Tráfico alto | `generador.py` → opción 7 (descarga de prueba) |
| Red desconectada / recuperada | apagar y encender el Wi-Fi |
| Red sigue caída | dejar el Wi-Fi apagado más de `RECORDATORIO_RED_S` |
| Todos los sonidos | botón **Probar sonidos** |
