import tkinter as tk
from tkinter import ttk, messagebox
import json
import os
from datetime import datetime, timedelta

RUTA_ARCHIVO = "clientes.json"

def abrir_ver_clientes(root):
    ventana = tk.Toplevel(root)
    ventana.title("Ver Clientes")
    ventana.attributes("-fullscreen", True)
    ventana.configure(bg="#1e1e1e")

    def cargar_clientes():
        if os.path.exists(RUTA_ARCHIVO):
            with open(RUTA_ARCHIVO, "r", encoding="utf-8") as archivo:
                try:
                    return json.load(archivo)
                except json.JSONDecodeError:
                    return []
        return []

    def guardar_clientes(clientes):
        with open(RUTA_ARCHIVO, "w", encoding="utf-8") as archivo:
            json.dump(clientes, archivo, indent=4)

    def eliminar_cliente():
        item = tree.selection()
        if item:
            confirm = messagebox.askyesno("Confirmar eliminación", "¿Estás seguro de eliminar este cliente?")
            if confirm:
                tree.delete(item)
                actualizar_json_desde_treeview()
        else:
            messagebox.showinfo("Seleccionar cliente", "Seleccione un cliente para eliminar.")

    def actualizar_json_desde_treeview():
        datos = []
        for item in tree.get_children():
            valores = tree.item(item)["values"]
            datos.append({
                "id": valores[0],
                "nombre": valores[1],
                "dni": valores[2],
                "telefono": valores[3],
                "email": valores[4],
                "membresia": valores[5],
                "plan": valores[6],
                "fecha_ingreso": valores[7],
                "tipo_pago": valores[8]
            })
        guardar_clientes(datos)

    def calcular_dias_restantes(fecha_ingreso_str, plan_str):
        try:
            fecha_ingreso = datetime.strptime(fecha_ingreso_str, "%Y-%m-%d")
            plan = plan_str.lower()
            if "mensual" in plan:
                duracion = timedelta(days=30)
            elif "trimestral" in plan:
                duracion = timedelta(days=90)
            elif "anual" in plan:
                duracion = timedelta(days=365)
            else:
                duracion = timedelta(days=0)  # Plan desconocido
            fecha_vencimiento = fecha_ingreso + duracion
            dias_restantes = (fecha_vencimiento - datetime.today()).days
            return dias_restantes
        except Exception:
            return None

    def cargar_y_mostrar_clientes(filtro_nombre=""):
        for item in tree.get_children():
            tree.delete(item)
        clientes = cargar_clientes()
        for cliente in clientes:
            if filtro_nombre.lower() not in cliente.get("nombre", "").lower():
                continue

            dias_restantes = calcular_dias_restantes(cliente.get("fecha_ingreso", ""), cliente.get("plan", ""))
            if dias_restantes is None:
                estado = "Desconocido"
                color_fila = "white"
            elif dias_restantes < 0:
                estado = "Vencida"
                color_fila = "red"
            else:
                estado = f"{dias_restantes} días"
                color_fila = "white"

            tree.insert("", "end", values=(
                cliente.get("id", ""),
                cliente.get("nombre", ""),
                cliente.get("dni", ""),
                cliente.get("telefono", ""),
                cliente.get("email", ""),
                cliente.get("membresia", ""),
                cliente.get("plan", ""),
                cliente.get("fecha_ingreso", ""),
                cliente.get("tipo_pago", ""),
                estado
            ), tags=(color_fila,))

        tree.tag_configure("red", foreground="red")
        tree.tag_configure("white", foreground="white")

    def on_buscar(event):
        texto = entry_buscar.get()
        cargar_y_mostrar_clientes(texto)

    # --- Estilos para el Treeview ---
    style = ttk.Style()
    style.theme_use("default")
    style.configure("Treeview.Heading", background="#333333", foreground="white", font=("Segoe UI", 11, "bold"))
    style.configure("Treeview", background="#1e1e1e", foreground="white", fieldbackground="#1e1e1e", font=("Segoe UI", 10))
    style.map('Treeview', background=[('selected', '#444444')])

    columnas = ("id", "nombre", "dni", "telefono", "email", "membresia", "plan", "fecha_ingreso", "tipo_pago", "estado")
    tree = ttk.Treeview(ventana, columns=columnas, show="headings")

    for col in columnas:
        tree.heading(col, text=col.replace("_", " ").capitalize())
        tree.column(col, width=140, anchor="center")

    tree.pack(fill="both", expand=True, pady=20)

    # Buscador por nombre
    frame_buscar = tk.Frame(ventana, bg="#1e1e1e")
    frame_buscar.pack(pady=5)

    lbl_buscar = tk.Label(frame_buscar, text="Buscar por nombre:", bg="#1e1e1e", fg="white", font=("Segoe UI", 12))
    lbl_buscar.pack(side="left", padx=5)

    entry_buscar = tk.Entry(frame_buscar, font=("Segoe UI", 12))
    entry_buscar.pack(side="left", padx=5)
    entry_buscar.bind("<KeyRelease>", on_buscar)

    btn_eliminar = tk.Button(ventana, text="Eliminar Cliente", bg="#E72113", fg="white", font=("Segoe UI", 12, "bold"), command=eliminar_cliente)
    btn_eliminar.pack(pady=10)

    cargar_y_mostrar_clientes()

    # Cambiar comportamiento de Escape para que vuelva al menú principal
    def cerrar_ventana(event=None):
        ventana.destroy()
        root.deiconify()

    ventana.bind("<Escape>", cerrar_ventana)
