import os
from django.conf import settings
from django.templatetags.static import static
from datetime import date
from datetime import datetime
from escpos.printer import Network
from PIL import Image, ImageDraw, ImageFont

def imprimir(codigo, departamento):
    fecha_actual = date.today().strftime('%Y-%m-%d')
    hora_actual = datetime.now()
    hora_actual_str = hora_actual.strftime('%H:%M:%S')
    printer_ip = '192.168.8.35'
    
    img_path = crear_img(codigo, departamento, fecha_actual, hora_actual_str)
    img_path2 = Image.open("tickets/static/img/logo3.png")

    printer = Network(printer_ip)
    printer.open()

    nueva_ancho = 110
    nueva_alto = 170 
    imagen = img_path2.resize((nueva_ancho, nueva_alto))

    printer.set(align='center')
    printer.image(imagen, impl="bitImageColumn")
    printer.text('\n')

    printer.set(align='center')
    printer.image(img_path, impl="bitImageColumn")
    
    printer.cut()
    printer.close()

    return True


def crear_img (codigo, departamento, fecha, hora):

    width = 600
    height = 450
    color_fondo = (255, 255, 255)
    img = Image.new('RGB', (width, height), color_fondo)

    dibujo = ImageDraw.Draw(img)

    fuente_b = ImageFont.truetype("tickets/static/fonts/Abrade/Abrade-SemiBold.ttf", 60)
    if len(codigo)>7:
        fuente_c = ImageFont.truetype("tickets/static/fonts/Abrade/Abrade-Bold.ttf", 100)
    else:
        fuente_c = ImageFont.truetype("tickets/static/fonts/Abrade/Abrade-Bold.ttf", 120)
    fuente_t = ImageFont.truetype("tickets/static/fonts/Abrade/Abrade-Medium.ttf", 30)

    texto1_width, texto1_height = dibujo.textsize("Texto 1", font=fuente_b)
    texto2_width, texto2_height = dibujo.textsize("Texto 2", font=fuente_c)
    texto3_width, texto3_height = dibujo.textsize("Texto 3", font=fuente_t)
    texto4_width, texto4_height = dibujo.textsize("Texto 4", font=fuente_t)
    texto5_width, texto5_height = dibujo.textsize("Texto 5", font=fuente_t)

    pos_texto1 = (width // 2, height // 7)
    pos_texto2 = (width // 2, pos_texto1[1] + texto1_height + 100)
    pos_texto3 = (width // 2, pos_texto2[1] + texto2_height + 10)
    pos_textoE = (width // 2, pos_texto2[1] + texto1_height)
    pos_texto4 = (width // 2, pos_texto3[1] + texto3_height + 30)
    pos_texto5 = (width // 2, pos_texto4[1] + texto4_height + 30)

    dibujo.text(pos_texto1, "BIENVENIDO", fill=(0, 0, 0), font=fuente_b, anchor="ms")
    dibujo.text(pos_texto2, codigo, fill=(0, 0, 0), font=fuente_c, anchor="ms")
    if len(departamento)>35:
        departamento = departamento.split("-")
        dibujo.text(pos_texto3, departamento[1], fill=(0, 0, 0), font=fuente_t, anchor="ms")
        dibujo.text(pos_textoE, departamento[0]+" -", fill=(0, 0, 0), font=fuente_t, anchor="ms")
    else:
        dibujo.text(pos_texto3, departamento, fill=(0, 0, 0), font=fuente_t, anchor="ms")
    dibujo.text(pos_texto4, "Gracias por tu visita.", fill=(0, 0, 0), font=fuente_t, anchor="ms")
    dibujo.text(pos_texto5, fecha+"  "+hora, fill=(0, 0, 0), font=fuente_t, anchor="ms")

    return img