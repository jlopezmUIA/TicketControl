import base64
import io
import json
import os
from django.contrib.auth.decorators import login_required
from google.cloud import texttospeech
from tempfile import TemporaryFile
from winsound import PlaySound
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from django.contrib.auth.models import User
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.views import LoginView, LogoutView
import requests
from django.views.generic.edit import FormView
from tickets.models import admisiones, agentes, atencion, cajas, casosAgente, cursoslibres, estadosAgente, registro, ticketControl, tiemposAgente, visualizador
from datetime import datetime
from datetime import date
from django.contrib.auth.forms import UserCreationForm
import threading
from queue import Queue
import pyttsx3
from .impresion import imprimir
from pydub.playback import play
from django.contrib.auth.forms import AuthenticationForm
from tickets.savedata import delete_agente, eliminar_atencion, marcar_cajas, marcar_cursoslibres, marcar_registro, marcar_admision, obtener_agenteAtencion, obtener_caso, obtener_cola, obtener_departamento, obtener_primero_dato_admisiones, obtener_primero_dato_cajas, obtener_primero_dato_cursoslibres, obtener_primero_dato_registro, obtener_ultimo_dato_admisiones, obtener_ultimo_dato_cajas, obtener_ultimo_dato_cursoslibres, obtener_ultimo_dato_registro, obtener_ventanilla, save_admisiones, save_agente, save_atencion, save_cajas, save_casos_agente, save_configuration, save_cursoslibres, save_estados_agente, save_registro, save_ticketcontrol, save_tiempos_agente, update_casos_agente, update_cola, update_configuration, update_estado, update_estados_agente, update_ticketcontrol, update_tiempos_agente

def home(request):
    if 'fechaactual' in request.session:
        estado = request.GET.get("estado")
        # Convertir la fecha a una cadena de texto en formato YYYY-MM-DD
        fecha_actual = date.today().strftime('%Y-%m-%d')
        hora_actual = datetime.now()
        hora_actual_str = hora_actual.strftime('%H:%M:%S')
        request.session['fechaactual'] = fecha_actual
        save = update_estados_agente(
            request, request.session.get('estadoactual'), hora_actual_str)
        if save:
            data_estados_agente = {
                # Objeto de la instancia relacionada del modelo agentes
                'agente': request.session.get('id_agente'),
                'estado': estado,
                'fecha': str(fecha_actual),
                'tiempoInicio': str(hora_actual_str),
                'tiempoFinal': None  # Fecha en formato YYYY-MM-DD
            }
        save = save_estados_agente(request, data_estados_agente)
        if save is not None:
            request.session['estadoactual'] = save.id_estado

    request.session.flush() 

    return render(request, 'home.html')

class Logueo(FormView):
    template_name = 'administracion/login.html'
    form_class = AuthenticationForm
    redirect_authenticated_user = True

    def form_valid(self, form):
        logout(self.request)
        username = form.cleaned_data.get('username')
        password = form.cleaned_data.get('password')

        user = authenticate(username=username, password=password)

        if user is not None:
            login(self.request, user)
            return redirect('admin_side')  # Reemplaza 'admin_side' con la vista a la que deseas redirigir luego del inicio de sesión exitoso
        else:
            # El usuario no existe o las credenciales son inválidas
            return render(self.request, self.template_name, {'form': form, 'error': 'Usuario o contraseña incorrectos'})

    def get(self, *args, **kwargs):
        if self.request.user.is_authenticated:
            logout(self.request)
            return redirect('login_admin')  # Reemplaza 'login_admin' con la URL a la vista de inicio de sesión
        return super(Logueo, self).get(*args, **kwargs)

class RegistroAdmin(FormView):
    template_name = 'administracion/registroadmin.html'
    form_class = UserCreationForm
    redirect_authenticated_user = True

    def form_valid(self, form):
        form.save()
        return redirect('admin_side')

    def get(self, *args, **kwargs):
        if self.request.user.is_authenticated:
            logout(self.request)
            return redirect('registro_admin')
        return super(RegistroAdmin, self).get(*args, **kwargs)

