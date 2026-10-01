"""
dashboard/ventana.py
Panel grafico con tkinter. Solo dibuja: toda la logica vive en nucleo.py.
El refresco usa after(), que es la version "orientada a eventos" del bucle:
tkinter avisa cuando toca redibujar en lugar de que el programa espere.
"""
import time
import tkinter as tk
from tkinter import ttk

import config

AZUL = "#1f3864"
FONDO = "#dce6f1"
TARJETA = "#c5d9f1"
VERDE = "#4caf50"
NARANJA = "#ff9800"
ROJO = "#f44336"

COLOR_NIVEL = {config.INFO: "#9aa7b8", config.AVISO: "#d9a441", config.ALERTA: "#e05c5c"}

TARJETAS = [
    ("cpu", "Uso de CPU"),
    ("memoria", "Memoria RAM"),
    ("disco", "Disco"),
    ("red", "Red"),
    ("procesos", "Procesos"),
    ("bateria", "Bateria"),
]


class Ventana:
    def __init__(self, nucleo):
        self.nucleo = nucleo
        self.raiz = tk.Tk()
        self.raiz.title(f"Nodo de telemetria - {config.NOMBRE_NODO}")
        self.raiz.geometry("1120x640")
        self.raiz.configure(bg=FONDO)
        self.widgets = {}
        self._encabezado()
        self._tarjetas()
        self._paneles()
        self._botones()
        self._refrescar()

    # ----------------------------------------------------------
    def _encabezado(self):
        barra = tk.Frame(self.raiz, bg="white", padx=12, pady=8)
        barra.pack(fill="x")
        tk.Label(barra, text=config.NOMBRE_NODO, font=("Segoe UI", 14, "bold"),
                 fg=AZUL, bg="white").pack(side="left")
        datos = (f"  ·  {config.UBICACION}   ·   {config.ESTUDIANTE} · "
                 f"{config.CEDULA} · {config.SALON}")
        tk.Label(barra, text=datos, font=("Segoe UI", 9), fg="#555",
                 bg="white").pack(side="left")
        self.reloj = tk.Label(barra, text="", font=("Segoe UI", 10, "bold"),
                              fg="#2e7d32", bg="white")
        self.reloj.pack(side="right")
        self.estado = tk.Label(barra, text="MONITOREANDO", font=("Segoe UI", 9, "bold"),
                               fg="#2e7d32", bg="white")
        self.estado.pack(side="right", padx=10)

    # ----------------------------------------------------------
    def _tarjetas(self):
        cont = tk.Frame(self.raiz, bg=FONDO, padx=10, pady=10)
        cont.pack(fill="x")
        for i in range(3):
            cont.columnconfigure(i, weight=1)
        for indice, (clave, titulo) in enumerate(TARJETAS):
            fila, col = divmod(indice, 3)
            marco = tk.Frame(cont, bg=TARJETA, bd=1, relief="solid", padx=10, pady=8)
            marco.grid(row=fila, column=col, sticky="nsew", padx=6, pady=6)
            tk.Label(marco, text=titulo, font=("Segoe UI", 9, "bold"),
                     bg=TARJETA, fg=AZUL).pack(anchor="w")
            valor = tk.Label(marco, text="--", font=("Segoe UI", 22, "bold"),
                             bg=TARJETA, fg="#0d1b33")
            valor.pack(anchor="w")
            barra = tk.Canvas(marco, height=10, bg="#2b2b2b", highlightthickness=0)
            barra.pack(fill="x", pady=4)
            detalle = tk.Label(marco, text="", font=("Segoe UI", 7),
                               bg=TARJETA, fg="#33475b")
            detalle.pack(anchor="w")
            self.widgets[clave] = {"valor": valor, "barra": barra, "detalle": detalle}

    # ----------------------------------------------------------
    def _paneles(self):
        cont = tk.Frame(self.raiz, bg=FONDO, padx=10)
        cont.pack(fill="both", expand=True)
        cont.columnconfigure(0, weight=1)
        cont.columnconfigure(1, weight=1)
        cont.rowconfigure(0, weight=1)

        izq = tk.Frame(cont, bg=TARJETA, bd=1, relief="solid", padx=8, pady=6)
        izq.grid(row=0, column=0, sticky="nsew", padx=(0, 6))
        tk.Label(izq, text="Procesos con mayor consumo", font=("Segoe UI", 8, "bold"),
                 bg=TARJETA, fg=AZUL).pack(anchor="w")
        self.lista_procesos = tk.Text(izq, height=10, bg=TARJETA, fg="#0d1b33",
                                      font=("Consolas", 8), bd=0)
        self.lista_procesos.pack(fill="both", expand=True)

        der = tk.Frame(cont, bg="#0f1b2d", bd=1, relief="solid", padx=8, pady=6)
        der.grid(row=0, column=1, sticky="nsew")
        tk.Label(der, text="Bitacora de eventos", font=("Segoe UI", 8, "bold"),
                 bg="#0f1b2d", fg="#9ec5fe").pack(anchor="w")
        self.log = tk.Text(der, height=10, bg="#0f1b2d", fg="#cfd8e3",
                           font=("Consolas", 8), bd=0)
        self.log.pack(fill="both", expand=True)
        for nivel, color in COLOR_NIVEL.items():
            self.log.tag_config(nivel, foreground=color)

    # ----------------------------------------------------------
    def _botones(self):
        barra = tk.Frame(self.raiz, bg=FONDO, padx=10, pady=8)
        barra.pack(fill="x")
        acciones = [
            ("Pausar / Reanudar", self.pausar),
            ("Generar reporte", self.reporte),
            ("Limpiar bitacora", self.limpiar),
            ("Salir", self.raiz.destroy),
        ]
        for texto, accion in acciones:
            tk.Button(barra, text=texto, command=accion, bg="#4472c4", fg="white",
                      font=("Segoe UI", 8, "bold"), relief="flat",
                      padx=10, pady=3).pack(side="left", padx=4)
        u = config.UMBRALES
        tk.Label(barra, bg=FONDO, fg="#33475b", font=("Segoe UI", 7),
                 text=(f"umbrales: CPU {u['cpu']['alto']:.0f}% · RAM {u['memoria']['alto']:.0f}% · "
                       f"disco {u['disco']['alto']:.0f}% · red {u['red']['alto']:.0f} KB/s")
                 ).pack(side="right")

    # ----------------------------------------------------------
    def pausar(self):
        pausado = self.nucleo.alternar_pausa()
        self.estado.config(text="PAUSADO" if pausado else "MONITOREANDO",
                           fg="#c62828" if pausado else "#2e7d32")

    def reporte(self):
        self.nucleo.generar_reporte_manual()

    def limpiar(self):
        self.nucleo.bitacora.limpiar()
        self.log.delete("1.0", "end")

    # ----------------------------------------------------------
    def _pintar_barra(self, canvas, porcentaje):
        canvas.delete("all")
        ancho = canvas.winfo_width() or 200
        porcentaje = max(0.0, min(porcentaje, 100.0))
        color = VERDE if porcentaje < 60 else (NARANJA if porcentaje < 85 else ROJO)
        canvas.create_rectangle(0, 0, ancho * porcentaje / 100, 10,
                                fill=color, outline=color)

    def _refrescar(self):
        self.nucleo.paso()
        self.reloj.config(text=time.strftime("%H:%M:%S"))
        datos = self.nucleo.instantanea()

        for clave, _ in TARJETAS:
            w = self.widgets[clave]
            d = datos.get(clave)
            if not d or not d["ok"]:
                w["valor"].config(text="N/D")
                w["detalle"].config(text=d["detalle"] if d else "sin lectura")
                self._pintar_barra(w["barra"], 0)
                continue
            valor = d["valor"]
            if clave == "procesos":
                w["valor"].config(text=f"{valor:.0f} procs")
                pct = min(valor / 5.0, 100)
            elif clave == "red":
                w["valor"].config(text=f"{valor:.1f} KB/s")
                pct = min(valor / config.UMBRALES["red"]["alto"] * 100, 100)
            else:
                w["valor"].config(text=f"{valor:.1f} %")
                pct = valor
            w["detalle"].config(text=d["detalle"])
            self._pintar_barra(w["barra"], pct)

        pro = self.nucleo.lecturas.get("procesos", {})
        self.lista_procesos.delete("1.0", "end")
        if pro.get("ok"):
            self.lista_procesos.insert("end", f"{'PID':>7} {'PROCESO':<26}{'CPU':>7}{'RAM':>7}\n")
            for p in pro["top"]:
                self.lista_procesos.insert(
                    "end", f"{p['pid']:>7} {p['nombre'][:26]:<26}{p['cpu']:>6.1f}%{p['ram']:>6.1f}%\n")

        self.log.delete("1.0", "end")
        for e in self.nucleo.bitacora.ultimos(14):
            self.log.insert("end", f"{e['hora']} [{e['nivel']:<6}] {e['mensaje']}\n", e["nivel"])
        self.log.see("end")

        self.raiz.after(500, self._refrescar)

    def iniciar(self):
        self.raiz.mainloop()
