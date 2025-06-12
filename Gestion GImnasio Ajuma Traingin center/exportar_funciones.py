import json
import os
from datetime import datetime
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.utils import ImageReader
import openpyxl
from openpyxl.chart import BarChart, Reference
from openpyxl.styles import Font, Alignment

RUTA_CLIENTES = "clientes.json"
RUTA_LOGO = "logo-ajuma.png"  

# Valores de los planes
VALORES_PLAN = {
    "mensual": 30000,
    "trimestral": 72000,  
    "anual": 216000
}

def cargar_clientes():
    """Carga la lista de clientes desde un archivo JSON."""
    if os.path.exists(RUTA_CLIENTES):
        with open(RUTA_CLIENTES, "r", encoding="utf-8") as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                print("Error al decodificar JSON. Archivo corrupto o vacío.")
                return []
    return []

def exportar_factura_pdf(cliente, nombre_pdf="factura.pdf", ruta_logo=RUTA_LOGO):
    """Genera una factura en PDF para un cliente dado."""
    try:
        c = canvas.Canvas(nombre_pdf, pagesize=letter)
        ancho, alto = letter

        # Logo del gym como marca de agua 
        if os.path.exists(ruta_logo):
            try:
                logo = ImageReader(ruta_logo)
                c.saveState()
                c.translate(ancho / 2, alto / 2)
                c.setFillAlpha(0.1)
                logo_ancho = 300
                logo_alto = 300
                c.drawImage(logo, -logo_ancho / 2, -logo_alto / 2, 
                          width=logo_ancho, height=logo_alto, mask='auto')
                c.restoreState()
            except Exception as e:
                print(f"Advertencia: No se pudo cargar el logo: {e}")

        # Títulos
        c.setFont("Helvetica-Bold", 20)
        c.drawCentredString(ancho / 2, alto - 100, "Factura Tipo X")
        c.setFont("Helvetica-Bold", 14)
        c.drawString(50, alto - 150, "AJUMA Training Center")
        c.setFont("Helvetica", 12)
        c.drawString(50, alto - 170, "Dirección: Formosa, Argentina")
        c.drawString(50, alto - 190, "Email: ajumatrainingcenter@gmail.com")

        # Fecha y hora
        fecha_obj = datetime.now()
        fecha_str = fecha_obj.strftime("%d/%m/%Y")
        hora_str = fecha_obj.strftime("%H:%M:%S")

        c.drawString(400, alto - 150, f"Fecha: {fecha_str}")
        c.drawString(400, alto - 170, f"Hora: {hora_str}")

        # Datos del cliente
        c.setFont("Helvetica-Bold", 14)
        c.drawString(50, alto - 230, "Datos del Cliente")
        c.setFont("Helvetica", 12)

        y = alto - 250
        campos = ["nombre", "dni", "telefono", "email", "membresia", "plan", "fecha_ingreso", "pago"]
        for campo in campos:
            valor = cliente.get(campo, "N/A")
            etiqueta = campo.capitalize().replace('_', ' ')
            c.drawString(70, y, f"{etiqueta}: {valor}")
            y -= 20

        c.save()
        print(f"Factura PDF generada: {nombre_pdf}")
        return True
    except Exception as e:
        print(f"Error al generar PDF: {e}")
        return False

def calcular_monto_mensual(plan):
    """Devuelve el monto mensual estimado según el plan."""
    plan = plan.lower() if plan else ""
    if plan == "mensual":
        return VALORES_PLAN["mensual"]
    elif plan == "trimestral":
        return VALORES_PLAN["trimestral"] / 3
    elif plan == "anual":
        return VALORES_PLAN["anual"] / 12
    else:
        return 0

