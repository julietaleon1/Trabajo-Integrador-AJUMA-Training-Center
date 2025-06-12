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
    login_ventana.geometry("400x200")
    login_ventana.configure(bg="#111111")
    login_ventana.grab_set() 
    login_ventana.resizable(False, False)

    tk.Label(login_ventana, text="Ingrese la contraseña:", font=("Segoe UI", 14), bg="#111111", fg="white").pack(pady=20)
    entry_contraseña = tk.Entry(login_ventana, show="*", font=("Segoe UI", 14), width=25)
    entry_contraseña.pack()
    
    #Verificacion de contraseña
    def verificar_contraseña():
        if entry_contraseña.get() == CONTRASEÑA_CORRECTA:
            login_ventana.destroy()
            iniciar_menu()
        else:
            messagebox.showerror("Error", "Contraseña incorrecta.")

    tk.Button(login_ventana, text="Ingresar", command=verificar_contraseña,
              font=("Segoe UI", 12), bg="#333333", fg="white").pack(pady=20)

    # Permitir Enter para ingresar
    login_ventana.bind("<Return>", lambda e: verificar_contraseña())

def iniciar_menu():
    root.deiconify()

#Interfaz principal
root = tk.Tk()
root.title("Sistema de Gestión de Gimnasio")
root.attributes('-fullscreen', True)
root.withdraw() 

# Fondo
imagen_fondo = Image.open("C:/Users/Usuario/Desktop/Gestion GImnasio Ajuma Traingin center/Imagen Gimnasio IA.jpg")
ancho_pantalla = root.winfo_screenwidth()
alto_pantalla = root.winfo_screenheight()
imagen_fondo = imagen_fondo.resize((ancho_pantalla, alto_pantalla))
fondo_tk = ImageTk.PhotoImage(imagen_fondo)

label_fondo = tk.Label(root, image=fondo_tk)
label_fondo.place(x=0, y=0, relwidth=1, relheight=1)

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
