# modulo_profesores.py
import tkinter as tk
from tkinter import ttk
import json
import os


RUTA_CLIENTES = "clientes.json"

TIPOS_ENTRENAMIENTO = [
    "Musculacion",
    "Pilates",
    "Yoga",
    "Cardio"
]

def abrir_modulo_profesores(callback_volver):
    
    ventana = tk.Toplevel()
    ventana.title("Módulo de Profesores")
    ventana.configure(bg="#1e1e1e")
    ventana.attributes('-fullscreen', True)

    # ---------------- Título -------------------
    titulo = tk.Label(ventana, text="Módulo de Profesores", font=("Segoe UI", 26, "bold"),
                      bg="#1e1e1e", fg="white")
    titulo.pack(pady=30)

    # ---------------- Contenedor de botones -------------------
    frame_botones = tk.Frame(ventana, bg="#1e1e1e")
    frame_botones.pack(pady=10)

    def mostrar_alumnos(tipo_entrenamiento):
        for widget in frame_resultados.winfo_children():
            widget.destroy()
        alumnos = cargar_alumnos_por_tipo(tipo_entrenamiento)
        if not alumnos:
            sin_resultado = tk.Label(frame_resultados, text="No hay alumnos para este tipo de entrenamiento.",
                                     fg="white", bg="#1e1e1e", font=("Segoe UI", 14))
            sin_resultado.pack()
            return

        tree = ttk.Treeview(frame_resultados, columns=("id", "nombre", "dni", "membresia"), show="headings")
        tree.heading("id", text="ID")
        tree.heading("nombre", text="Nombre")
        tree.heading("dni", text="DNI")
        tree.heading("membresia", text="Entrenamiento")
        for i, alumno in enumerate(alumnos, 1):
            tree.insert("", "end", values=(i, alumno["nombre"], alumno["dni"], alumno["membresia"]))
        tree.pack(fill="both", expand=True, pady=10)

    def cargar_alumnos_por_tipo(tipo):
        if not os.path.exists(RUTA_CLIENTES):
            return []
        with open(RUTA_CLIENTES, "r", encoding="utf-8") as f:
            try:
                datos = json.load(f)
            except json.JSONDecodeError:
                return []
        return [a for a in datos if a.get("membresia") == tipo]

    # Crear botones para cada tipo de entrenamiento
    for tipo in TIPOS_ENTRENAMIENTO:
        btn = tk.Button(frame_botones, text=tipo, font=("Segoe UI", 14),
                        width=15, height=2, bg="#3b8ed0", fg="white",
                        command=lambda t=tipo: mostrar_alumnos(t))
        btn.pack(padx=10, pady=5)

    # ---------------- Área para resultados -------------------
    frame_resultados = tk.Frame(ventana, bg="#1e1e1e")
    frame_resultados.pack(fill="both", expand=True, padx=20, pady=10)

    # ---------------- Botón de regreso -------------------
    def cerrar_ventana():
        callback_volver()
        ventana.destroy()

    btn_volver = tk.Button(ventana, text="Volver al Menú", font=("Segoe UI", 12),
                           bg="#444444", fg="white", command=cerrar_ventana)
    btn_volver.pack(pady=20)

    ventana.bind("<Escape>", lambda e: cerrar_ventana())
    ventana.protocol("WM_DELETE_WINDOW", lambda: cerrar_ventana())
