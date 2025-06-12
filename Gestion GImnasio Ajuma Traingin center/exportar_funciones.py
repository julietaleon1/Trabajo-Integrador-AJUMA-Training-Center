import json
import os
from datetime import datetime
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.utils import ImageReader
import openpyxl
from openpyxl.chart import BarChart, Reference
from openpyxl.styles import Font, Alignment, numbers
from openpyxl.drawing.image import Image as XLImage

# Configuración de rutas (ajustar según necesidad)
RUTA_CLIENTES = os.path.join(os.path.dirname(__file__), "clientes.json")
RUTA_LOGO = os.path.join(os.path.dirname(__file__), "logo.png")  # Cambiar a ruta relativa

# Valores de los planes (actualizables)
VALORES_PLAN = {
    "mensual": 30000,
    "trimestral": 72000,  
    "anual": 216000
}

# Métodos de pago aceptados (para validación)
METODOS_PAGO_ACEPTADOS = ["efectivo", "transferencia", "tarjeta", "mercado pago"]

def cargar_clientes():
    """Carga y valida la lista de clientes desde un archivo JSON."""
    if not os.path.exists(RUTA_CLIENTES):
        print(f"Archivo no encontrado: {RUTA_CLIENTES}")
        return []
    
    try:
        with open(RUTA_CLIENTES, "r", encoding="utf-8") as f:
            clientes = json.load(f)
            
            # Validación básica de datos
            clientes_validos = []
            for cliente in clientes:
                if not isinstance(cliente, dict):
                    continue
                
                # Normalizar método de pago
                if "pago" in cliente:
                    cliente["pago"] = cliente["pago"].lower()
                    if cliente["pago"] not in METODOS_PAGO_ACEPTADOS:
                        cliente["pago"] = "efectivo"  # Valor por defecto
                
                clientes_validos.append(cliente)
            
            return clientes_validos
            
    except json.JSONDecodeError:
        print("Error: Archivo JSON corrupto o mal formateado.")
    except Exception as e:
        print(f"Error inesperado al cargar clientes: {e}")
    
    return []

def exportar_factura_pdf(cliente, nombre_pdf="factura.pdf", ruta_logo=RUTA_LOGO):
    """Genera una factura en PDF para un cliente con mejor formato."""
    try:
        c = canvas.Canvas(nombre_pdf, pagesize=letter)
        ancho, alto = letter

        # Configuración de márgenes
        margen_izq = 50
        margen_sup = alto - 100
        espacio_linea = 20

        # Logo como marca de agua (con mejor manejo de errores)
        if os.path.exists(ruta_logo):
            try:
                logo = ImageReader(ruta_logo)
                c.saveState()
                c.translate(ancho / 2, alto / 2)
                c.setFillAlpha(0.1)
                c.drawImage(logo, -150, -150, width=300, height=300, mask='auto')
                c.restoreState()
            except Exception as e:
                print(f"Advertencia: Error al procesar logo - {e}")

        # Encabezado
        c.setFont("Helvetica-Bold", 18)
        c.drawCentredString(ancho / 2, margen_sup, "AJUMA TRAINING CENTER")
        c.setFont("Helvetica", 12)
        c.drawString(margen_izq, margen_sup - 30, "Dirección: Formosa, Argentina")
        c.drawString(margen_izq, margen_sup - 50, "Email: ajumatrainingcenter@gmail.com")
        c.drawString(margen_izq, margen_sup - 70, "Teléfono: +54 3704-123456")

        # Información de factura
        c.setFont("Helvetica-Bold", 16)
        c.drawCentredString(ancho / 2, margen_sup - 100, "FACTURA")
        
        fecha_actual = datetime.now()
        c.setFont("Helvetica", 10)
        c.drawRightString(ancho - margen_izq, margen_sup - 100, f"Fecha: {fecha_actual.strftime('%d/%m/%Y')}")
        c.drawRightString(ancho - margen_izq, margen_sup - 115, f"Hora: {fecha_actual.strftime('%H:%M:%S')}")

        # Datos del cliente
        c.setFont("Helvetica-Bold", 14)
        c.drawString(margen_izq, margen_sup - 150, "DATOS DEL CLIENTE:")
        c.setFont("Helvetica", 12)

        y_pos = margen_sup - 170
        campos = [
            ("Nombre", "nombre"),
            ("DNI", "dni"),
            ("Teléfono", "telefono"),
            ("Email", "email"),
            ("Membresía", "membresia"),
            ("Plan", "plan"),
            ("Fecha Ingreso", "fecha_ingreso"),
            ("Método Pago", "pago")
        ]

        for etiqueta, campo in campos:
            valor = cliente.get(campo, "N/A")
            # Formateo especial para algunos campos
            if campo == "pago":
                valor = valor.capitalize()
            elif campo == "plan":
                valor = valor.capitalize() + f" (${VALORES_PLAN.get(valor.lower(), 0):,})"
            
            c.drawString(margen_izq + 20, y_pos, f"{etiqueta}: {valor}")
            y_pos -= espacio_linea

        # Pie de página
        c.setFont("Helvetica-Oblique", 10)
        c.drawCentredString(ancho / 2, 50, "¡Gracias por elegir AJUMA Training Center!")
        c.drawCentredString(ancho / 2, 30, "Sistema de gestión desarrollado por [Tu Nombre]")

        c.save()
        print(f"✓ Factura PDF generada: {nombre_pdf}")
        return True
        
    except Exception as e:
        print(f"✗ Error al generar PDF: {e}")
        return False