@login_required
def adminside(request):
    fecha_actual = date.today().strftime('%Y-%m-%d')
    records = atencion.objects.all()
    casos = casosAgente.objects.filter(fecha=fecha_actual)
    admin = admisiones.objects.all()
    regis = registro.objects.all()
    caja = cajas.objects.all()
    cursos = cursoslibres.objects.all()
    return render(request, 'administracion/admin.html', {'records': records, 'casos': casos, 'admin': admin, 'registro': regis, 'cajas': caja, 'cursos':cursos})

@login_required
def colasatencion(request):
    records = atencion.objects.all()
    return render(request, 'administracion/colasatencion.html', {'records': records})

@login_required
def configuracion(request):
    registro = visualizador.objects.first()  # Obtener el primer registro del modelo visualizador

    if registro:
        nombre_imagen1 = registro.imagen1_nombre if registro.imagen1 else 'Sin Imagen 1'
        nombre_imagen2 = registro.imagen2_nombre if registro.imagen2 else 'Sin Imagen 2'
        nombre_imagen3 = registro.imagen3_nombre if registro.imagen3 else 'Sin Imagen 3'
        nombre_imagen4 = registro.imagen4_nombre if registro.imagen4 else 'Sin Imagen 4'
        link = registro.link if registro.link else 'Sin Link'
        tipo = 'playlist' if registro.tipo_visor  else 'imgs'
        text = registro.text if registro.text else 'Sin Texto'

    records = {
        'imagen1':nombre_imagen1,
        'imagen2':nombre_imagen2,
        'imagen3':nombre_imagen3,
        'imagen4':nombre_imagen4,
        'link': link,
        'tipo': tipo,
        'text': text
    }
        
    return render(request, 'administracion/configuracion.html', {'records': records})

def cambiar_imagen(request):
    imgnueva = request.FILES.get('imagen1')
    if imgnueva is not None:
        img_data = imgnueva.read()
        img_bytes = bytearray(img_data)
        campo = request.POST.get('imagen_select')
        nombre_archivo = imgnueva.name  # Obtener el nombre del archivo
        save = update_configuration(request, 1, campo, img_bytes, nombre_archivo)
        if save:
            return redirect(request.META.get('HTTP_REFERER'))
    else:
        return redirect(request.META.get('HTTP_REFERER'))

def cambiar_visual(request):
    estado = request.GET.get("estado")
    if estado == "playlist":
        tipo = True
    elif estado == "imgs":
        tipo = False
    else:
        tipo = False

    save = save_configuration(request, 1,'tipo_visor', tipo)

    dic = {
        'success': True
    }
    return JsonResponse(dic, safe=False)

def cambiar_link_text(request):
    link = request.POST.get("link")
    text = request.POST.get("text")

    link = link.split('=')

    linkformat = "http://www.youtube.com/embed?listType=playlist&list=" + link[2] + "&mute=1&autoplay=1"

    save = save_configuration(request, 1,'link', linkformat)
    save = save_configuration(request, 1,'text', text)

    return redirect(request.META.get('HTTP_REFERER'))

@login_required
def estadosagente(request):
    records = estadosAgente.objects.all()
    return render(request, 'administracion/estadosagente.html', {'records': records})

@login_required
def casosagente(request):
    records = casosAgente.objects.all()
    return render(request, 'administracion/casosagente.html', {'records': records})

@login_required
def ticketsagente(request):
    admin = admisiones.objects.all()
    regis = registro.objects.all()
    caja = cajas.objects.all()
    cursos = cursoslibres.objects.all()
    records = ticketControl.objects.all()
    return render(request, 'administracion/ticketsagente.html', {'records':records, 'admin': admin, 'registro': regis, 'cajas': caja, 'cursos':cursos})

