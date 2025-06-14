#importamos librerias
import tkinter as tk
from tkinter import ttk, messagebox
from tkcalendar import DateEntry
import json
import os
from datetime import datetime
import subprocess
import sys
import random
from bienvenida_cliente import enviar_bienvenida

#creamos constante de archivo json
RUTA_ARCHIVO = "clientes.json"

#Funcion principal
def abrir_agregar_cliente(root):
    ventana = tk.Toplevel(root)
    ventana.title("Gestión de Clientes")
    ventana.attributes("-fullscreen", True)
    ventana.configure(bg="#2a2a2a")
    
    # Estilo mejorado para los widgets
    estilo = {
        "bg": "#2a2a2a",
        "fg": "white",
        "font": ("Segoe UI", 11),
        "relief": "flat",
        "bd": 0
    }
    
    estilo_botones = {
        "font": ("Segoe UI", 10, "bold"),
        "width": 14,
        "height": 1,
        "padx": 5,
        "pady": 5,
        "bd": 0,
        "highlightthickness": 0
    }

    #Funcion para cerrar ventana 
    def cerrar_ventana():
        ventana.destroy()
        root.deiconify()
        root.focus_set()

    ventana.bind("<Escape>", lambda e: cerrar_ventana())
    ventana.protocol("WM_DELETE_WINDOW", cerrar_ventana)

    entradas = []
    
    #cargar datos cliente
    def cargar_clientes():
        if os.path.exists(RUTA_ARCHIVO):
            with open(RUTA_ARCHIVO, "r", encoding="utf-8") as archivo:
                try:
                    return json.load(archivo)
                except json.JSONDecodeError:
                    return []
        return []
    
    #guardar datos clientes
    def guardar_clientes(clientes):
        with open(RUTA_ARCHIVO, "w", encoding="utf-8") as archivo:
            json.dump(clientes, archivo, indent=4)
    
    #actualizar json desde el treeview
    def actualizar_json_desde_treeview():
        datos = []
        for item in tree.get_children():
            valores = tree.item(item)["values"]
            id_cliente = tree.item(item)["tags"][0]
            datos.append({
                "id": id_cliente,
                "nombre": valores[0],
                "dni": valores[1],
                "telefono": valores[2],
                "email": valores[3],
                "membresia": valores[4],
                "plan": valores[5],
                "fecha_ingreso": valores[6],
                "tipo_pago": valores[7],
            })
        guardar_clientes(datos)
    
    #validacion datos
    def validar_nombre(nombre):
        return nombre.replace(" ", "").isalpha()

    def validar_dni_telefono(valor):
        return valor.isdigit()

    def limpiar_campos():
        for entrada in entradas:
            if isinstance(entrada, (tk.Entry, ttk.Combobox)):
                entrada.delete(0, tk.END)
            elif isinstance(entrada, DateEntry):
                entrada.set_date(datetime.today())
    
    #Funcion para agregar cliente y validaciones
    def agregar_cliente():
        datos = []
        for entrada in entradas:
            if isinstance(entrada, tk.Entry):
                datos.append(entrada.get().strip())
            elif isinstance(entrada, ttk.Combobox):
                datos.append(entrada.get())
            elif isinstance(entrada, DateEntry):
                datos.append(entrada.get_date().strftime("%Y-%m-%d"))

        if all(datos):
            nombre, dni, telefono, email = datos[0], datos[1], datos[2], datos[3]

            if not validar_nombre(nombre):
                messagebox.showerror("Nombre inválido", "El campo 'Nombre' solo debe contener letras y espacios.")
                return
            if not validar_dni_telefono(dni):
                messagebox.showerror("DNI inválido", "El campo 'DNI' solo debe contener números.")
                return
            if not validar_dni_telefono(telefono):
                messagebox.showerror("Teléfono inválido", "El campo 'Teléfono' solo debe contener números.")
                return
            if "@" not in email:
                messagebox.showerror("Email inválido", "El campo 'Email' debe contener una arroba (@).")
                return

            id_cliente = str(random.randint(10000, 99999))
            tree.insert("", "end", values=datos, tags=(id_cliente,))
            actualizar_json_desde_treeview()
            limpiar_campos()

            subprocess.Popen([sys.executable, "RecordatorioVencimiento.py"])

            try:
                plan = datos[5]
                enviado = enviar_bienvenida(nombre, email, plan, id_cliente)
                if enviado:
                    print(f"Correo de bienvenida enviado a {email}")
            except Exception as e:
                print(f"Error al enviar correo: {e}")
        else:
            messagebox.showwarning("Campos incompletos", "Complete todos los campos.")
    
    #Poder seleccionar cliente en el tree
    def seleccionar_cliente(event):
        item = tree.selection()
        if item:
            valores = tree.item(item[0], "values")
            for i, valor in enumerate(valores):
                if isinstance(entradas[i], (tk.Entry, ttk.Combobox)):
                    entradas[i].delete(0, tk.END)
                    entradas[i].insert(0, valor)
                elif isinstance(entradas[i], DateEntry):
                    try:
                        fecha_dt = datetime.strptime(valor, "%Y-%m-%d").date()
                        entradas[i].set_date(fecha_dt)
                    except Exception:
                        entradas[i].set_date(datetime.today())
    
    #Modifcar cliente
    def modificar_cliente():
        item = tree.selection()
        if item:
            nuevos_datos = []
            for entrada in entradas:
                if isinstance(entrada, tk.Entry):
                    nuevos_datos.append(entrada.get().strip())
                elif isinstance(entrada, ttk.Combobox):
                    nuevos_datos.append(entrada.get())
                elif isinstance(entrada, DateEntry):
                    nuevos_datos.append(entrada.get_date().strftime("%Y-%m-%d"))

            if all(nuevos_datos):
                tree.item(item, values=nuevos_datos)
                actualizar_json_desde_treeview()
                limpiar_campos()
            else:
                messagebox.showwarning("Campos incompletos", "Complete todos los campos.")
        else:
            messagebox.showinfo("Seleccionar cliente", "Seleccione un cliente de la lista.")

    confirmacion_activa = [False]

    frame_confirmacion = tk.Frame(ventana, bg="#2a2a2a")
    label_confirmacion = tk.Label(frame_confirmacion, text="¿Seguro que querés eliminar este cliente?", 
                                font=("Segoe UI", 11), fg="white", bg="#2a2a2a")
    boton_confirmar = tk.Button(frame_confirmacion, text="Sí, eliminar", bg="#E72113", 
                              fg="white", font=("Segoe UI", 10, "bold"), command=lambda: confirmar_eliminacion())
    boton_cancelar = tk.Button(frame_confirmacion, text="Cancelar", bg="#444444", 
                             fg="white", font=("Segoe UI", 10, "bold"), command=lambda: cancelar_eliminacion())
    
    #Eliminar cliente
    def eliminar_cliente():
        item = tree.selection()
        if item:
            if not confirmacion_activa[0]:
                confirmacion_activa[0] = True
                frame_confirmacion.pack(pady=10)
                label_confirmacion.pack(side="left", padx=10)
                boton_confirmar.pack(side="left", padx=5)
                boton_cancelar.pack(side="left", padx=5)
        else:
            messagebox.showinfo("Seleccionar cliente", "Seleccione un cliente para eliminar.")

    def confirmar_eliminacion():
        item = tree.selection()
        if item:
            tree.delete(item)
            actualizar_json_desde_treeview()
            limpiar_campos()
        cancelar_eliminacion()

    def cancelar_eliminacion():
        confirmacion_activa[0] = False
        label_confirmacion.pack_forget()
        boton_confirmar.pack_forget()
        boton_cancelar.pack_forget()
        frame_confirmacion.pack_forget()

    # Frame de búsqueda
    frame_busqueda = tk.Frame(ventana, bg="#2a2a2a")
    frame_busqueda.pack(pady=10, padx=20, fill="x")
    
    lbl_buscar = tk.Label(frame_busqueda, text="Buscar:", **estilo)
    lbl_buscar.pack(side="left", padx=5)
    
    entry_busqueda = tk.Entry(frame_busqueda, width=50, font=("Segoe UI", 11), 
                            bg="#3a3a3a", fg="white", insertbackground="white", relief="flat")
    entry_busqueda.pack(side="left", padx=5, fill="x", expand=True)
    
    btn_buscar = tk.Button(frame_busqueda, text="Buscar", bg="#1E90FF", fg="white", 
                         command=lambda: buscar_cliente(), **estilo_botones)
    btn_buscar.pack(side="left", padx=5)
    
    def buscar_cliente():
        termino = entry_busqueda.get().lower()
        if not termino:
            return
            
        for item in tree.get_children():
            valores = tree.item(item)["values"]
            if any(termino in str(valor).lower() for valor in valores):
                tree.selection_set(item)
                tree.focus(item)
                tree.see(item)
                break
        else:
            messagebox.showinfo("Búsqueda", "No se encontraron coincidencias.")

    frame_form = tk.Frame(ventana, bg="#2a2a2a")
    frame_form.pack(pady=20, padx=20)
    
    #campos o entradas
    campos = [
        ("Nombre", tk.Entry),
        ("DNI", tk.Entry),
        ("Telefono", tk.Entry),
        ("Email", tk.Entry),
        ("Membresía", ttk.Combobox, ["Musculacion", "Pilates", "Cardio", "Funcional"]),
        ("Plan", ttk.Combobox, ["Mensual $30.000", "Trimestral $72.000", "Anual $216.000"]),
        ("Fecha de ingreso", DateEntry),
        ("Tipo de pago", ttk.Combobox, ["Efectivo", "Transferencia"])
    ]

    for i, (campo, tipo, *opciones) in enumerate(campos):
        tk.Label(frame_form, text=campo, **estilo).grid(row=i, column=0, padx=10, pady=8, sticky="e")

        if tipo == tk.Entry:
            entrada = tipo(frame_form, width=50, font=("Segoe UI", 11), 
                         bg="#3a3a3a", fg="white", insertbackground="white", relief="flat")
        elif tipo == ttk.Combobox:
            entrada = tipo(frame_form, values=opciones[0], state="readonly", width=47, 
                         font=("Segoe UI", 11), style="TCombobox")
            entrada.current(0)
        elif tipo == DateEntry:
            entrada = tipo(frame_form, width=47, font=("Segoe UI", 11), 
                         background='#3a3a3a', foreground='white', 
                         bordercolor='#3a3a3a', date_pattern="yyyy-mm-dd")

        entrada.grid(row=i, column=1, pady=8, sticky="w")
        entradas.append(entrada)

    frame_botones = tk.Frame(ventana, bg="#2a2a2a")
    frame_botones.pack(pady=15)
    
    #Colores de botones y estilo
    colores = {
        "Agregar": "#15CC1B",
        "Modificar": "#F321BB",
        "Eliminar": "#E72113",
        "Limpiar": "#EF6F0D",
        "Cerrar": "#000000"
    }
    
    #Acciones con sus respectivas funciones
    acciones = [
        ("Agregar", agregar_cliente),
        ("Modificar", modificar_cliente),
        ("Eliminar", eliminar_cliente),
        ("Limpiar", limpiar_campos),
        ("Cerrar", cerrar_ventana)
    ]

    for i, (texto, accion) in enumerate(acciones):
        tk.Button(frame_botones, text=texto, command=accion, bg=colores[texto], 
                fg="white", **estilo_botones).grid(row=0, column=i, padx=6)
    
    # Configuración del Treeview con estilo mejorado
    style = ttk.Style()
    style.theme_use("clam")
    style.configure("Treeview", 
                  background="#3a3a3a",
                  foreground="white",
                  fieldbackground="#3a3a3a",
                  font=("Segoe UI", 10),
                  rowheight=25,
                  bordercolor="#3a3a3a")
    style.configure("Treeview.Heading", 
                  background="#444444",
                  foreground="white",
                  font=("Segoe UI", 11, "bold"),
                  relief="flat")
    style.map("Treeview", background=[("selected", "#1E90FF")])
    
    #columnas del treeview con datos de los clientes
    columnas = ("nombre", "dni", "telefono", "email", "membresia", "plan", "fecha_ingreso", "tipo_pago")
    tree = ttk.Treeview(ventana, columns=columnas, show="headings")
    
    for col in columnas:
        tree.heading(col, text=col.replace("_", " ").capitalize())
        tree.column(col, anchor="center", width=140, minwidth=100)

    # Añadir scrollbar
    scrollbar = ttk.Scrollbar(ventana, orient="vertical", command=tree.yview)
    scrollbar.pack(side="right", fill="y")
    tree.configure(yscrollcommand=scrollbar.set)
    
    tree.pack(pady=20, padx=20, fill="both", expand=True)

    tree.bind("<<TreeviewSelect>>", seleccionar_cliente)

    # Cargar datos existentes
    clientes_cargados = cargar_clientes()
    for cliente in clientes_cargados:
        valores = (
            cliente.get("nombre", ""),
            cliente.get("dni", ""),
            cliente.get("telefono", ""),
            cliente.get("email", ""),
            cliente.get("membresia", ""),
            cliente.get("plan", ""),
            cliente.get("fecha_ingreso", ""),
            cliente.get("tipo_pago", "Efectivo")
        )
        tree.insert("", "end", values=valores, tags=(cliente.get("id", str(random.randint(10000, 99999))),))

    root.withdraw()
    ventana.mainloop()