def calcular_monto_mensual(plan):
    """Calcula el monto mensual con validación mejorada."""
    if not plan or not isinstance(plan, str):
        return 0
        
    plan = plan.lower()
    return VALORES_PLAN.get(plan, 0) / (3 if plan == "trimestral" else 12 if plan == "anual" else 1)

def exportar_excel_con_grafico(clientes, nombre_archivo="clientes_ganancias.xlsx"):
    """Genera un Excel mejor formateado con gráficos y resumen financiero."""
    if not clientes:
        print("No hay datos de clientes para exportar")
        return False

    try:
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = "Clientes"

        # Encabezados con estilo mejorado
        encabezados = [
            "Nombre", "DNI", "Teléfono", "Email", 
            "Membresía", "Plan", "Método de Pago", 
            "Fecha Ingreso", "Monto Mensual ($)"
        ]

        for col, encabezado in enumerate(encabezados, 1):
            celda = ws.cell(row=1, column=col, value=encabezado)
            celda.font = Font(bold=True, color="FFFFFF")
            celda.fill = openpyxl.styles.PatternFill("solid", fgColor="4F81BD")
            celda.alignment = Alignment(horizontal="center")

        # Datos de clientes
        fila = 2
        ganancia_total = 0
        montos_por_metodo = {metodo: 0 for metodo in METODOS_PAGO_ACEPTADOS}

        for cliente in clientes:
            plan = cliente.get("plan", "").lower()
            pago = cliente.get("pago", "efectivo").lower()
            monto = calcular_monto_mensual(plan)
            
            ganancia_total += monto
            montos_por_metodo[pago] += monto

            datos = [
                cliente.get("nombre", ""),
                cliente.get("dni", ""),
                cliente.get("telefono", ""),
                cliente.get("email", ""),
                cliente.get("membresia", ""),
                plan.capitalize(),
                pago.capitalize(),
                cliente.get("fecha_ingreso", ""),
                monto
            ]

            for col, valor in enumerate(datos, 1):
                ws.cell(row=fila, column=col, value=valor)
            
            fila += 1

        # Formato de moneda para montos
        for row in range(2, fila):
            ws.cell(row=row, column=9).number_format = numbers.FORMAT_CURRENCY_USD_SIMPLE

        # Resumen financiero
        fila_resumen = fila + 2
        ws.cell(row=fila_resumen, column=1, value="RESUMEN FINANCIERO").font = Font(bold=True, size=14)
        
        # Ganancia total
        ws.cell(row=fila_resumen+1, column=1, value="Ganancia Mensual Total:").font = Font(bold=True)
        ws.cell(row=fila_resumen+1, column=2, value=ganancia_total).font = Font(bold=True)
        ws.cell(row=fila_resumen+1, column=2).number_format = numbers.FORMAT_CURRENCY_USD_SIMPLE

        # Ganancias por método de pago
        fila_metodos = fila_resumen + 3
        ws.cell(row=fila_metodos, column=1, value="Método de Pago").font = Font(bold=True)
        ws.cell(row=fila_metodos, column=2, value="Monto ($)").font = Font(bold=True)
        
        fila_actual = fila_metodos + 1
        for metodo, monto in montos_por_metodo.items():
            if monto > 0:
                ws.cell(row=fila_actual, column=1, value=metodo.capitalize())
                ws.cell(row=fila_actual, column=2, value=monto).number_format = numbers.FORMAT_CURRENCY_USD_SIMPLE
                fila_actual += 1

        # Gráfico de ganancias por método
        chart = BarChart()
        chart.type = "col"
        chart.style = 10
        chart.title = "Distribución de Ganancias por Método de Pago"
        chart.y_axis.title = "Monto ($)"
        chart.x_axis.title = "Método de Pago"

        data = Reference(ws, min_col=2, min_row=fila_metodos+1, max_row=fila_actual-1)
        categorias = Reference(ws, min_col=1, min_row=fila_metodos+1, max_row=fila_actual-1)
        
        chart.add_data(data, titles_from_data=False)
        chart.set_categories(categorias)
        chart.shape = 4
        
        ws.add_chart(chart, f"D{fila_resumen}")

        # Ajustar anchos de columnas automáticamente
        for col in ws.columns:
            max_length = max(len(str(cell.value)) for cell in col) + 2
            ws.column_dimensions[col[0].column_letter].width = max_length

        wb.save(nombre_archivo)
        print(f"✓ Excel generado: {nombre_archivo}")
        
        # Mostrar resumen por consola
        print(f"\nResumen financiero:")
        print(f"- Ganancia total mensual: ${ganancia_total:,.2f}")
        for metodo, monto in montos_por_metodo.items():
            if monto > 0:
                print(f"- {metodo.capitalize()}: ${monto:,.2f}")
        
        return True
        
    except Exception as e:
        print(f"✗ Error al generar Excel: {e}")
        return False

if __name__ == "__main__":
    print("\n" + "="*50)
    print(" SISTEMA DE GESTIÓN AJUMA TRAINING CENTER")
    print("="*50 + "\n")

    # Cargar datos
    clientes = cargar_clientes()
    print(f"Clientes cargados: {len(clientes)}")

    if not clientes:
        print("No hay clientes para procesar. Verifique el archivo clientes.json")
    else:
        # Exportar factura PDF (primer cliente en efectivo)
        cliente_efectivo = next((c for c in clientes if c.get("pago", "").lower() == "efectivo"), None)
        if cliente_efectivo:
            if not exportar_factura_pdf(cliente_efectivo):
                print("Advertencia: No se pudo generar la factura PDF")
        else:
            print("Info: No se encontraron clientes con pago en efectivo para factura")

        # Exportar reporte Excel completo
        if not exportar_excel_con_grafico(clientes):
            print("Error: No se pudo generar el reporte Excel")