@login_required
def datosagente(request):
    agente = agentes.objects.all()
    records = tiemposAgente.objects.all()
    return render(request, 'administracion/datosagente.html', {'records':records, 'agentes': agente})

@login_required
def nuevoagente(request):
    nombreagente = request.POST.get('name')
    departamento = request.POST.get('departamento')
    data_agente = {
        'departamento': departamento,
        'nombreAgente': nombreagente
    }
    save = save_agente(request, data_agente)
    return redirect(request.META.get('HTTP_REFERER'))

def eliminaragente(request):
    id = request.POST.get('id_agente')
    save = delete_agente(request, id)
    return redirect(request.META.get('HTTP_REFERER'))

def registroAgente(request):
    return render(request, 'agentes/registro_agente.html')

def obtener_agentes(request):
    departamento = request.GET.get("departamento")
    agentes_dict = {}
    agentes_queryset = agentes.objects.filter(departamento=departamento)

    for agente in agentes_queryset:
        agentes_dict[agente.id_agente] = agente.nombreAgente

    return JsonResponse(agentes_dict, safe=False)

def inicio_atencion(request):
    if request.method == 'POST':
        agente = request.POST.get('agente_select')
        numeroVentanilla = request.POST.get('ventanilla')
        departamento = request.POST.get('departamento')
        if 'id_agente' in request.session:
            pass
        else:
            request.session['id_agente'] = agente

        fecha_actual = date.today().strftime('%Y-%m-%d')

        data_atencion = {
            'agente': agente,
            'numeroVentanilla': numeroVentanilla,
            'colaAtencion': departamento,
            'estadoAtencion': 'Activo'
        }
        delete = eliminar_atencion(agente)
        save = save_atencion(request, data_atencion)

        if save:
            if 'idcasos' in request.session:
                return redirect('atencion_agentes')
            else:
                casoid = obtener_caso(agente)
                if casoid != False:
                    request.session['idcasos'] = casoid
                else:
                    data_caso = {
                        'agente': agente,
                        'fecha': fecha_actual
                    }
                    save_caso = save_casos_agente(request, data_caso)
                    request.session['idcasos'] = save_caso.id_casoagente
                return redirect('atencion_agentes')

def atencion_agentes(request):
    agente_id = request.session.get('id_agente')
    cola = obtener_cola(agente_id)
    return render(request, 'agentes/inicio_atencion.html', {'agente':agente_id, 'cola': cola})

def ticket_maker(request):
    return render(request, 'ticket/ticketmaker.html')

def crear_ticket_admision(request):
    dato = obtener_ultimo_dato_admisiones()
    codigo = dato.split('-')
    numero_siguiente = str(int(codigo[1]) + 1).zfill(4)
    fecha_actual = date.today().strftime('%Y-%m-%d')

    data_admisiones = {
        'codigo': 'AD-'+numero_siguiente,
        'departamento': 'Admisiones',
        'fecha': fecha_actual,
        'atentido': False
    }
    save_admisiones(request, data_admisiones)
    codigo = 'AD-'+numero_siguiente

    departamento = 'AD, ADM = Admisiones'
    imprimir(codigo, departamento)
    dic = {
        'success': True
    }

    return JsonResponse(dic, safe=False)

def crear_ticket_cajas(request):
    dato = obtener_ultimo_dato_cajas()
    codigo = dato.split('-')
    numero_siguiente = str(int(codigo[1]) + 1).zfill(4)
    fecha_actual = date.today().strftime('%Y-%m-%d')

    data_admisiones = {
        'codigo': 'CJ-'+numero_siguiente,
        'departamento': 'Cajas',
        'fecha': fecha_actual,
        'atentido': False
    }
    save_cajas(request, data_admisiones)
    codigo = 'CJ-'+numero_siguiente

    departamento = 'CJ, CJA = Cajas'
    imprimir(codigo, departamento)
    dic = {
        'success': True
    }

    return JsonResponse(dic, safe=False)

