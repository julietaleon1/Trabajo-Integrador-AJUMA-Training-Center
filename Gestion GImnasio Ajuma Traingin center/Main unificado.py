#Importacion de librerias
import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk
from agregar_cliente import abrir_agregar_cliente
from ver_clientes import abrir_ver_clientes
from rutinas import abrir_rutina
from Profesores import abrir_modulo_profesores
from exportar import abrir_ventana_exportar
import subprocess
import sys
import os
#inicio de sesion 
CONTRASEÑA_CORRECTA = "ajumagym"

#Funciones generales para la interfaz
def salir():
    root.destroy()

def volver_al_menu():
    root.deiconify()

def animar_titulo(texto_completo, etiqueta, i=0):
    if i <= len(texto_completo):
        etiqueta.config(text=texto_completo[:i])
        etiqueta.after(100, lambda: animar_titulo(texto_completo, etiqueta, i+1))

def parpadear_color(etiqueta, colores, i=0):
    etiqueta.config(fg=colores[i % len(colores)])
    etiqueta.after(700, lambda: parpadear_color(etiqueta, colores, i+1))

def animar_hover_boton(boton, color_base, color_hover):
    def ampliar(event):
        boton.config(bg=color_hover)
        boton.config(font=("Segoe UI", 15, "bold"))

    def reducir(event):
        boton.config(bg=color_base)
        boton.config(font=("Segoe UI", 14))

    boton.bind("<Enter>", ampliar)
    boton.bind("<Leave>", reducir)

