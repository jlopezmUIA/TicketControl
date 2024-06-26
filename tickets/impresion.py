import json
import requests
from django.conf import settings
from django.templatetags.static import static
from datetime import date
from datetime import datetime
from escpos.printer import Network
from PIL import Image, ImageDraw, ImageFont
from django.templatetags.static import static

def imprimir(codigo, departamento):
    # session = requests.Session()
    # url = 'http://186.96.95.26:8057/create_ticket'
    # headers = {
    #     'Content-Type': 'application/json'
    # }
    # data = {
    #     "codigo": codigo,
    #     "departamento": departamento
    # }
    # response = session.post(url, data=json.dumps(data), headers=headers)

    # if response.status_code == 200:
    #     return True
    # else:
    #     return False
    
    return True

def crear_img (codigo, departamento, fecha, hora):

    width = 600
    height = 450
    color_fondo = (255, 255, 255)
    img = Image.new('RGB', (width, height), color_fondo)

    dibujo = ImageDraw.Draw(img)

    fuente_b = ImageFont.truetype('tickets/static/fonts/Abrade/Abrade-SemiBold.ttf', 60)
    if len(codigo)>7:
        fuente_c = ImageFont.truetype('tickets/static/fonts/Abrade/Abrade-Bold.ttf', 90)
    else:
        fuente_c = ImageFont.truetype('tickets/static/fonts/Abrade/Abrade-Bold.ttf', 120)
    fuente_t = ImageFont.truetype('tickets/static/fonts/Abrade/Abrade-Medium.ttf', 30)

    texto1_width, texto1_height = dibujo.textsize("Texto 1", font=fuente_b)
    texto2_width, texto2_height = dibujo.textsize("Texto 2", font=fuente_c)
    texto3_width, texto3_height = dibujo.textsize("Texto 3", font=fuente_t)
    texto4_width, texto4_height = dibujo.textsize("Texto 4", font=fuente_t)
    texto5_width, texto5_height = dibujo.textsize("Texto 5", font=fuente_t)

    pos_texto1 = (width // 2, height // 7)
    pos_texto2 = (width // 2, pos_texto1[1] + texto1_height + 90)
    pos_texto3 = (width // 2, pos_texto2[1] + texto2_height + 10)
    if len(departamento)>35:
        pos_textoE = (width // 2, pos_texto2[1] + texto2_height + 40)
        pos_texto4 = (width // 2, pos_texto3[1] + texto3_height + 55)
        pos_texto5 = (width // 2, pos_texto4[1] + texto4_height + 45)
    else:
        pos_texto4 = (width // 2, pos_texto3[1] + texto3_height + 30)
        pos_texto5 = (width // 2, pos_texto4[1] + texto4_height + 30)

    dibujo.text(pos_texto1, "BIENVENIDO", fill=(0, 0, 0), font=fuente_b, anchor="ms")
    dibujo.text(pos_texto2, codigo, fill=(0, 0, 0), font=fuente_c, anchor="ms")
    if len(departamento)>35:
        departamento = departamento.split("-")
        dibujo.text(pos_texto3, departamento[0]+" -", fill=(0, 0, 0), font=fuente_t, anchor="ms")
        dibujo.text(pos_textoE, departamento[1], fill=(0, 0, 0), font=fuente_t, anchor="ms")
    else:
        dibujo.text(pos_texto3, departamento, fill=(0, 0, 0), font=fuente_t, anchor="ms")
    dibujo.text(pos_texto4, "Gracias por tu visita.", fill=(0, 0, 0), font=fuente_t, anchor="ms")
    dibujo.text(pos_texto5, fecha+"  "+hora, fill=(0, 0, 0), font=fuente_t, anchor="ms")

    return img