def crear_ticket_cursolibre(request):
    dato = obtener_ultimo_dato_cursoslibres()
    codigo = dato.split('-')
    numero_siguiente = str(int(codigo[1]) + 1).zfill(4)
    fecha_actual = date.today().strftime('%Y-%m-%d')

    data_admisiones = {
        'codigo': 'CL-'+numero_siguiente,
        'departamento': 'Curso Libres',
        'fecha': fecha_actual,
        'atentido': False
    }
    save_cursoslibres(request, data_admisiones)
    codigo = 'CL-'+numero_siguiente

    departamento = 'CL, C.L. = Cursos Libres'
    imprimir(codigo, departamento)
    dic = {
        'success': True
    }

    return JsonResponse(dic, safe=False)

def crear_ticket_registro(request):
    dato = obtener_ultimo_dato_registro()
    codigo = dato.split('-')
    numero_siguiente = str(int(codigo[1]) + 1).zfill(4)
    fecha_actual = date.today().strftime('%Y-%m-%d')

    data_admisiones = {
        'codigo': 'RG-'+numero_siguiente,
        'departamento': 'Registro',
        'fecha': fecha_actual,
        'atentido': False
    }
    save_registro(request, data_admisiones)
    codigo = 'RG-'+numero_siguiente

    departamento = 'RG, REG = Registro'
    imprimir(codigo, departamento)
    dic = {
        'success': True
    }

    return JsonResponse(dic, safe=False)

def crear_ticket_registro_tesis(request):
    dato = obtener_ultimo_dato_registro()
    codigo = dato.split('-')
    numero_siguiente = str(int(codigo[1]) + 1).zfill(4)
    fecha_actual = date.today().strftime('%Y-%m-%d')

    data_admisiones = {
        'codigo': 'RGT-'+numero_siguiente,
        'departamento': 'Registro/Tesis',
        'fecha': fecha_actual,
        'atentido': False
    }
    save_registro(request, data_admisiones)
    codigo = 'RGT-'+numero_siguiente

    departamento = 'RGT, REG = Registro - Tesis'
    imprimir(codigo, departamento)
    dic = {
        'success': True
    }

    return JsonResponse(dic, safe=False)

def crear_ticket_registro_convalidacion(request):
    dato = obtener_ultimo_dato_registro()
    codigo = dato.split('-')
    numero_siguiente = str(int(codigo[1]) + 1).zfill(4)
    fecha_actual = date.today().strftime('%Y-%m-%d')

    data_admisiones = {
        'codigo': 'RGC-'+numero_siguiente,
        'departamento': 'Registro/Convalidacion',
        'fecha': fecha_actual,
        'atentido': False
    }
    save_registro(request, data_admisiones)
    codigo = 'RGC-'+numero_siguiente

    departamento = 'RGC, REG = Registro - Convalidacion'
    imprimir(codigo, departamento)
    dic = {
        'success': True
    }

    return JsonResponse(dic, safe=False)

def crear_ticket_registro_retiros(request):
    dato = obtener_ultimo_dato_registro()
    codigo = dato.split('-')
    numero_siguiente = str(int(codigo[1]) + 1).zfill(4)
    fecha_actual = date.today().strftime('%Y-%m-%d')

    data_admisiones = {
        'codigo': 'RGR-'+numero_siguiente,
        'departamento': 'Registro/Retiros',
        'fecha': fecha_actual,
        'atentido': False
    }
    save_registro(request, data_admisiones)
    codigo = 'RGR-'+numero_siguiente

    departamento = 'RGR, REG = Registro - Retiros/Congelacion'
    imprimir(codigo, departamento)
    dic = {
        'success': True
    }

    return JsonResponse(dic, safe=False)