#Funciones de acceso
def mostrar_login():
    login_ventana = tk.Toplevel()
    login_ventana.title("Acceso al Sistema")
    login_ventana.geometry("400x250")  # Aumentamos el alto para el nuevo botón
    login_ventana.configure(bg="#111111")
    login_ventana.grab_set() 
    login_ventana.resizable(False, False)
    
    # Centrar la ventana
    pantalla_ancho = login_ventana.winfo_screenwidth()
    pantalla_alto = login_ventana.winfo_screenheight()
    x = (pantalla_ancho // 2) - (400 // 2)
    y = (pantalla_alto // 2) - (250 // 2)
    login_ventana.geometry(f'400x250+{x}+{y}')

    # Frame principal
    frame_login = tk.Frame(login_ventana, bg="#111111")
    frame_login.pack(pady=20, padx=20, fill="both", expand=True)

    tk.Label(frame_login, text="Ingrese la contraseña:", font=("Segoe UI", 14), bg="#111111", fg="white").pack(pady=10)
    
    # Frame para el campo de contraseña y botón de mostrar
    frame_password = tk.Frame(frame_login, bg="#111111")
    frame_password.pack()
    
    entry_contraseña = tk.Entry(frame_password, show="*", font=("Segoe UI", 14), width=20, bd=2, relief="flat")
    entry_contraseña.pack(side="left", padx=5)
    
    # Botón para mostrar/ocultar contraseña
    mostrar_icon = Image.open("eye_icon.png").resize((20, 20)) if os.path.exists("eye_icon.png") else None
    if mostrar_icon:
        mostrar_icon = ImageTk.PhotoImage(mostrar_icon)
        btn_mostrar = tk.Button(frame_password, image=mostrar_icon, command=lambda: toggle_password(entry_contraseña, btn_mostrar), 
                              bg="#111111", activebackground="#111111", bd=0)
        btn_mostrar.image = mostrar_icon
    else:
        btn_mostrar = tk.Button(frame_password, text="👁️", command=lambda: toggle_password(entry_contraseña, btn_mostrar), 
                              font=("Segoe UI", 10), bg="#111111", fg="white", bd=0)
    btn_mostrar.pack(side="left")
    
    # Función para alternar entre mostrar/ocultar contraseña
    def toggle_password(entry, button):
     if entry['show'] == "*":
        entry.config(show="")
        if not mostrar_icon:
            button.config(text="👁️")
        else:
            button.config(image=mostrar_icon)
     else:
        entry.config(show="*")
        if not mostrar_icon:
            button.config(text="👁️")
        else:
            button.config(image=mostrar_icon)

    
    #Verificacion de contraseña
    def verificar_contraseña():
        if entry_contraseña.get() == CONTRASEÑA_CORRECTA:
            login_ventana.destroy()
            iniciar_menu()
        else:
            messagebox.showerror("Error", "Contraseña incorrecta.")
            entry_contraseña.delete(0, tk.END)
            entry_contraseña.focus()

    # Frame para botones
    frame_botones = tk.Frame(frame_login, bg="#111111")
    frame_botones.pack(pady=15)
    
    btn_ingresar = tk.Button(frame_botones, text="Ingresar", command=verificar_contraseña,
                            font=("Segoe UI", 12), bg="#333333", fg="white", width=10)
    btn_ingresar.pack(side="left", padx=10)
    
    btn_cancelar = tk.Button(frame_botones, text="Cancelar", command=salir,
                            font=("Segoe UI", 12), bg="#555555", fg="white", width=10)
    btn_cancelar.pack(side="left", padx=10)

    # Permitir Enter para ingresar
    login_ventana.bind("<Return>", lambda e: verificar_contraseña())
    
    # Enfocar el campo de contraseña al abrir
    entry_contraseña.focus()

def iniciar_menu():
    root.deiconify()

#Interfaz principal
root = tk.Tk()
root.title("Sistema de Gestión de Gimnasio")
root.attributes('-fullscreen', True)
root.withdraw() 

# Fondo
<<<<<<< HEAD
imagen_fondo = Image.open("./Imagen Gimnasio IA.jpg")
ancho_pantalla = root.winfo_screenwidth()
alto_pantalla = root.winfo_screenheight()
imagen_fondo = imagen_fondo.resize((ancho_pantalla, alto_pantalla))
fondo_tk = ImageTk.PhotoImage(imagen_fondo)

label_fondo = tk.Label(root, image=fondo_tk)
label_fondo.place(x=0, y=0, relwidth=1, relheight=1)
=======
try:
    imagen_fondo = Image.open("C:/Users/Usuario/Desktop/Gestion GImnasio Ajuma Traingin center/Imagen Gimnasio IA.jpg")
    ancho_pantalla = root.winfo_screenwidth()
    alto_pantalla = root.winfo_screenheight()
    imagen_fondo = imagen_fondo.resize((ancho_pantalla, alto_pantalla))
    fondo_tk = ImageTk.PhotoImage(imagen_fondo)
    label_fondo = tk.Label(root, image=fondo_tk)
    label_fondo.place(x=0, y=0, relwidth=1, relheight=1)
except:
    # Fondo alternativo si no se carga la imagen
    root.configure(bg='#000000')
>>>>>>> 5e56511e8cce752944d920bd6b9a536381a9628b

contenedor = tk.Frame(root, bg='#000000')
contenedor.place(relx=0.5, rely=0.5, anchor='center')

# Título animado
titulo = tk.Label(contenedor, text="", font=("Segoe UI", 36, "bold"), fg="white", bg="#000000")
titulo.pack(pady=40)
animar_titulo("Sistema de Gestión de Gimnasio", titulo)
parpadear_color(titulo, ["white", "#AAAAAA", "#888888"])

# Botones
def crear_boton(texto, comando):
    btn = tk.Button(contenedor, text=texto, font=("Segoe UI", 14),
                    bg="#222222", fg="white", activebackground="#444444",
                    relief="flat", command=comando)
    btn.pack(pady=18, fill="x")
    animar_hover_boton(btn, "#222222", "#444444")

crear_boton("Gestionar Clientes", lambda: (root.withdraw(), abrir_agregar_cliente(root)))
crear_boton("Ver Clientes", lambda: (root.withdraw(), abrir_ver_clientes(root)))
crear_boton("Ver Rutinas", lambda: (root.withdraw(), abrir_rutina(root, volver_al_menu)))
crear_boton("Profesor", lambda: (root.withdraw(), abrir_modulo_profesores(volver_al_menu)))
crear_boton("Exportar", lambda: (root.withdraw(), abrir_ventana_exportar(root, volver_al_menu)))
crear_boton("Salir", salir)

# Script de recordatorio
subprocess.Popen([sys.executable, "RecordatorioVencimiento.py"])

# Escape en menú principal cierra programa
root.bind('<Escape>', lambda e: salir())

# Mostrar pantalla de login
mostrar_login()

# Bucle principal
root.mainloop()