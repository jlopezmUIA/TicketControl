import os
from django.conf import settings
from django.templatetags.static import static
from datetime import date
from datetime import datetime
from escpos.printer import Network

def imprimir(codigo, departamento):
    fecha_actual = date.today().strftime('%Y-%m-%d')
    hora_actual = datetime.now()
    hora_actual_str = hora_actual.strftime('%H:%M:%S')
    printer_ip = '192.168.8.35'
    img_path = os.path.join(settings.STATIC_ROOT,'img', 'logo.png')

    printer = Network(printer_ip)
    printer.open()
    printer.set(align='center')
    printer.image(img_path, impl="bitImageColumn")
    printer.text("\n")

    printer.set(align='center', font='1', width=2, height=2, text_type='italic')
    printer.text("Bienvenido")
    printer.text("\n\n")

    printer.set(align='center', font='1', width=5, height=5)
    printer.text(""+codigo+"\n\n")

    printer.set(align='center', width=1, height=1)
    printer.text(departamento)
    printer.text("\n\n")

    printer.set(align='center', width=1, height=1)
    printer.text("Gracias por su visita.")
    printer.text("\n\n")

    printer.set(align='center', width=1, height=1)
    printer.text(fecha_actual+"  "+hora_actual_str)
    printer.text("\n")

    

    printer.cut()
    printer.close()

    return True