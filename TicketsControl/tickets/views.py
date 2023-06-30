import base64
import json
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render
from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.views.generic.edit import FormView
from tickets.models import admisiones, agentes, metricas, atencion, cajas, casosAgente, cursoslibres, estadosAgente, registro, ticketControl, tiemposAgente, visualizador
from datetime import datetime
from datetime import date
from django.contrib.auth.forms import UserCreationForm
import threading
from .impresion import imprimir
from django.contrib.auth.forms import AuthenticationForm
from tickets.savedata import delete_agente, eliminar_atencion, marcar_cajas, marcar_cursoslibres, marcar_registro, marcar_admision, obtener_caso, obtener_cola, obtener_departamento, obtener_primero_dato_admisiones, obtener_primero_dato_cajas, obtener_primero_dato_cursoslibres, obtener_primero_dato_registro, obtener_ultimo_dato_admisiones, obtener_ultimo_dato_cajas, obtener_ultimo_dato_cursoslibres, obtener_ultimo_dato_registro, obtener_ventanilla, save_admisiones, save_agente, save_atencion, save_cajas, save_casos_agente, save_configuration, save_cursoslibres, save_estados_agente, save_metricas, save_registro, save_ticketcontrol, save_tiempos_agente, update_casos_agente, update_cola, update_configuration, update_estado, update_estados_agente, update_tiempos_agente

def home(request):
    request.session.flush() 
    request.session['estadoR'] = False
    request.session['listaR'] = []
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
        return redirect('login')

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
    visual = visualizador.objects.first()
    if visual.link != link:
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
    encuestas = metricas.objects.all()
    return render(request, 'administracion/datosagente.html', {'records':records, 'agentes': agente, 'encuestas': encuestas})

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
                
                if departamento == 'Registro':
                    return redirect('atencion_agentes_registro')
                else:
                    return redirect('atencion_agentes')

def atencion_agentes(request):
    agente_id = request.session.get('id_agente')
    cola = obtener_cola(agente_id)
    return render(request, 'agentes/inicio_atencion.html', {'agente':agente_id, 'cola': cola})

def atencion_agentes_registro(request):
    agente_id = request.session.get('id_agente')
    cola = obtener_cola(agente_id)
    return render(request, 'agentes/inicio_atencion_registro.html', {'agente':agente_id, 'cola': cola})

def ticket_maker(request):
    return render(request, 'ticket/ticketmaker.html')

def digital_ticket_maker(request):
    request.session.flush() 
    return render(request, 'ticket/digitalticketmaker.html')

def crear_ticket_admision(request):
    dato = obtener_ultimo_dato_admisiones()
    codigo = dato.split('-')
    numero_siguiente = str(int(codigo[1]) + 1).zfill(3)
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
    numero_siguiente = str(int(codigo[1]) + 1).zfill(3)
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
    numero_siguiente = str(int(codigo[1]) + 1).zfill(3)
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
    numero_siguiente = str(int(codigo[1]) + 1).zfill(3)
    fecha_actual = date.today().strftime('%Y-%m-%d')

    data_admisiones = {
        'codigo': 'RG-'+numero_siguiente,
        'departamento': 'Registro/Documentos',
        'fecha': fecha_actual,
        'atentido': False
    }
    save_registro(request, data_admisiones)
    codigo = 'RG-'+numero_siguiente

    departamento = 'RG, REG = Registro - Documentos'
    imprimir(codigo, departamento)
    dic = {
        'success': True
    }

    return JsonResponse(dic, safe=False)

def crear_ticket_registro_tesis(request):
    dato = obtener_ultimo_dato_registro()
    codigo = dato.split('-')
    numero_siguiente = str(int(codigo[1]) + 1).zfill(3)
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
    numero_siguiente = str(int(codigo[1]) + 1).zfill(3)
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
    numero_siguiente = str(int(codigo[1]) + 1).zfill(3)
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
    numero_siguiente = str(int(codigo[1]) + 1).zfill(3)
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
    numero_siguiente = str(int(codigo[1]) + 1).zfill(3)
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

