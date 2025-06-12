import tkinter as tk
from tkinter import ttk, Toplevel, StringVar, Listbox, END
from PIL import Image, ImageTk
import json
import datetime
import os

RUTA_ARCHIVO = "clientes.json"
RUTA_RUTINAS_ASIGNADAS = "rutinasyaasignadas.json"

#GEESTOR DE RUTINAS

def abrir_rutina(root, callback_volver):
    try:
        with open(RUTA_ARCHIVO, "r", encoding="utf-8") as f:
            datos_clientes = json.load(f)
            clientes = [c["nombre"] for c in datos_clientes]
    except:
        return

    ventana = Toplevel(root)
    ventana.title("Gestor de Rutinas - AJUMA training center")
    ventana.attributes("-fullscreen", True)
    selected_client_name = StringVar()
    selected_client_name.set("Seleccione un cliente")
#ESTILOS VISUALES
    def estilos():
        estilo = ttk.Style()
        estilo.theme_use("clam")
        estilo.configure("TLabel", background="#34495E", foreground="white", font=("Arial", 12))
        estilo.configure("TButton", font=("Arial", 12, "bold"))
        estilo.configure("TCombobox", font=("Arial", 12))
#SELECCIONAR CLIENTE LISTA
    def seleccionar_cliente(event):
        idxs = lista_clientes.curselection()
        if idxs:
            selected_client_name.set(lista_clientes.get(idxs[0]))
#MENSAJE TEMPORAL EN VENTANA FLOTANTE
    def mensaje_emergente(texto):
        top = Toplevel(ventana)
        top.overrideredirect(True)
        top.geometry(f"+{ventana.winfo_x()+200}+{ventana.winfo_y()+300}")
        tk.Label(top, text=texto, bg="#27AE60", fg="white", font=("Arial", 14, "bold"), padx=20, pady=10).pack()
        ventana.after(2000, top.destroy)
#VALIDACION DE RUTINAS ASIGNADAS
    def asignar_rutina():
        cliente = selected_client_name.get()
        rutina = combo_rutina.get()
        tiempo = combo_tiempo.get()

        if cliente == "Seleccione un cliente" or not rutina or not tiempo:
            return

        nueva_asignacion = {
            "cliente": cliente,
            "rutina": rutina,
            "tiempo": tiempo,
            "fecha": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }

        datos = []
        if os.path.exists(RUTA_RUTINAS_ASIGNADAS):
            try:
                with open(RUTA_RUTINAS_ASIGNADAS, "r", encoding="utf-8") as f:
                    datos = json.load(f)
            except:
                pass

        datos.append(nueva_asignacion)

        try:
            with open(RUTA_RUTINAS_ASIGNADAS, "w", encoding="utf-8") as f:
                json.dump(datos, f, indent=4, ensure_ascii=False)
        except:
            return

        mensaje_emergente(f"¡Asignado {rutina} por {tiempo} a {cliente}!")
#CONFIRMACION DE SALIDA
    def confirmar_salida_personalizado():
        confirmar_frame = tk.Frame(main_frame, bg="#1e1e1e")
        confirmar_frame.pack(pady=10)

        tk.Label(confirmar_frame, text="¿Estás seguro que deseas salir al menú?",
                 font=("Arial", 12), bg="#1e1e1e", fg="white").pack(side="left", padx=10)

        tk.Button(confirmar_frame, text="Confirmar", bg="red", fg="white",
                  font=("Arial", 10, "bold"), command=cerrar_ventana).pack(side="left", padx=5)

        tk.Button(confirmar_frame, text="Cancelar", bg="gray", fg="white",
                  font=("Arial", 10, "bold"), command=confirmar_frame.destroy).pack(side="left", padx=5)
#CONFIRMACION VISUAL DE LA VENTANA
    def cerrar_ventana():
        callback_volver()
        ventana.destroy()

    estilos()

    canvas = tk.Canvas(ventana)
    canvas.pack(fill="both", expand=True)
#FONDO 
    try:
        original_bg_image = Image.open("gimnasioimagen.jpg")
    except:
        canvas.config(bg="#2C3E50")
        original_bg_image = None

    bg_image_container = [None]
#FUNCIONAMIENTO POR SECCIONES
    def redibujar_fondo(event=None):
        if original_bg_image:
            w = ventana.winfo_width()
            h = ventana.winfo_height()
            resized = original_bg_image.resize((w, h), Image.LANCZOS)
            bg = ImageTk.PhotoImage(resized)
            canvas.delete("bg")
            canvas.create_image(0, 0, image=bg, anchor="nw", tags="bg")
            bg_image_container[0] = bg

    ventana.bind("<Configure>", redibujar_fondo)
    ventana.protocol("WM_DELETE_WINDOW", cerrar_ventana)

    main_frame = ttk.Frame(canvas, padding=20)
    canvas.create_window(ventana.winfo_screenwidth() // 2, ventana.winfo_screenheight() // 2, window=main_frame)

    ttk.Label(main_frame, text="Gestión de Rutinas", font=("Arial", 24, "bold"), foreground="white").pack(pady=10)

    lista_frame = ttk.Frame(main_frame)
    lista_frame.pack(pady=10)
#LISTA DE CLIENTES
    ttk.Label(lista_frame, text="Clientes:").pack(anchor="w")
    lista_clientes = Listbox(lista_frame, height=10, width=30, font=("Arial", 12), bg="black", fg="white")
    for c in clientes:
        lista_clientes.insert(END, c)
    lista_clientes.pack()
    lista_clientes.bind("<<ListboxSelect>>", seleccionar_cliente)

    ttk.Label(main_frame, textvariable=selected_client_name, font=("Arial", 14, "italic"),
              foreground="white").pack(pady=10)

    opciones_frame = ttk.Frame(main_frame)
    opciones_frame.pack(pady=10)

    ttk.Label(opciones_frame, text="Rutina:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
    combo_rutina = ttk.Combobox(opciones_frame, state="readonly",
                                values=["Pilates", "Musculación", "Yoga", "Cardio"])
    combo_rutina.grid(row=0, column=1, padx=5, pady=5)

    ttk.Label(opciones_frame, text="Tiempo:").grid(row=1, column=0, sticky="w", padx=5, pady=5)
    combo_tiempo = ttk.Combobox(opciones_frame, state="readonly",
                                values=["30 minutos", "40 minutos", "60 minutos", "2 horas"])
    combo_tiempo.grid(row=1, column=1, padx=5, pady=5)

    ttk.Button(main_frame, text="Asignar Rutina", command=asignar_rutina).pack(pady=20)
    ttk.Button(main_frame, text="Salir al Menú", command=confirmar_salida_personalizado).pack(pady=10)
#TECLA ESCAPE PARA ACTIVAR LA FUNCIÓN DE SALIDA
    redibujar_fondo()
    ventana.bind("<Escape>", lambda e: confirmar_salida_personalizado())