def exportar_excel_con_grafico(clientes, nombre_archivo="clientes_ganancias.xlsx"):
    """Genera un archivo Excel con clientes, su info y gráfico de ganancia mensual."""
    try:
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = "Clientes"

        # Encabezados
        encabezados = [
            "Nombre", "DNI", "Teléfono", "Email", "Membresía", "Plan",
            "Método de Pago", "Fecha de Ingreso", "Monto Mensual"
        ]

        # Escribir encabezados
        for col, encabezado in enumerate(encabezados, start=1):
            celda = ws.cell(row=1, column=col, value=encabezado)
            celda.font = Font(bold=True)
            celda.alignment = Alignment(horizontal='center')

        fila = 2
        ganancia_mensual_total = 0
        montos_por_metodo = {"efectivo": 0, "transferencia": 0, "tarjeta": 0}

        for cliente in clientes:
            nombre = cliente.get("nombre", "")
            dni = cliente.get("dni", "")
            telefono = cliente.get("telefono", "")
            email = cliente.get("email", "")
            membresia = cliente.get("membresia", "")
            plan = cliente.get("plan", "").lower()
            pago = cliente.get("pago", "").lower()
            fecha_ingreso = cliente.get("fecha_ingreso", "")

            monto_mensual = calcular_monto_mensual(plan)
            ganancia_mensual_total += monto_mensual
            
            # Sumar al método de pago correspondiente
            if pago in montos_por_metodo:
                montos_por_metodo[pago] += monto_mensual
            else:
                montos_por_metodo["efectivo"] += monto_mensual  # Por defecto

            datos_fila = [
                nombre, dni, telefono, email, membresia, plan,
                pago.capitalize(), fecha_ingreso, monto_mensual
            ]

            for col, valor in enumerate(datos_fila, start=1):
                ws.cell(row=fila, column=col, value=valor)
            fila += 1

        # Resumen de ganancias por método de pago
        ws.cell(row=fila+2, column=1, value="RESUMEN DE GANANCIAS").font = Font(bold=True)
        
        # Ganancia total mensual
        ws.cell(row=fila+3, column=1, value="Ganancia Mensual Total:")
        celda_total = ws.cell(row=fila+3, column=2, value=ganancia_mensual_total)
        celda_total.font = Font(bold=True)
        
        # Ganancias por método de pago
        row_counter = fila+4
        ws.cell(row=row_counter, column=1, value="Ganancias por Método de Pago:").font = Font(bold=True)
        row_counter += 1
        
        for metodo, monto in montos_por_metodo.items():
            if monto > 0:  # Solo mostrar métodos con montos positivos
                ws.cell(row=row_counter, column=1, value=f"{metodo.capitalize()}:")
                ws.cell(row=row_counter, column=2, value=monto)
                row_counter += 1

        # Gráfico de barras
        chart = BarChart()
        chart.title = "Ganancias por Método de Pago"
        chart.y_axis.title = "Monto ($)"
        chart.x_axis.title = "Método de Pago"

        # Preparar datos para el gráfico
        data_labels = []
        data_values = []
        for metodo, monto in montos_por_metodo.items():
            if monto > 0:
                data_labels.append(metodo.capitalize())
                data_values.append(monto)

        # Escribir datos para el gráfico
        start_row = row_counter + 2
        for i, (label, value) in enumerate(zip(data_labels, data_values), start=1):
            ws.cell(row=start_row+i, column=1, value=label)
            ws.cell(row=start_row+i, column=2, value=value)

        # Referencias para el gráfico
        data = Reference(ws, min_col=2, min_row=start_row+1, max_row=start_row+len(data_values))
        categories = Reference(ws, min_col=1, min_row=start_row+1, max_row=start_row+len(data_values))
        
        chart.add_data(data, titles_from_data=False)
        chart.set_categories(categories)

        # Añadir gráfico
        ws.add_chart(chart, f"D{start_row}")

        # Ajustar anchos de columnas
        for col in ws.columns:
            max_length = 0
            column = col[0].column_letter
            for cell in col:
                try:
                    if len(str(cell.value)) > max_length:
                        max_length = len(str(cell.value))
                except:
                    pass
            adjusted_width = (max_length + 2)
            ws.column_dimensions[column].width = adjusted_width

        wb.save(nombre_archivo)
        print(f"Excel generado: {nombre_archivo}")
        return True
    except Exception as e:
        print(f"Error al generar Excel: {e}")
        return False

if __name__ == "__main__":
    clientes = cargar_clientes()
    
    if not clientes:
        print("No hay clientes para procesar.")
    else:
        # Exportar factura PDF para el primer cliente que paga en efectivo
        cliente_efectivo = next((c for c in clientes if c.get("pago", "").lower() == "efectivo"), None)
        if cliente_efectivo:
            if not exportar_factura_pdf(cliente_efectivo, nombre_pdf="factura_cliente_efectivo.pdf"):
                print("Hubo un problema al generar el PDF.")
        else:
            print("No se encontró cliente que pague en efectivo para exportar PDF.")

        # Exportar Excel con todos los clientes
        if not exportar_excel_con_grafico(clientes, nombre_archivo="clientes_ganancias.xlsx"):
            print("Hubo un problema al generar el Excel.")