def crear_ticket_registro_taller(request):
    dato = obtener_ultimo_dato_registro()
    codigo = dato.split('-')
    numero_siguiente = str(int(codigo[1]) + 1).zfill(3)
    fecha_actual = date.today().strftime('%Y-%m-%d')

    data_admisiones = {
        'codigo': 'RTT-'+numero_siguiente,
        'departamento': 'Registro/Taller',
        'fecha': fecha_actual,
        'atentido': False
    }
    save_registro(request, data_admisiones)
    codigo = 'RTT-'+numero_siguiente

    departamento = 'RTT, REG = Registro - Taller'
    imprimir(codigo, departamento)
    dic = {
        'success': True
    }

    return JsonResponse(dic, safe=False)

def crear_ticket_registro_apelacion(request):
    dato = obtener_ultimo_dato_registro()
    codigo = dato.split('-')
    numero_siguiente = str(int(codigo[1]) + 1).zfill(3)
    fecha_actual = date.today().strftime('%Y-%m-%d')

    data_admisiones = {
        'codigo': 'RGA-'+numero_siguiente,
        'departamento': 'Registro/Apelaciones',
        'fecha': fecha_actual,
        'atentido': False
    }
    save_registro(request, data_admisiones)
    codigo = 'RGA-'+numero_siguiente

    departamento = 'RGA, REG = Registro - Apelaciones'
    imprimir(codigo, departamento)
    dic = {
        'success': True
    }

    return JsonResponse(dic, safe=False)