def crear_ticket_registro_suficiencia(request):
    dato = obtener_ultimo_dato_registro()
    codigo = dato.split('-')
    numero_siguiente = str(int(codigo[1]) + 1).zfill(4)
    fecha_actual = date.today().strftime('%Y-%m-%d')

    data_admisiones = {
        'codigo': 'RGS-'+numero_siguiente,
        'departamento': 'Registro/Suficiencia',
        'fecha': fecha_actual,
        'atentido': False
    }
    save_registro(request, data_admisiones)
    codigo = 'RGS-'+numero_siguiente

    departamento = 'RGS, REG = Registro - Suficiencia'
    imprimir(codigo, departamento)
    dic = {
        'success': True
    }

    return JsonResponse(dic, safe=False)

def crear_ticket_registro_graduacion(request):
    dato = obtener_ultimo_dato_registro()
    codigo = dato.split('-')
    numero_siguiente = str(int(codigo[1]) + 1).zfill(4)
    fecha_actual = date.today().strftime('%Y-%m-%d')

    data_admisiones = {
        'codigo': 'RGG-'+numero_siguiente,
        'departamento': 'Registro/Graduaciones',
        'fecha': fecha_actual,
        'atentido': False
    }
    save_registro(request, data_admisiones)
    codigo = 'RGG-'+numero_siguiente

    departamento = 'RGG, REG = Registro - Graduaciones'
    imprimir(codigo, departamento)
    dic = {
        'success': True
    }

    return JsonResponse(dic, safe=False)

def estados_reporte(request):
    estado = request.GET.get("estado")
    # Convertir la fecha a una cadena de texto en formato YYYY-MM-DD
    fecha_actual = date.today().strftime('%Y-%m-%d')
    hora_actual = datetime.now()
    hora_actual_str = hora_actual.strftime('%H:%M:%S')

    if 'fechaactual' in request.session:

        if estado == 'Inactivo'or estado == 'Desconectado':
            if 'idtiempo' in request.session:
                save = update_tiempos_agente(request, request.session.get('idtiempo'), str(hora_actual_str))
                del request.session['idtiempo']

                if 'idcasos' in request.session:
                    save = update_casos_agente(request, request.session.get('idcasos'), "caso")

        request.session['fechaactual'] = fecha_actual
        save = update_estados_agente(
            request, request.session.get('estadoactual'), hora_actual_str)
        if save:
            data_estados_agente = {
                # Objeto de la instancia relacionada del modelo agentes
                'agente': request.session.get('id_agente'),
                'estado': estado,
                'fecha': str(fecha_actual),
                # Fecha en formato YYYY-MM-DD
                'tiempoInicio': str(hora_actual_str),
                'tiempoFinal': None  # Fecha en formato YYYY-MM-DD
            }
        save = save_estados_agente(request, data_estados_agente)
        if save is not None:
            request.session['estadoactual'] = save.id_estado
    else:
        request.session['fechaactual'] = fecha_actual
        data_estados_agente = {
            # Objeto de la instancia relacionada del modelo agentes
            'agente': request.session.get('id_agente'),
            'estado': estado,
            'fecha': str(fecha_actual),
            # Fecha en formato YYYY-MM-DD
            'tiempoInicio': str(hora_actual_str),
            'tiempoFinal': None  # Fecha en formato YYYY-MM-DD
        }
        save = save_estados_agente(request, data_estados_agente)
        if save is not None:
            request.session['estadoactual'] = save.id_estado

    update_estado(request, request.session.get('id_agente'), estado)

    data = ['success']
    data_completa = json.dumps(data)
    return JsonResponse(data_completa, safe=False)

