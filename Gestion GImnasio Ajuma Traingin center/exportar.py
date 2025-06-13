import tkinter as tk
from exportar_funciones import cargar_clientes, exportar_factura_pdf, exportar_excel_con_grafico

def abrir_ventana_exportar(root, volver_al_menu):
    ventana = tk.Toplevel()
    ventana.title("Exportar Datos")
    ventana.configure(bg="#2c2c2c")
    ventana.attributes('-fullscreen', True)

    titulo = tk.Label(ventana, text="Exportar Información", font=("Helvetica", 28, "bold"),
                      fg="white", bg="#2c2c2c")
    titulo.pack(pady=40)

    def generar_pdf():
        clientes = cargar_clientes()
        cliente_efectivo = next((c for c in clientes if c.get("tipo_pago", "").lower() == "efectivo"), None)
        if cliente_efectivo:
            exportar_factura_pdf(cliente_efectivo, nombre_pdf="factura_cliente_efectivo.pdf")
        else:
            print("No se encontró cliente que pague en efectivo.")

    boton_pdf = tk.Button(ventana, text="Exportar Factura (PDF)", font=("Helvetica", 16), bg="#3b8ed0", fg="white",
                          command=generar_pdf)
    boton_pdf.pack(pady=20)

    def generar_excel():
        clientes = cargar_clientes()
        exportar_excel_con_grafico(clientes, nombre_archivo="clientes_ganancias.xlsx")

    boton_excel = tk.Button(ventana, text="Exportar Excel de Ganancias", font=("Helvetica", 16), bg="#3b8ed0", fg="white",
                            command=generar_excel)
    boton_excel.pack(pady=20)

    def cerrar():
        ventana.destroy()
        root.deiconify()  # Mostrar ventana principal de nuevo
        if volver_al_menu:
            volver_al_menu()  # Ejecutar función de retorno si existe

    boton_cerrar = tk.Button(ventana, text="Volver al Menú", font=("Helvetica", 16), bg="#5e5e5e", fg="white",
                             command=cerrar)
    boton_cerrar.pack(pady=30)

    ventana.bind('<Escape>', lambda e: cerrar())