def crear_ticket_registro_retencion(request):
    dato = obtener_ultimo_dato_registro()
    codigo = dato.split('-')
    numero_siguiente = str(int(codigo[1]) + 1).zfill(3)
    fecha_actual = date.today().strftime('%Y-%m-%d')

    data_admisiones = {
        'codigo': 'RRT-'+numero_siguiente,
        'departamento': 'Registro/Retenciones',
        'fecha': fecha_actual,
        'atentido': False
    }
    save_registro(request, data_admisiones)
    codigo = 'RRT-'+numero_siguiente

    departamento = 'RRT, REG = Registro - Retenciones'
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
        if "000" in numero.codigo:
            data = {'codigo': 'N/C'}
        else:
            data = {'codigo': numero.codigo}
            marcar_admision(numero.pk)
            caso = True
    elif cola == "Cajas":
        numero = obtener_primero_dato_cajas()
        if "000" in numero.codigo:
            data = {'codigo': 'N/C'}
        else:
            data = {'codigo': numero.codigo}
            marcar_cajas(numero.pk)
            caso = True
    elif cola == "Cursos Libres":
        numero = obtener_primero_dato_cursoslibres()
        if "000" in numero.codigo:
            data = {'codigo': 'N/C'}
        else:
            data = {'codigo': numero.codigo}
            marcar_cursoslibres(numero.pk)
            caso = True

    if caso:
        data_caso = {
            'agente': request.session.get('id_agente'),
            'codigoCaso': numero.codigo,
            'fecha': str(fecha_actual),
            'tiempoInicio': str(hora_actual_str),
            'tiempoFinal': None
        }
        data_ticket = {
            'codigoCaso': numero.codigo,
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

        request.session['cliente'] = numero.codigo

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

def numero_agente_registro(request):
    cola = obtener_cola(request.session.get('id_agente'))
    ventanilla = obtener_ventanilla(request.session.get('id_agente'))
    departamento = obtener_departamento(request.session.get('id_agente'))
    caso = False

    fecha_actual = date.today().strftime('%Y-%m-%d')
    hora_actual = datetime.now()
    hora_actual_str = hora_actual.strftime('%H:%M:%S')

    numero = obtener_primero_dato_registro(cola)
    if "000" in numero.codigo:
        data = {'codigo': 'N/C'}
    else:
        data = {'codigo': numero.codigo}
        marcar_registro(numero.pk)
        caso = True
    

    if caso:
        data_caso = {
            'agente': request.session.get('id_agente'),
            'codigoCaso': numero.codigo,
            'fecha': str(fecha_actual),
            'tiempoInicio': str(hora_actual_str),
            'tiempoFinal': None
        }
        data_ticket = {
            'codigoCaso': numero.codigo,
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

        request.session['cliente'] = numero.codigo

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

    elif departamento == 'Registro/Documentos':
        data_admisiones = {
            'codigo': cliente,
            'departamento': 'Registro/Documentos'
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

    elif departamento == 'Registro/Taller':
        data_admisiones = {
            'codigo': cliente,
            'departamento': 'Registro/Taller'
        }
        save_registro(request, data_admisiones)
    
    elif departamento == 'Registro/Apelaciones':
        data_admisiones = {
            'codigo': cliente,
            'departamento': 'Registro/Apelaciones'
        }
        save_registro(request, data_admisiones)

    elif departamento == 'Registro/Retenciones':
        data_admisiones = {
            'codigo': cliente,
            'departamento': 'Registro/Retenciones'
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
    fecha_actual = date.today().strftime('%Y-%m-%d')
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
                    departamento = 'Admisiones'
                elif registro.departamento == 'Reg':
                    departamento = 'Registro'
                elif registro.departamento == 'Cja':
                    departamento = 'Cajas'
                elif registro.departamento == 'C.L.':
                    departamento = 'Cursos Libres'
                codigo = str(registro.codigoCaso).split('-')
                numero = int(codigo[1].lstrip("0"))
                texto = codigo[0]+"-"+str(numero) + ", dirigirse a la Ventanilla número " + registro.numeroVentanilla+" del área de "+ departamento
                request.session['listaR'].append(texto)
                # Crear hilo y esperar a que el hilo anterior termine
                if previous_thread:
                    previous_thread.join()
                
                t = threading.Thread(target=reproductor, args=(request,))
                t.start()
                cantregistro += 1
                request.session['reproduccion'] = cantregistro
                request.session['estadoR'] = True
                # Actualizar el hilo anterior
                previous_thread = t
        else:
            reproductor(request)
            mi_lista = request.session.get('listaR', [])
            mi_lista.clear()
            request.session['listaR'] = mi_lista
    else:
        recordscant = ticketControl.objects.count()
        request.session['cantrecords'] = recordscant
        request.session['reproduccion'] = recordscant
    registro = visualizador.objects.first() 
    records = ticketControl.objects.filter(fecha=fecha_actual).order_by('-id_ticketcontrol')[:6]
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

def reproductor(request):
    dic = {}
    list = request.session.get('listaR', [])
    status = request.session.get('estadoR')
    if status:
        dic = {
            'estado': True,
            'list': list
        }
    else:
        dic = {
            'estado': False,
            'list': list
        }

    return JsonResponse(dic, safe=False)

def cambiar_cola(request):
    cola = request.GET.get("cola")
    agente = request.GET.get("agente")
    
    save = update_cola(request, agente, cola)

    if save:
        dic = {
            'success': True
        }

    return JsonResponse(dic, safe=False)

def registroEncuesta(request):
    return render(request, 'encuestas/registro_agente.html')

def inicio_encuesta(request):
    if request.method == 'POST':
        agente = request.POST.get('agente_select')
        numeroVentanilla = request.POST.get('ventanilla')
        departamento = request.POST.get('departamento')

        if departamento == 'Admisiones':
            departamento = 'Adm'
        elif departamento == 'Registro':
            departamento = 'Reg'
        elif departamento == 'Cursos Libres':
            departamento = 'C.L.'
        elif departamento == 'Cajas':
            departamento = 'Cja'

        request.session['agenteEncuesta'] = agente
        request.session['ventanillaEncuesta'] = numeroVentanilla
        request.session['departamentoEncuesta'] = departamento
        
    return redirect('ticket_control_encuesta')

def ticketcontrolEncuesta(request):
    ventanilla = request.session['ventanillaEncuesta']
    departamentoAgente = request.session['departamentoEncuesta']

    if 'last_ticket_id' in request.session:
        last_ticket_id = request.session.get('last_ticket_id')
        try:
            new_last_ticket = ticketControl.objects.latest('id_ticketcontrol')
        except:
            new_last_ticket = ticketControl(pk = 0)

        if new_last_ticket.pk == last_ticket_id:
            return render(request, 'encuestas/encuesta_visor.html', {'ventanilla': ventanilla, 'departamento': departamentoAgente, 'codigo': 'N/C'})
        elif new_last_ticket.pk > last_ticket_id:
            times = new_last_ticket.pk - last_ticket_id
            for vfc in range(times):
                last_ticket_id += 1
                ticket = ticketControl.objects.get(id_ticketcontrol=last_ticket_id)
                if ticket.numeroVentanilla == ventanilla and ticket.departamento == departamentoAgente:
                    request.session['last_ticket_id'] = new_last_ticket.pk
                    return render(request, 'encuestas/encuesta_visor.html', {'ventanilla': ventanilla, 'departamento': departamentoAgente, 'codigo': ticket.codigoCaso})
    else:
        try:
            last_ticket_id = ticketControl.objects.latest('id_ticketcontrol')
            request.session['last_ticket_id'] = last_ticket_id.pk
        except:
            last_ticket_id = 0
            request.session['last_ticket_id'] = last_ticket_id
        return render(request, 'encuestas/encuesta_visor.html', {'ventanilla': ventanilla, 'departamento': departamentoAgente, 'codigo': 'N/C'})

def metricas_guardado(request):
    estado = request.GET.get("estado")
    codigo = request.GET.get("codigo")
    agente = request.session.get('agenteEncuesta')
    
    fecha_actual = date.today().strftime('%Y-%m-%d')

    data = {
        'agente': agente,
        'codigoCaso': codigo,
        'estado': estado,
        'fecha': fecha_actual
    }

    save_metricas(request, data)
    
    dic = {
        'success': True
    }

    return JsonResponse(dic, safe=False)

#DIGITAL
def digital_crear_ticket_admision(request):
    if 'codigoDigital' in request.session:
        codigo = request.session.get('codigoDigital')
        fecha_actual = request.session.get('fechaDigital')
        hora_actual_str = request.session.get('horaDigital')
        departamento = request.session.get('departamentoDigital')
    else:
        dato = obtener_ultimo_dato_admisiones()
        codigo = dato.split('-') 
        numero_siguiente = str(int(codigo[1]) + 1).zfill(3)
        fecha_actual = date.today().strftime('%Y-%m-%d')
        hora_actual = datetime.now()
        hora_actual_str = hora_actual.strftime('%H:%M:%S')

        data_admisiones = {
            'codigo': 'AD-'+numero_siguiente,
            'departamento': 'Admisiones',
            'fecha': fecha_actual,
            'atentido': False
        }
        save_admisiones(request, data_admisiones)
        codigo = 'AD-'+numero_siguiente

        departamento = 'AD, ADM = Admisiones'
        request.session['codigoDigital'] = codigo
        request.session['fechaDigital'] = fecha_actual
        request.session['horaDigital'] = hora_actual_str
        request.session['departamentoDigital'] = departamento
    return render(request, 'ticket/ticketdigital.html', {'codigo': codigo, 'departamento': departamento, 'fecha':fecha_actual, 'hora': hora_actual_str})

def digital_crear_ticket_cajas(request):
    if 'codigoDigital' in request.session:
        codigo = request.session.get('codigoDigital')
        fecha_actual = request.session.get('fechaDigital')
        hora_actual_str = request.session.get('horaDigital')
        departamento = request.session.get('departamentoDigital')
    else:
        dato = obtener_ultimo_dato_cajas()
        codigo = dato.split('-')
        numero_siguiente = str(int(codigo[1]) + 1).zfill(3)
        fecha_actual = date.today().strftime('%Y-%m-%d')
        hora_actual = datetime.now()
        hora_actual_str = hora_actual.strftime('%H:%M:%S')

        data_admisiones = {
            'codigo': 'CJ-'+numero_siguiente,
            'departamento': 'Cajas',
            'fecha': fecha_actual,
            'atentido': False
        }
        save_cajas(request, data_admisiones)
        codigo = 'CJ-'+numero_siguiente

        departamento = 'CJ, CJA = Cajas'
        request.session['codigoDigital'] = codigo
        request.session['fechaDigital'] = fecha_actual
        request.session['horaDigital'] = hora_actual_str
        request.session['departamentoDigital'] = departamento
    return render(request, 'ticket/ticketdigital.html', {'codigo': codigo, 'departamento': departamento, 'fecha':fecha_actual, 'hora': hora_actual_str})

def digital_crear_ticket_cursolibre(request):
    if 'codigoDigital' in request.session:
        codigo = request.session.get('codigoDigital')
        fecha_actual = request.session.get('fechaDigital')
        hora_actual_str = request.session.get('horaDigital')
        departamento = request.session.get('departamentoDigital')
    else:
        dato = obtener_ultimo_dato_cursoslibres()
        codigo = dato.split('-')
        numero_siguiente = str(int(codigo[1]) + 1).zfill(3)
        fecha_actual = date.today().strftime('%Y-%m-%d')
        hora_actual = datetime.now()
        hora_actual_str = hora_actual.strftime('%H:%M:%S')

        data_admisiones = {
            'codigo': 'CL-'+numero_siguiente,
            'departamento': 'Curso Libres',
            'fecha': fecha_actual,
            'atentido': False
        }
        save_cursoslibres(request, data_admisiones)
        codigo = 'CL-'+numero_siguiente

        departamento = 'CL, C.L. = Cursos Libres'
        request.session['codigoDigital'] = codigo
        request.session['fechaDigital'] = fecha_actual
        request.session['horaDigital'] = hora_actual_str
        request.session['departamentoDigital'] = departamento
    return render(request, 'ticket/ticketdigital.html', {'codigo': codigo, 'departamento': departamento, 'fecha':fecha_actual, 'hora': hora_actual_str})

def digital_crear_ticket_registro(request):
    if 'codigoDigital' in request.session:
        codigo = request.session.get('codigoDigital')
        fecha_actual = request.session.get('fechaDigital')
        hora_actual_str = request.session.get('horaDigital')
        departamento = request.session.get('departamentoDigital')
    else:
        dato = obtener_ultimo_dato_registro()
        codigo = dato.split('-')
        numero_siguiente = str(int(codigo[1]) + 1).zfill(3)
        fecha_actual = date.today().strftime('%Y-%m-%d')
        hora_actual = datetime.now()
        hora_actual_str = hora_actual.strftime('%H:%M:%S')

        data_admisiones = {
            'codigo': 'RG-'+numero_siguiente,
            'departamento': 'Registro/Documentos',
            'fecha': fecha_actual,
            'atentido': False
        }
        save_registro(request, data_admisiones)
        codigo = 'RG-'+numero_siguiente

        departamento = 'RG, REG = Registro - Documentos'
        request.session['codigoDigital'] = codigo
        request.session['fechaDigital'] = fecha_actual
        request.session['horaDigital'] = hora_actual_str
        request.session['departamentoDigital'] = departamento
    return render(request, 'ticket/ticketdigital.html', {'codigo': codigo, 'departamento': departamento, 'fecha':fecha_actual, 'hora': hora_actual_str})

def digital_crear_ticket_registro_tesis(request):
    if 'codigoDigital' in request.session:
        codigo = request.session.get('codigoDigital')
        fecha_actual = request.session.get('fechaDigital')
        hora_actual_str = request.session.get('horaDigital')
        departamento = request.session.get('departamentoDigital')
    else:
        dato = obtener_ultimo_dato_registro()
        codigo = dato.split('-')
        numero_siguiente = str(int(codigo[1]) + 1).zfill(3)
        fecha_actual = date.today().strftime('%Y-%m-%d')
        hora_actual = datetime.now()
        hora_actual_str = hora_actual.strftime('%H:%M:%S')

        data_admisiones = {
            'codigo': 'RGT-'+numero_siguiente,
            'departamento': 'Registro/Tesis',
            'fecha': fecha_actual,
            'atentido': False
        }
        save_registro(request, data_admisiones)
        codigo = 'RGT-'+numero_siguiente

        departamento = 'RGT, REG = Registro - Tesis'
        request.session['codigoDigital'] = codigo
        request.session['fechaDigital'] = fecha_actual
        request.session['horaDigital'] = hora_actual_str
        request.session['departamentoDigital'] = departamento
    return render(request, 'ticket/ticketdigital.html', {'codigo': codigo, 'departamento': departamento, 'fecha':fecha_actual, 'hora': hora_actual_str})

def digital_crear_ticket_registro_convalidacion(request):
    if 'codigoDigital' in request.session:
        codigo = request.session.get('codigoDigital')
        fecha_actual = request.session.get('fechaDigital')
        hora_actual_str = request.session.get('horaDigital')
        departamento = request.session.get('departamentoDigital')
    else:
        dato = obtener_ultimo_dato_registro()
        codigo = dato.split('-')
        numero_siguiente = str(int(codigo[1]) + 1).zfill(3)
        fecha_actual = date.today().strftime('%Y-%m-%d')
        hora_actual = datetime.now()
        hora_actual_str = hora_actual.strftime('%H:%M:%S')

        data_admisiones = {
            'codigo': 'RGC-'+numero_siguiente,
            'departamento': 'Registro/Convalidacion',
            'fecha': fecha_actual,
            'atentido': False
        }
        save_registro(request, data_admisiones)
        codigo = 'RGC-'+numero_siguiente

        departamento = 'RGC, REG = Registro - Convalidacion'
        request.session['codigoDigital'] = codigo
        request.session['fechaDigital'] = fecha_actual
        request.session['horaDigital'] = hora_actual_str
        request.session['departamentoDigital'] = departamento
    return render(request, 'ticket/ticketdigital.html', {'codigo': codigo, 'departamento': departamento, 'fecha':fecha_actual, 'hora': hora_actual_str})

def digital_crear_ticket_registro_retiros(request):
    if 'codigoDigital' in request.session:
        codigo = request.session.get('codigoDigital')
        fecha_actual = request.session.get('fechaDigital')
        hora_actual_str = request.session.get('horaDigital')
        departamento = request.session.get('departamentoDigital')
    else:
        dato = obtener_ultimo_dato_registro()
        codigo = dato.split('-')
        numero_siguiente = str(int(codigo[1]) + 1).zfill(3)
        fecha_actual = date.today().strftime('%Y-%m-%d')
        hora_actual = datetime.now()
        hora_actual_str = hora_actual.strftime('%H:%M:%S')

        data_admisiones = {
            'codigo': 'RGR-'+numero_siguiente,
            'departamento': 'Registro/Retiros',
            'fecha': fecha_actual,
            'atentido': False
        }
        save_registro(request, data_admisiones)
        codigo = 'RGR-'+numero_siguiente

        departamento = 'RGR, REG = Registro - Retiros/Congelacion'
        request.session['codigoDigital'] = codigo
        request.session['fechaDigital'] = fecha_actual
        request.session['horaDigital'] = hora_actual_str
        request.session['departamentoDigital'] = departamento
    return render(request, 'ticket/ticketdigital.html', {'codigo': codigo, 'departamento': departamento, 'fecha':fecha_actual, 'hora': hora_actual_str})

def digital_crear_ticket_registro_suficiencia(request):
    if 'codigoDigital' in request.session:
        codigo = request.session.get('codigoDigital')
        fecha_actual = request.session.get('fechaDigital')
        hora_actual_str = request.session.get('horaDigital')
        departamento = request.session.get('departamentoDigital')
    else:
        dato = obtener_ultimo_dato_registro()
        codigo = dato.split('-')
        numero_siguiente = str(int(codigo[1]) + 1).zfill(3)
        fecha_actual = date.today().strftime('%Y-%m-%d')
        hora_actual = datetime.now()
        hora_actual_str = hora_actual.strftime('%H:%M:%S')

        data_admisiones = {
            'codigo': 'RGS-'+numero_siguiente,
            'departamento': 'Registro/Suficiencia',
            'fecha': fecha_actual,
            'atentido': False
        }
        save_registro(request, data_admisiones)
        codigo = 'RGS-'+numero_siguiente

        departamento = 'RGS, REG = Registro - Suficiencia'
        request.session['codigoDigital'] = codigo
        request.session['fechaDigital'] = fecha_actual
        request.session['horaDigital'] = hora_actual_str
        request.session['departamentoDigital'] = departamento
    return render(request, 'ticket/ticketdigital.html', {'codigo': codigo, 'departamento': departamento, 'fecha':fecha_actual, 'hora': hora_actual_str})

def digital_crear_ticket_registro_graduacion(request):
    if 'codigoDigital' in request.session:
        codigo = request.session.get('codigoDigital')
        fecha_actual = request.session.get('fechaDigital')
        hora_actual_str = request.session.get('horaDigital')
        departamento = request.session.get('departamentoDigital')
    else:
        dato = obtener_ultimo_dato_registro()
        codigo = dato.split('-')
        numero_siguiente = str(int(codigo[1]) + 1).zfill(3)
        fecha_actual = date.today().strftime('%Y-%m-%d')
        hora_actual = datetime.now()
        hora_actual_str = hora_actual.strftime('%H:%M:%S')

        data_admisiones = {
            'codigo': 'RGG-'+numero_siguiente,
            'departamento': 'Registro/Graduaciones',
            'fecha': fecha_actual,
            'atentido': False
        }
        save_registro(request, data_admisiones)
        codigo = 'RGG-'+numero_siguiente

        departamento = 'RGG, REG = Registro - Graduaciones'
        request.session['codigoDigital'] = codigo
        request.session['fechaDigital'] = fecha_actual
        request.session['horaDigital'] = hora_actual_str
        request.session['departamentoDigital'] = departamento
    return render(request, 'ticket/ticketdigital.html', {'codigo': codigo, 'departamento': departamento, 'fecha':fecha_actual, 'hora': hora_actual_str})

def digital_crear_ticket_registro_taller(request):
    if 'codigoDigital' in request.session:
        codigo = request.session.get('codigoDigital')
        fecha_actual = request.session.get('fechaDigital')
        hora_actual_str = request.session.get('horaDigital')
        departamento = request.session.get('departamentoDigital')
    else:
        dato = obtener_ultimo_dato_registro()
        codigo = dato.split('-')
        numero_siguiente = str(int(codigo[1]) + 1).zfill(3)
        fecha_actual = date.today().strftime('%Y-%m-%d')
        hora_actual = datetime.now()
        hora_actual_str = hora_actual.strftime('%H:%M:%S')

        data_admisiones = {
            'codigo': 'RTT-'+numero_siguiente,
            'departamento': 'Registro/Taller',
            'fecha': fecha_actual,
            'atentido': False
        }
        save_registro(request, data_admisiones)
        codigo = 'RTT-'+numero_siguiente

        departamento = 'RTT, REG = Registro - Taller'
        request.session['codigoDigital'] = codigo
        request.session['fechaDigital'] = fecha_actual
        request.session['horaDigital'] = hora_actual_str
        request.session['departamentoDigital'] = departamento
    return render(request, 'ticket/ticketdigital.html', {'codigo': codigo, 'departamento': departamento, 'fecha':fecha_actual, 'hora': hora_actual_str})

def digital_crear_ticket_registro_apelacion(request):
    if 'codigoDigital' in request.session:
        codigo = request.session.get('codigoDigital')
        fecha_actual = request.session.get('fechaDigital')
        hora_actual_str = request.session.get('horaDigital')
        departamento = request.session.get('departamentoDigital')
    else:
        dato = obtener_ultimo_dato_registro()
        codigo = dato.split('-')
        numero_siguiente = str(int(codigo[1]) + 1).zfill(3)
        fecha_actual = date.today().strftime('%Y-%m-%d')
        hora_actual = datetime.now()
        hora_actual_str = hora_actual.strftime('%H:%M:%S')

        data_admisiones = {
            'codigo': 'RGA-'+numero_siguiente,
            'departamento': 'Registro/Apelaciones',
            'fecha': fecha_actual,
            'atentido': False
        }
        save_registro(request, data_admisiones)
        codigo = 'RGA-'+numero_siguiente

        departamento = 'RGA, REG = Registro - Apelaciones'
        request.session['codigoDigital'] = codigo
        request.session['fechaDigital'] = fecha_actual
        request.session['horaDigital'] = hora_actual_str
        request.session['departamentoDigital'] = departamento
    return render(request, 'ticket/ticketdigital.html', {'codigo': codigo, 'departamento': departamento, 'fecha':fecha_actual, 'hora': hora_actual_str})

def digital_crear_ticket_registro_retencion(request):
    if 'codigoDigital' in request.session:
        codigo = request.session.get('codigoDigital')
        fecha_actual = request.session.get('fechaDigital')
        hora_actual_str = request.session.get('horaDigital')
        departamento = request.session.get('departamentoDigital')
    else:
        dato = obtener_ultimo_dato_registro()
        codigo = dato.split('-')
        numero_siguiente = str(int(codigo[1]) + 1).zfill(3)
        fecha_actual = date.today().strftime('%Y-%m-%d')
        hora_actual = datetime.now()
        hora_actual_str = hora_actual.strftime('%H:%M:%S')

        data_admisiones = {
            'codigo': 'RRT-'+numero_siguiente,
            'departamento': 'Registro/Retenciones',
            'fecha': fecha_actual,
            'atentido': False
        }
        save_registro(request, data_admisiones)
        codigo = 'RRT-'+numero_siguiente

        departamento = 'RRT, REG = Registro - Retenciones'
        request.session['codigoDigital'] = codigo
        request.session['fechaDigital'] = fecha_actual
        request.session['horaDigital'] = hora_actual_str
        request.session['departamentoDigital'] = departamento
    return render(request, 'ticket/ticketdigital.html', {'codigo': codigo, 'departamento': departamento, 'fecha':fecha_actual, 'hora': hora_actual_str})