def numero_agente(request):
    cola = obtener_cola(request.session.get('id_agente'))
    ventanilla = obtener_ventanilla(request.session.get('id_agente'))
    departamento = obtener_departamento(request.session.get('id_agente'))
    caso = False

    fecha_actual = date.today().strftime('%Y-%m-%d')
    hora_actual = datetime.now()
    hora_actual_str = hora_actual.strftime('%H:%M:%S')

    if cola == "Admisiones":
        numero = obtener_primero_dato_admisiones()
        if "0000" in numero:
            data = {'codigo': 'N/C'}
        else:
            data = {'codigo': numero}
            marcar_admision(numero)
            caso = True
    elif "Registro" in cola:
        numero = obtener_primero_dato_registro(cola)
        if "0000" in numero:
            data = {'codigo': 'N/C'}
        else:
            data = {'codigo': numero}
            marcar_registro(numero)
            caso = True
    elif cola == "Cajas":
        numero = obtener_primero_dato_cajas()
        if "0000" in numero:
            data = {'codigo': 'N/C'}
        else:
            data = {'codigo': numero}
            marcar_cajas(numero)
            caso = True
    elif cola == "Cursos Libres":
        numero = obtener_primero_dato_cursoslibres()
        if "0000" in numero:
            data = {'codigo': 'N/C'}
        else:
            data = {'codigo': numero}
            marcar_cursoslibres(numero)
            caso = True

    if caso:
        data_caso = {
            'agente': request.session.get('id_agente'),
            'codigoCaso': numero,
            'fecha': str(fecha_actual),
            'tiempoInicio': str(hora_actual_str),
            'tiempoFinal': None
        }

        data_ticket = {
            'codigoCaso': numero,
            'numeroVentanilla': ventanilla,
            'departamento': departamento,
            'fecha': str(fecha_actual)
        }

        if 'idtiempo' in request.session:
            save = update_tiempos_agente(request, request.session.get('idtiempo'), str(hora_actual_str))
            del request.session['idtiempo']
            idtiempo = save_tiempos_agente(request, data_caso)
            request.session['idtiempo'] = idtiempo.id_tiemposagente
        else:
            idtiempo = save_tiempos_agente(request, data_caso)
            request.session['idtiempo'] = idtiempo.id_tiemposagente

        request.session['cliente'] = numero

        save_ticket = save_ticketcontrol(request, data_ticket)

        if 'idcasos' in request.session:
            save = update_casos_agente(
                request, request.session.get('idcasos'), "caso")
    else:
        if 'idtiempo' in request.session:
            save = update_tiempos_agente(
                request, request.session.get('idtiempo'), str(hora_actual_str))
            del request.session['idtiempo']

    return JsonResponse(data, safe=False)

def transferencia(request):
    ventanilla = obtener_ventanilla(request.session.get('id_agente'))
    departamento = obtener_departamento(request.session.get('id_agente'))
    departamento = request.GET.get("departamento")
    cliente = request.session.get('cliente')
    if departamento == 'Admisiones':
        data_admisiones = {
            'codigo': cliente,
            'departamento': 'Admisiones'
        }
        save_admisiones(request, data_admisiones)

    elif departamento == 'Registro':
        data_admisiones = {
            'codigo': cliente,
            'departamento': 'Registro'
        }
        save_registro(request, data_admisiones)

    elif departamento == 'Registro/Tesis':
        data_admisiones = {
            'codigo': cliente,
            'departamento': 'Registro/Tesis'
        }
        save_registro(request, data_admisiones)

    elif departamento == 'Registro/Convalidacion':
        data_admisiones = {
            'codigo': cliente,
            'departamento': 'Registro/Convalidacion'
        }
        save_registro(request, data_admisiones)

    elif departamento == 'Registro/Suficiencia':
        data_admisiones = {
            'codigo': cliente,
            'departamento': 'Registro/Suficiencia'
        }
        save_registro(request, data_admisiones)

    elif departamento == 'Registro/Retiros':
        data_admisiones = {
            'codigo': cliente,
            'departamento': 'Registro/Retiros'
        }
        save_registro(request, data_admisiones)

    elif departamento == 'Registro/Graduaciones':
        data_admisiones = {
            'codigo': cliente,
            'departamento': 'Registro/Graduaciones'
        }
        save_registro(request, data_admisiones)

    elif departamento == 'Cajas':
        data_admisiones = {
            'codigo': cliente,
            'departamento': 'Cajas'
        }
        save_cajas(request, data_admisiones)

    elif departamento == 'Cursos Libres':
        data_admisiones = {
            'codigo': cliente,
            'departamento': 'Curso Libres'
        }
        save_cursoslibres(request, data_admisiones)

    if departamento == "Admisiones":
            departamento = 'Adm'
    elif departamento == "Registro":
            departamento = 'Reg'
    elif departamento == "Cajas":
            departamento = 'Cja'
    elif departamento == "Cursos Libres":
            departamento = 'C.L.'

    data_ticket = {
        'codigoCaso': cliente,
        'numeroVentanilla': ventanilla,
        'departamento': departamento
    }

    save = update_casos_agente(request, request.session.get('idcasos'), "transferencia")

    data = ['success']
    data_completa = json.dumps(data)
    return JsonResponse(data_completa, safe=False)

previous_thread = None
def ticketcontrol(request):
    if 'cantrecords' in request.session:
        global previous_thread
        recordscant = ticketControl.objects.count()
        cantrecord = request.session.get('cantrecords')

        if int(recordscant) > cantrecord:
            cantregistro = request.session.get('reproduccion')
            # Cantidad de veces que se ha sobrepasado el valor
            cantidad_sobrepasada = recordscant - cantrecord
            request.session['cantrecords'] = recordscant
            
            for _ in range(cantidad_sobrepasada):
                registro = ticketControl.objects.all()[cantregistro]
                if registro.departamento == 'Adm':
                    departamento = 'admisiones'
                elif registro.departamento == 'Reg':
                    departamento = 'registro'
                elif registro.departamento == 'Cja':
                    departamento = 'cajas'
                elif registro.departamento == 'C.L.':
                    departamento = 'cursos libres'
                texto = registro.codigoCaso + ", dirigirse a la Ventanilla numero," + registro.numeroVentanilla+", del departamento de "+departamento
                # Crear hilo y esperar a que el hilo anterior termine
                if previous_thread:
                    previous_thread.join()
                
                t = threading.Thread(target=reproducir_texto, args=(texto,))
                t.start()
                cantregistro += 1
                request.session['reproduccion'] = cantregistro

                # Actualizar el hilo anterior
                previous_thread = t
        else:
            pass
    else:
        recordscant = ticketControl.objects.count()
        request.session['cantrecords'] = recordscant
        request.session['reproduccion'] = recordscant
    registro = visualizador.objects.first() 
    records = ticketControl.objects.all().order_by('-id_ticketcontrol')[:5]
    noticia = registro.text
    tipovisual = registro.tipo_visor

    if tipovisual != True:
        imgs = [base64.b64encode(bytes(registro.imagen1)).decode('utf-8'),
                base64.b64encode(bytes(registro.imagen2)).decode('utf-8'),
                base64.b64encode(bytes(registro.imagen3)).decode('utf-8'),
                base64.b64encode(bytes(registro.imagen4)).decode('utf-8')]
        return render(request, 'visualizador/ticket_control.html', {'records': records, 'noticia': noticia, 'tipo': tipovisual, 'image_response': imgs})
    else:
        link = registro.link
        return render(request, 'visualizador/ticket_control.html', {'records': records, 'noticia': noticia, 'tipo': tipovisual, 'link': link})

def reproducir_texto(texto):
    engine = pyttsx3.init()
    velocidad_actual = engine.getProperty('rate')
    engine.setProperty('rate', velocidad_actual - 60)
    engine.say(texto)
    engine.runAndWait()

def cambiar_cola(request):
    cola = request.GET.get("cola")
    agente = request.GET.get("agente")
    
    save = update_cola(request, agente, cola)

    if save:
        dic = {
            'success': True
        }

    return JsonResponse(dic, safe=False)