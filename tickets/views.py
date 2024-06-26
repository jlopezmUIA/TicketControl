import base64
import json
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render
from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.views.generic.edit import FormView
from tickets.models import agentes, agentes_citas, citas, departamentos, ley700, llamado, metricas, atencion, casosAgente, estadosAgente, ticketControl, tickets, tiemposAgente, tramites, visualizador
from datetime import datetime
from datetime import date
from django.contrib.auth.forms import UserCreationForm
from .envioCorreo import Correo
import threading
from django.views import View
from django.http import Http404, JsonResponse, HttpResponse, HttpResponseRedirect
from .impresion import imprimir
from django.db.models import Q
from django.contrib.auth.forms import AuthenticationForm
from tickets.savedata import delete_agente, delete_agente_cita, eliminar_ley, eliminar_llamado, marcar_estado_ticket, marcar_estado_ticket_unico, marcar_estado_ticket_varios, procesador_datos_crm, save_agente_cita, save_ley, save_llamado, update_cita, eliminar_cita, eliminar_atencion, eliminar_departamento, eliminar_tramite, marcar_ticket, obtener_caso, obtener_cola, obtener_departamento, obtener_primero_dato, obtener_ultimo_dato, obtener_ventanilla, save_agente, save_atencion, save_casos_agente, save_cita, save_configuration, save_departamento, save_estados_agente, save_metricas, save_ticket, save_ticketcontrol, save_tiempos_agente, save_tramite, update_agente, update_casos_agente, update_cola, update_configuration, update_departamento, update_estado, update_estados_agente, update_tiempos_agente, update_tramite

def error_404(request, exception):
    return render(request, '404.html', status=404)

def error_500(request):
    return render(request, '500.html', status=500)

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
            if user.username == 'mercadeo':
                return redirect('configuracion')
            elif user.username == 'recepcion':
                return redirect('recepcion')
            elif user.username == 'callcenter':
                return redirect('control_citas_callcenter')
            else:
                return redirect('admin_side')
        else:
            # El usuario no existe o las credenciales son inválidas
            return render(self.request, self.template_name, {'form': form, 'error': 'Usuario o contraseña incorrectos'})

    def get(self, *args, **kwargs):
        if self.request.user.is_authenticated != True:
            logout(self.request)
        return super(Logueo, self).get(*args, **kwargs)

class CustomLogoutView(View):
    def get(self, request, *args, **kwargs):
        logout(request)
        return HttpResponseRedirect('/')
    
    def post(self, request, *args, **kwargs):
        return self.get(request, *args, **kwargs)

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
    departamento = departamentos.objects.all()
    tramite = tramites.objects.all()
    ley = ley700.objects.all()
    records = atencion.objects.all()
    return render(request, 'administracion/admin.html', {'ley': ley, 'records':records, 'departamentos': departamento, 'tramites': tramite})

@login_required
def colasatencion(request):
    records = atencion.objects.all()
    agente = agentes.objects.all()
    return render(request, 'administracion/colasatencion.html', {'records': records, 'agentes':agente})

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
        
    return render(request, 'administracion/configuracion.html', {'records': records, 'merca':True})

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
    records = estadosAgente.objects.all().order_by('-fecha')
    agente = agentes.objects.all()
    return render(request, 'administracion/estadosagente.html', {'records': records, 'agentes':agente})

@login_required
def casosagente(request):
    records = casosAgente.objects.all().order_by('-fecha')
    agente = agentes.objects.all()
    return render(request, 'administracion/casosagente.html', {'records': records, 'agentes':agente})

@login_required
def ticketsagente(request):
    departamento = departamentos.objects.all()
    ticket = tickets.objects.all().order_by("-id_ticket")
    records = ticketControl.objects.all().order_by('-id_ticketcontrol')
    return render(request, 'administracion/ticketsagente.html', {'records':records, 'departamento': departamento, 'ticket': ticket})

@login_required
def recepcion(request):
    agente = agentes.objects.all()
    departamento = departamentos.objects.all()
    ticket = tickets.objects.all()
    records = ticketControl.objects.all()
    cita = citas.objects.all().order_by('-fecha')
    return render(request, 'administracion/recepcion.html', {'agentes':agente, 'records':records, 'citas':cita, 'departamento': departamento, 'ticket': ticket})

@login_required
def datosagente(request):
    agente = agentes.objects.all()
    agente_cita = agentes_citas.objects.all()
    records = tiemposAgente.objects.all().order_by('-fecha')
    encuestas = metricas.objects.all().order_by('-fecha')
    return render(request, 'administracion/datosagente.html', {'records':records, 'agente_cita': agente_cita, 'agentes': agente, 'encuestas': encuestas})

@login_required
def nuevoagente(request):
    nombreagente = request.POST.get('nombre_agente')
    departamento_select = request.POST.get('tramite_select')
    departamento = departamentos.objects.get(id_departamentos=departamento_select)
    data_agente = {
        'departamento': departamento.nombre,
        'nombreAgente': nombreagente
    }
    save = save_agente(request, data_agente)
    return redirect(request.META.get('HTTP_REFERER'))

@login_required
def nuevoagentecita(request):
    nombreagente = request.POST.get('nombre_agente_cita')
    data_agente = {
        'nombreAgente': nombreagente
    }
    save = save_agente_cita(request, data_agente)
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
            request.session['agente_ventanilla'] = numeroVentanilla

        fecha_actual = date.today().strftime('%Y-%m-%d')

        data_atencion = {
            'agente': agente,
            'numeroVentanilla': numeroVentanilla,
            'colaAtencion': departamento,
            'estadoAtencion': 'Activo'
        }
        request.session['departamentoAgente'] = departamento
        request.session['cantCitas'] = 0
        request.session['cantClientes'] = 0
        request.session["colaNoAtendida"] = {}
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
    agente = agentes.objects.get(pk=agente_id)
    fecha_actual = date.today().strftime('%Y-%m-%d')
    fecha = datetime.now().date()
    cola = obtener_cola(agente_id)

    request.session['cita'] = False
    request.session['cliente'] = 'N/C'
    
    ventanilla = request.session.get('agente_ventanilla')

    if 'departamentoAgente' in request.session:
        depart = request.session.get('departamentoAgente')
        departamento = departamentos.objects.get(nombre=depart)
    
    tranferDepartamentos = departamentos.objects.all()
    tranferTramites = tramites.objects.all()
    
    if departamento.tramitesDepartamento:
        dict = {}
        tramite = tramites.objects.filter(departamento=departamento.pk)
        
        for tr in tramite:
            dict[tr.nombre] = tickets.objects.filter(tramite=tr.nombre, atendido=False, fecha=fecha_actual).count()
        
        if departamento.citasDepartamento:
            cita_obt = citas.objects.filter(nombreAgente=agente.nombreAgente).order_by('-fecha')
            citas_filtradas = []
            for cita in cita_obt:
                cita_fecha = datetime.strptime(cita.fecha, "%Y-%m-%d").date()
                if cita_fecha >= fecha:
                    citas_filtradas.append(cita)

            return render(request, 'agentes/inicio_atencion.html', {'ventanilla':ventanilla, 'agente':agente_id, 'cola': cola, 'departamento':departamento, 'tramites':tramite, 'tranferDepartamentos':tranferDepartamentos, 'tranferTramites':tranferTramites, 'tickets':dict, 'citas':citas_filtradas, 'fecha': fecha_actual})
        else:
            return render(request, 'agentes/inicio_atencion.html', {'ventanilla':ventanilla, 'agente':agente_id, 'cola': cola, 'departamento':departamento, 'tramites':tramite, 'tranferDepartamentos':tranferDepartamentos, 'tranferTramites':tranferTramites, 'tickets':dict})
    else:
        dict = {}
        dict[departamento.nombre] = tickets.objects.filter(departamento=departamento.nombre, atendido=False, fecha=fecha_actual).count()
        if departamento.citasDepartamento:
            cita_obt = citas.objects.filter(nombreAgente=agente.nombreAgente).order_by('-fecha')
            citas_filtradas = []
            for cita in cita_obt:
                cita_fecha = datetime.strptime(cita.fecha, "%Y-%m-%d").date()
                if cita_fecha >= fecha:
                    citas_filtradas.append(cita)
            return render(request, 'agentes/inicio_atencion.html', {'ventanilla':ventanilla, 'agente':agente_id, 'cola': cola, 'departamento':departamento, 'tranferDepartamentos':tranferDepartamentos, 'tranferTramites':tranferTramites, 'tickets':dict, 'citas':citas_filtradas, 'fecha': fecha_actual})
        else:
            return render(request, 'agentes/inicio_atencion.html', {'ventanilla':ventanilla, 'agente':agente_id, 'cola': cola, 'departamento':departamento, 'tranferDepartamentos':tranferDepartamentos, 'tranferTramites':tranferTramites, 'tickets':dict})
        
def digital_ticket_maker(request):
    request.session.flush() 
    return render(request, 'ticket/digitalticketmaker.html')

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
        save = update_estados_agente(request, request.session.get('estadoactual'), hora_actual_str)
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
    data = {}
    status=302
    cola = obtener_cola(request.session.get('id_agente'))
    ventanilla = obtener_ventanilla(request.session.get('id_agente'))
    departamento = obtener_departamento(request.session.get('id_agente'))
    caso = False

    fecha_actual = date.today().strftime('%Y-%m-%d')
    hora_actual = datetime.now()
    hora_actual_str = hora_actual.strftime('%H:%M:%S')

    agente_departamento  = agentes.objects.get(id_agente=request.session.get('id_agente'))
    deparData = departamentos.objects.get(nombre=agente_departamento.departamento)

    if deparData.tramitesDepartamento:
        numero = obtener_primero_dato(request, deparData.nombre, cola)
    else: 
        numero = obtener_primero_dato(request, deparData.nombre, 'N/A')

    if "000" in numero.codigo:
        data = {'codigo': 'N/C'}
        request.session['cliente'] = 'N/C'
        request.session.save()
    else:
        data = {'codigo': numero.codigo}
        marcar_ticket(numero.pk)
        if numero.tramite == 'Cita':
            cita = citas.objects.get(codigo=numero.codigo, estado='Asesor no disponible')
            cita.estado = 'Recibido de otro asesor: '+ agente_departamento.nombreAgente
            cita.save()
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

        idtiempo = save_tiempos_agente(request, data_caso)
        request.session['idtiempo'] = idtiempo.id_tiemposagente

        request.session['cliente'] = numero.pk
        request.session.save()

        save_ticket = save_ticketcontrol(request, data_ticket)

        status=200

        if 'idcasos' in request.session:
            save = update_casos_agente(
                request, request.session.get('idcasos'), "caso")

    return JsonResponse(data, safe=False, status=status)

def numero_agente_cita(request):
    data = {}
    
    status=302
    estado = request.GET.get("estado")
    fecha_actual = date.today().strftime('%Y-%m-%d')
    hora_actual = datetime.now()
    hora_actual_str = hora_actual.strftime('%H:%M:%S')
    
    agente_departamento  = agentes.objects.get(id_agente=request.session.get('id_agente'))
    deparData = departamentos.objects.get(nombre=agente_departamento.departamento)
    
    if deparData.citasDepartamento:

        try:
            cita = citas.objects.exclude(codigo='').get(
                fecha=fecha_actual,
                departamento=deparData.nombre,
                estado='Recibido'
            )
            if cita is not None:
                citaNueva = True
        except ObjectDoesNotExist:
            citaNueva = False
        if citaNueva and estado == 'Disponible':
            if cita.estado == 'Recibido' and cita.nombreAgente != 'N/A':
                data_caso = {
                    'agente': request.session.get('id_agente'),
                    'codigoCaso': cita.codigo,
                    'fecha': str(fecha_actual),
                    'tiempoInicio': str(hora_actual_str),
                    'tiempoFinal': None
                }

                idtiempo = save_tiempos_agente(request, data_caso)
                request.session['idtiempo'] = idtiempo.id_tiemposagente
                request.session.save()

                ticket = tickets.objects.get(codigo=cita.codigo, fecha=fecha_actual)

                request.session['cliente'] = ticket.pk
                request.session.save()

                status=200

                data = {'codigo': cita.codigo}
                marcar_ticket(ticket.pk)

                cita.estado = 'Completado'
                cita.save()

                if 'idcasos' in request.session:
                    update_casos_agente(request, request.session.get('idcasos'), "caso")
    return JsonResponse(data, safe=False, status=status)

def siguiente_ticket(request):
    data = {}
    del request.session['cliente']
    request.session['cliente'] = 'N/D'
    request.session.save()
    return JsonResponse(data, status=200, safe=False)

def terminar_ticket(request):
    data = {}
    fecha_actual = date.today().strftime('%Y-%m-%d')
    hora_actual = datetime.now()
    hora_actual_str = hora_actual.strftime('%H:%M:%S')
    
    idticket = request.session.get('cliente')
    
    save = marcar_estado_ticket_unico(idticket)

    if 'idtiempo' in request.session:
        save = update_tiempos_agente(request, request.session.get('idtiempo'), str(hora_actual_str))
        del request.session['idtiempo']

    request.session['cliente'] = 'N/C'
    request.session.save()

    return JsonResponse(data, status=200, safe=False)

def terminar_ticket_varios(request):
    data = {}
    fecha_actual = date.today().strftime('%Y-%m-%d')
    hora_actual = datetime.now()
    hora_actual_str = hora_actual.strftime('%H:%M:%S')
    
    idticket = request.session.get('cliente')
    
    save = marcar_estado_ticket_varios(idticket)

    if 'idtiempo' in request.session:
        save = update_tiempos_agente(request, request.session.get('idtiempo'), str(hora_actual_str))
        del request.session['idtiempo']

    request.session['cliente'] = 'N/C'
    request.session.save()

    return JsonResponse(data, status=200, safe=False)

def no_presente(request):
    data = {}
    fecha_actual = date.today().strftime('%Y-%m-%d')
    hora_actual = datetime.now()
    hora_actual_str = hora_actual.strftime('%H:%M:%S')
    
    idticket = request.session.get('cliente')
    
    save = marcar_estado_ticket(idticket)

    if 'idtiempo' in request.session and save:
        save = update_tiempos_agente(request, request.session.get('idtiempo'), str(hora_actual_str))
        del request.session['idtiempo']

    request.session['cliente'] = 'N/C'
    request.session.save()

    return JsonResponse(data, status=200, safe=False)

def transferencia(request):
    departamento = request.GET.get("departamento")
    codigo = request.session.get('cliente')
    fecha_actual = date.today().strftime('%Y-%m-%d')

    request.session['cliente'] = 'N/A'
    request.session.save()

    departamento = departamento.split('/')

    if len(departamento) > 1:
        depart = departamento[0]
        tramite = departamento[1]
    else:
        depart = departamento[0]
        tramite = 'N/A'
    
    ticket = tickets.objects.get(pk=codigo)
    data = {
        'codigo': ticket.codigo,
        'departamento': depart,
        'tramite': tramite,
        'fecha': fecha_actual,
        'atentido': False
    }
    save_ticket(request, data)

    save = update_casos_agente(request, request.session.get('idcasos'), "transferencia")

    data = ['success']
    data_completa = json.dumps(data)
    return JsonResponse(data_completa, safe=False)

def ticketcontrol(request):
    fecha_actual = date.today().strftime('%Y-%m-%d')
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

previous_thread = None
def actualizar_tabla(request):
    dic = {}
    fecha_actual = date.today().strftime('%Y-%m-%d')
    if 'cantrecords' in request.session:
        global previous_thread
        recordscant = ticketControl.objects.count()
        cantrecord = request.session.get('cantrecords')
        
        llamado_cant = llamado.objects.count()
        
        if llamado_cant > 0:
            mi_lista2 = []
            request.session['listaRC'] = mi_lista2
            llamado_cliente = llamado.objects.all()
            for ll_cl in llamado_cliente:
                request.session['listaRC'].append(ll_cl.texto)
                eliminar_llamado(ll_cl.pk)
                
                # Crear hilo y esperar a que el hilo anterior termine
                if previous_thread:
                    previous_thread.join()
                
                t = threading.Thread(target=reproductor_cliente, args=(request,))
                t.start()
                request.session['estadoRC'] = True
                previous_thread = t
        
        if int(recordscant) > cantrecord:
            cantregistro = request.session.get('reproduccion')
            # Cantidad de veces que se ha sobrepasado el valor
            cantidad_sobrepasada = recordscant - cantrecord
            request.session['cantrecords'] = recordscant
            
            for _ in range(cantidad_sobrepasada):
                registro = ticketControl.objects.order_by('id_ticketcontrol').last()
                departamento = departamentos.objects.get(siglasDepartamento=registro.departamento)
                codigo = str(registro.codigoCaso).split('-')
                numero = int(codigo[1].lstrip("0"))
                letras = insertar_comas(codigo[0])
                texto = letras+", "+str(numero) + ", dirigirse a la Ventanilla número " + registro.numeroVentanilla+" del área de "+ departamento.nombre
                request.session['listaR'].append(texto)

                # Crear hilo y esperar a que el hilo anterior termine
                if previous_thread:
                    previous_thread.join()
                
                t = threading.Thread(target=reproductor, args=(request,))
                t.start()

                cantregistro += 1
                request.session['reproduccion'] = cantregistro
                request.session['estadoR'] = True
                
                records = ticketControl.objects.filter(fecha=fecha_actual).order_by('-id_ticketcontrol')[:6]
        
                # Crear una lista para almacenar los registros en formato tabular
                tabular_records = []

                for record in records:
                    tabular_record = {
                        'codigoCaso': record.codigoCaso,
                        'numeroVentanilla': record.numeroVentanilla,
                        'departamento': record.departamento,
                    }
                    tabular_records.append(tabular_record)

                dic['tabla'] = tabular_records
                previous_thread = t
            return JsonResponse(dic, safe=False, status=200)
        else:
            reproductor(request)
            mi_lista = request.session.get('listaR', [])
            mi_lista.clear()
            request.session['listaR'] = mi_lista
            return JsonResponse(dic, safe=False, status=302)
            
    else:
        dic = {
            'success': False
        }
        recordscant = ticketControl.objects.count()
        request.session['cantrecords'] = recordscant
        request.session['reproduccion'] = recordscant
        return JsonResponse(dic, safe=False, status=200)

def insertar_comas(text):
    return ",".join(char for char in text)

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

def reproductor_cliente(request):
    dic = {}
    list = request.session.get('listaRC', [])
    status = request.session.get('estadoRC')
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
    request.session['estadoRC'] = False
    # mi_lista = request.session.get('listaRC', [])
    # mi_lista.clear()
    # request.session['listaRC'] = mi_lista

    return JsonResponse(dic, safe=False)

def llamar_ticket(request):
    dic = {}
    idagente = request.session.get('id_agente')
    agente = agentes.objects.get(id_agente=idagente)
    ventanilla = request.session.get('agente_ventanilla')
    codigoCliente = request.GET.get('codigo')
    codigo = str(codigoCliente).split('-')
    numero = int(codigo[1].lstrip("0"))
    letras = insertar_comas(codigo[0])
    
    texto = letras+", "+str(numero) + ", dirigirse a la Ventanilla número " + ventanilla +" del área de "+ agente.departamento
    
    data = {
        'texto':texto
    }
    
    save = save_llamado(request, data)
    
    dic = {
        'success': False
    }
    return JsonResponse(dic, safe=False, status=200)

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

        departamento = departamentos.objects.get(nombre=request.POST.get('departamento'))

        request.session['agenteEncuesta'] = agente
        request.session['ventanillaEncuesta'] = numeroVentanilla
        request.session['departamentoEncuesta'] = departamento.siglasDepartamento
        
    return redirect('ticket_control_encuesta')

def ticketcontrolEncuesta(request):
    ventanilla = request.session.get('ventanillaEncuesta')
    departamentoAgente = request.session.get('departamentoEncuesta')
    return render(request, 'encuestas/encuesta_visor.html', {'ventanilla': ventanilla, 'departamento': departamentoAgente})

def ticket_encuesta(request):
    ventanilla = request.session.get('ventanillaEncuesta')
    departamentoAgente = request.session.get('departamentoEncuesta')
    
    status=200

    if 'last_ticket_id' in request.session:
        last_ticket_id = request.session.get('last_ticket_id')
        try:
            new_last_ticket = ticketControl.objects.latest('id_ticketcontrol')
        except:
            new_last_ticket = ticketControl(pk = 0)

        if new_last_ticket.pk == last_ticket_id:
            dic = {
                'codigo': 'N/C'
            }
        elif new_last_ticket.pk > last_ticket_id:
            times = new_last_ticket.pk - last_ticket_id
            for vfc in range(times):
                last_ticket_id += 1
                ticket = ticketControl.objects.get(id_ticketcontrol=last_ticket_id)
                if ticket.numeroVentanilla == ventanilla and ticket.departamento == departamentoAgente:
                    request.session['last_ticket_id'] = new_last_ticket.pk
                    dic = {
                        'codigo': ticket.codigoCaso
                    }
    else:
        try:
            last_ticket_id = ticketControl.objects.latest('id_ticketcontrol')
            request.session['last_ticket_id'] = last_ticket_id.pk
        except:
            last_ticket_id = 0
            request.session['last_ticket_id'] = last_ticket_id
            
        dic = {
            'codigo': 'N/C'
        }

    return JsonResponse(dic, safe=False, status=status)

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

    nombre_agente = agentes.objects.get(pk=agente)
    
    if estado != 'Satisfecho' and estado != 'Neutral':
        nombre_agente = agentes.objects.get(pk=agente)
        
        correo_destinatario = 'jlopezm@uia.ac.cr'
        correo_cc = 'apereirac@uia.ac.cr'
        subject = f'Encuesta: Mala Calificación - {fecha_actual}.'
        mensaje = f'El agente, {nombre_agente.nombreAgente}, ha recibido una mala calificación.\n\nEl código del ticket es: {codigo}\n\nEl motivo de la mala calificación es: {estado}.\n\nUn saludo cordial.\nUIA.'
            
        Correo.envioCorreos(correoSend=0, emailTo=correo_destinatario,emailCC=correo_cc,asunto=subject,mensaje=mensaje,archivo=None)
        
    save_metricas(request, data)
    
    dic = {
        'success': True
    }

    return JsonResponse(dic, safe=False)

#DIGITAL
def digital_crear_ticket(request):
    hora_actual = datetime.now()
    hora_actual_str = hora_actual.strftime('%H:%M:%S')
    dato = request.GET.get("departamento")
    ticket = dato.split(",")

    if len(ticket) > 1:
        tramitesData = tramites.objects.get(id_tramites=ticket[1])
        departamentoData = departamentos.objects.get(id_departamentos=tramitesData.departamento.pk)
        tramite = tramitesData.nombre
        
    else:
        departamentoData = departamentos.objects.get(id_departamentos=ticket[0])
        tramite = 'N/A'

    ultimoTicket = obtener_ultimo_dato(departamentoData.nombre, tramite)
    codigo = ultimoTicket.split('-')
    numero_siguiente = str(int(codigo[1]) + 1).zfill(3)
    fecha_actual = date.today().strftime('%Y-%m-%d')

    if tramite == "N/A":
        data = {
            'codigo': departamentoData.codigoDepartamento+'-'+numero_siguiente,
            'departamento': departamentoData.nombre,
            'tramite': tramite,
            'fecha': fecha_actual,
            'atentido': False
        }
        save_ticket(request, data)
        codigo = departamentoData.codigoDepartamento+'-'+numero_siguiente
        departamento = departamentoData.codigoDepartamento+', '+departamentoData.siglasDepartamento+' = '+departamentoData.nombre
    else:
        data = {
            'codigo': tramitesData.codigoTramite+'-'+numero_siguiente,
            'departamento': departamentoData.nombre,
            'tramite': tramite,
            'fecha': fecha_actual,
            'atentido': False
        }
        save_ticket(request, data)
        codigo = tramitesData.codigoTramite+'-'+numero_siguiente
        departamento = tramitesData.codigoTramite+', '+departamentoData.siglasDepartamento+' = '+departamentoData.nombre+' - '+tramitesData.nombre

        departamento = 'AD, ADM = Admisiones'
        request.session['codigoDigital'] = codigo
        request.session['fechaDigital'] = fecha_actual
        request.session['horaDigital'] = hora_actual_str
        request.session['departamentoDigital'] = departamento
    return render(request, 'ticket/ticketdigital.html', {'codigo': codigo, 'departamento': departamento, 'fecha':fecha_actual, 'hora': hora_actual_str})

@login_required
def nuevodepartamento(request):
    nombredepartamento = request.POST.get('nombreDepartamento')
    aliasDepartamento = request.POST.get('aliasDepartamento')
    codigodepartamento = request.POST.get('codigoDepartamento')
    siglasdepartamento = request.POST.get('siglasDepartamento')
    citasDepartamento = request.POST.get('citasDepartamento')
    notiDepartamento = request.POST.get('notiDepartamento')

    data_agente = {
        'nombre': nombredepartamento,
        'alias': aliasDepartamento,
        'codigoDepartamento': codigodepartamento,
        'siglasDepartamento': siglasdepartamento,
        'tramitesDepartamento': False,
        'citasDepartamento': citasDepartamento,
        'notiDepartamento': notiDepartamento
    }

    save = save_departamento(request, data_agente)
    return redirect(request.META.get('HTTP_REFERER'))

@login_required
def modificardepartamento(request):
    iddepartamento = request.POST.get('idDepartamento')
    nombredepartamento = request.POST.get('nombreDepartamento')
    aliasDepartamento = request.POST.get('aliasDepartamento')
    codigodepartamento = request.POST.get('codigoDepartamento')
    siglasdepartamento = request.POST.get('siglasDepartamento')
    citasDepartamento = request.POST.get('citasDepartamento')
    notiDepartamento = request.POST.get('notiDepartamento')

    if citasDepartamento is None:
        citasDepartamento = False

    departamentoSelected = departamentos.objects.get(id_departamentos=iddepartamento)

    data = {
        'id_departamentos': iddepartamento,
        'nombre': nombredepartamento,
        'alias': aliasDepartamento,
        'codigoDepartamento': codigodepartamento,
        'siglasDepartamento': siglasdepartamento,
        'tramitesDepartamento': departamentoSelected.tramitesDepartamento,
        'citasDepartamento': citasDepartamento,
        'notiDepartamento': notiDepartamento
    }

    save = update_departamento(request, data)
    return redirect(request.META.get('HTTP_REFERER'))

@login_required
def eliminardepartamento(request):
    iddepartamento = request.POST.get('idDepartamento')

    data = {
        'id_departamentos': iddepartamento
    }

    save = eliminar_departamento(request, data)
    return redirect(request.META.get('HTTP_REFERER'))

def obtener_departamentos(request):
    departamentos_dict = {}
    departamentos_queryset = departamentos.objects.all()

    for departamento in departamentos_queryset:
        departamentos_dict[departamento.id_departamentos] = departamento.nombre

    return JsonResponse(departamentos_dict, safe=False)

@login_required
def nuevotramite(request):
    departamento = request.POST.get('tramite_select')
    nombretramiteo = request.POST.get('nombreTramite')
    codigotramite = request.POST.get('codigoTramite')

    departamentoSelected = departamentos.objects.get(id_departamentos=departamento)

    dataDepartamento = {
        'id_departamentos': departamentoSelected.pk,
        'nombre': departamentoSelected.nombre,
        'alias': departamentoSelected.alias,
        'codigoDepartamento': departamentoSelected.codigoDepartamento,
        'siglasDepartamento': departamentoSelected.siglasDepartamento,
        'tramitesDepartamento': True,
        'citasDepartamento': departamentoSelected.citasDepartamento,
        'notiDepartamento': departamentoSelected.notiDepartamento
    }

    saveDepartamento = update_departamento(request, dataDepartamento)

    data = {
        'departamento':departamento,
        'nombre': nombretramiteo,
        'codigoTramite': codigotramite
    }

    save = save_tramite(request, data)
    return redirect(request.META.get('HTTP_REFERER'))

@login_required
def modificartramite(request):
    idtramite = request.POST.get('idTramite')
    nombretramiteo = request.POST.get('nombreTramite')
    codigotramite = request.POST.get('codigoTramite')

    data = {
        'id_tramites': idtramite,
        'nombre': nombretramiteo,
        'codigoTramite': codigotramite
    }

    save = update_tramite(request, data)
    return redirect(request.META.get('HTTP_REFERER'))

@login_required
def eliminartramite(request):
    idtramite = request.POST.get('idTramite')

    data = {
        'id_tramites': idtramite
    }

    save = eliminar_tramite(request, data)
    return redirect(request.META.get('HTTP_REFERER'))

def ticket_maker(request):
    departamento = departamentos.objects.all()

    if departamento.count() % 2 != 0:
        par = True
    else:
        par = False

    citaDepartamento = departamentos.objects.filter(citasDepartamento=True).exists()

    tramite = tramites.objects.all()
    
    return render(request, 'ticket/ticketmaker.html', {'departamentos': departamento, 'tramites': tramite, 'par':par, 'citas':citaDepartamento})

def crear_ticket(request):
    dato = request.GET.get("departamento")
    ticket = dato.split(",")
    
    hora_actual = datetime.now()
    hora_actual_str = hora_actual.strftime('%H:%M:%S')

    if len(ticket) > 1:
        tramitesData = tramites.objects.get(id_tramites=ticket[1])
        departamentoData = departamentos.objects.get(id_departamentos=tramitesData.departamento.pk)
        tramite = tramitesData.nombre
        
    else:
        departamentoData = departamentos.objects.get(id_departamentos=ticket[0])
        tramite = 'N/A'

    ultimoTicket = obtener_ultimo_dato(departamentoData.nombre, tramite)
    codigo = ultimoTicket.split('-')
    numero_siguiente = str(int(codigo[1]) + 1).zfill(3)
    fecha_actual = date.today().strftime('%Y-%m-%d')

    if tramite == "N/A":
        data = {
            'codigo': departamentoData.codigoDepartamento+'-'+numero_siguiente,
            'departamento': departamentoData.nombre,
            'tramite': tramite,
            'fecha': fecha_actual,
            'hora': hora_actual_str,
            'atentido': False,
            'estado': 'N/A'
        }
        save_ticket(request, data)
        codigo = departamentoData.codigoDepartamento+'-'+numero_siguiente
        departamento = departamentoData.codigoDepartamento+', '+departamentoData.siglasDepartamento+' = '+departamentoData.nombre
    else:
        data = {
            'codigo': tramitesData.codigoTramite+'-'+numero_siguiente,
            'departamento': departamentoData.nombre,
            'tramite': tramite,
            'fecha': fecha_actual,
            'hora': hora_actual_str,
            'atentido': False,
            'estado': 'N/A'
        }
        save_ticket(request, data)
        codigo = tramitesData.codigoTramite+'-'+numero_siguiente
        departamento = tramitesData.codigoTramite+', '+departamentoData.siglasDepartamento+' = '+departamentoData.nombre+' - '+tramitesData.nombre

    imprimir(codigo, departamento)
    dic = {
        'success': True
    }

    return JsonResponse(dic, safe=False)

def cargar_tramites(request):
    iddepartamento = request.GET.get("departamento")
    tramitesData = tramites.objects.filter(departamento=iddepartamento)
    tramites_dict = {}
    for tramite in tramitesData:
        tramites_dict[tramite.id_tramites] = tramite.nombre

    return JsonResponse(tramites_dict, safe=False)

def obtener_todos_departamentos(request):
    departamentos_dict = {}
    departamentos_queryset = departamentos.objects.all()

    for departamento in departamentos_queryset:
        departamentos_dict[departamento.id_departamentos] = departamento.nombre

    return JsonResponse(departamentos_dict, safe=False)

@login_required
def eliminaragente(request):
    idagente = request.POST.get('id_agente_modal')
    save = delete_agente(request, idagente)
    return redirect(request.META.get('HTTP_REFERER'))

@login_required
def eliminaragentecita(request):
    idagente = request.POST.get('id_agente_cita_modal')
    save = delete_agente_cita(request, idagente)
    return redirect(request.META.get('HTTP_REFERER'))

@login_required
def modificaragente(request): 
    id_agente = request.POST.get('id_agente_modal')
    nombre_agente = request.POST.get('nombre_agente')
    tramite_select = request.POST.get('tramite_select')

    departamentoSelected = departamentos.objects.get(id_departamentos=tramite_select)

    data = {
        'id_agente': id_agente,
        'nombreAgente': nombre_agente,
        'departamento': departamentoSelected.nombre
    }

    save = update_agente(request, data)
    return redirect(request.META.get('HTTP_REFERER'))

@login_required
def control_citas(request):
    records = citas.objects.all().order_by('-fecha')
    agente = agentes.objects.all()
    return render(request, 'administracion/citas.html', {'records': records, 'agentes': agente})

@login_required
def control_citas_callcenter(request):
    records = citas.objects.all().order_by('-fecha')
    agente = agentes.objects.all()
    return render(request, 'administracion/citas_callcenter.html', {'records': records, 'agentes': agente})

@login_required
def nuevacita(request):
    departamento_cita = request.POST.get('departamento_cita')
    agentes_cita = request.POST.get('agente_cita')
    identificacion = request.POST.get('identificacion')
    nombre = request.POST.get('nombre')
    telefono = request.POST.get('telefono')
    fecha = request.POST.get('fecha')
    hora = request.POST.get('hora')

    departamentoSelected = departamentos.objects.get(nombre=departamento_cita)
                
    cita_list = {
        'departamento': departamentoSelected.nombre,
        'nombreAgente': agentes_cita,
        'identificacion': identificacion,
        'nombreCliente': nombre,
        'telefono': telefono,
        'fecha': str(fecha),
        'hora': str(hora),
        'estado': 'Pendiente'
    }

    save = save_cita(request, cita_list)

    return redirect(request.META.get('HTTP_REFERER'))

def nuevacitaagente(request):
    dict = {}
    departamento_siglas = obtener_departamento(request.session.get('id_agente'))
    departamento = departamentos.objects.get(siglasDepartamento=departamento_siglas)
    identificacion = request.GET.get('identificacion')
    nombre = request.GET.get('nombre')
    telefono = request.GET.get('telefono')
    fecha = request.GET.get('fecha')
    hora = request.GET.get('hora')

    agente = agentes.objects.get(pk=request.session.get('id_agente'))

    try:
        cita = citas.objects.get(fecha=fecha, hora=hora, nombreAgente=agente.nombreAgente)
        status=302
    except:
        status=200

        cita_list = {
            'departamento': departamento.nombre,
            'nombreAgente': agente.nombreAgente,
            'identificacion': identificacion,
            'nombreCliente': nombre,
            'telefono': telefono,
            'fecha': str(fecha),
            'hora': str(hora),
            'estado': 'Pendiente'
        }
        
        save = save_cita(request, cita_list)

    dict = {
        'success':True
    }
    return JsonResponse(dict, safe=False, status=status)

def modificarcita(request):
    dict = {}
    status = 200
    id = request.GET.get('id')
    fecha = request.GET.get('fecha')
    hora = request.GET.get('hora')

    data = {
        'id_cita': id,
        'fecha': fecha,
        'hora': hora
    }

    save = update_cita(request, data)

    return JsonResponse(dict, safe=False, status=status)

def eliminarcita(request):
    dict = {}
    status = 200
    id = request.GET.get('id')

    save = eliminar_cita(id)

    return JsonResponse(dict, safe=False, status=status)

def obtener_departamentos_cita(request):
    departamentos_dict = {}
    departamentos_queryset = departamentos.objects.filter(citasDepartamento=True)

    for departamento in departamentos_queryset:
        departamentos_dict[departamento.id_departamentos] = departamento.alias

    return JsonResponse(departamentos_dict, safe=False)

def actualizar_tabla_departamentos(request):
    fecha_actual = date.today().strftime('%Y-%m-%d')
    
    cantCitas = request.session.get('cantCitas')
    cantClientes = request.session.get('cantClientes')
    colaNoAtendida = request.session.get("colaNoAtendida")
    
    if 'departamentoAgente' in request.session:
        depart = request.session.get('departamentoAgente')
        departamento = departamentos.objects.get(nombre=depart)

    dict = {}
    tramite = tramites.objects.filter(departamento=departamento.pk)
    
    cant_ley = tickets.objects.filter(tramite='7600', atendido=False, fecha=fecha_actual).count()
        
    if departamento.tramitesDepartamento:
        tabular_records = []
        cant_cita = tickets.objects.filter(tramite='Cita', atendido=False, fecha=fecha_actual, departamento=departamento.nombre).count() 
        cant_cliente = tickets.objects.filter(departamento=departamento.nombre, atendido=False, fecha=fecha_actual).count()
        if cantCitas != cant_cita or cantClientes != cant_cliente:
            
            if cant_ley > 0:
                ley_tk = tickets.objects.filter(tramite='7600', atendido=False, fecha=fecha_actual, departamento=departamento.nombre).count() 
                if ley_tk > 0:
                    tabular_record_citas = {
                        'nombreDepartamento':'Ley 7600',
                        'cantidad': ley_tk
                    }
                    tabular_records.append(tabular_record_citas)
                    
            if cant_cita > 0:
                tabular_record_citas = {
                    'nombreDepartamento':'Citas',
                    'cantidad': cant_cita
                }
                tabular_records.append(tabular_record_citas)
            tabular_colas = []
            tabular_cola = {}
            colas_filtradas = atencion.objects.exclude(estadoAtencion='Desconectado')
            for tr in tramite:
                cant = tickets.objects.filter(tramite=tr.nombre, atendido=False, fecha=fecha_actual).count()
                if cant > 0:
                    #Analisis de colas
                    colas_exist = colas_filtradas.filter(colaAtencion__icontains=tr.nombre).exists()
                    if colas_exist:
                        pass
                    else:
                        tabular_cola = {
                            'nombreDepartamento':tr.nombre
                        }
                        request.session["colaNoAtendida"] = tabular_cola
                        tabular_colas.append(tabular_cola)
                    tabular_record = {
                        'nombreDepartamento':tr.nombre,
                        'cantidad': cant
                    }
                    tabular_records.append(tabular_record)
            if tabular_cola and colaNoAtendida != tabular_cola:
                dict['cola'] = tabular_colas
                
            if cant_cita < cantCitas:  
                status=202
            else:
                status=200
                
            request.session['cantCitas'] = cant_cita
        elif cantClientes == 0:
            if cant_cita > 0:
                tabular_record_citas = {
                    'nombreDepartamento':'Citas',
                    'cantidad': cant_cita
                }
                tabular_records.append(tabular_record_citas)
                
            if cant_ley > 0:
                ley_tk = tickets.objects.filter(tramite='7600', atendido=False, fecha=fecha_actual, departamento=departamento.nombre).count() 
                if ley_tk > 0:
                    tabular_record_citas = {
                        'nombreDepartamento':'Ley 7600',
                        'cantidad': ley_tk
                    }
                    tabular_records.append(tabular_record_citas)
            
            for tr in tramite:
                cant = tickets.objects.filter(tramite=tr.nombre, atendido=False, fecha=fecha_actual).count()
                if cant > 0:
                    tabular_record = {
                        'nombreDepartamento':tr.nombre,
                        'cantidad': cant
                    }
                    tabular_records.append(tabular_record)
            
            if cant_cita < cantCitas:   
                status=202
            else:
                status=202
        else:
            status=302
            
    else:
        tabular_records = []
        cant_cliente = tickets.objects.filter(departamento=departamento.nombre, atendido=False, fecha=fecha_actual).count()
        if cantClientes != cant_cliente:
            
            if cant_ley > 0:
                ley_tk = tickets.objects.filter(tramite='7600', atendido=False, fecha=fecha_actual, departamento=departamento.nombre).count() 
                if ley_tk > 0:
                    tabular_record_citas = {
                        'nombreDepartamento':'Ley 7600',
                        'cantidad': ley_tk
                    }
                    tabular_records.append(tabular_record_citas)
            
            tabular_record = {
                'nombreDepartamento':departamento.nombre,
                'cantidad': tickets.objects.filter(departamento=departamento.nombre, atendido=False, fecha=fecha_actual).count()
            }
            tabular_records.append(tabular_record)
            
            if cant_cliente < cantClientes:  
                status=202
            else:
                status=200
                
            request.session['cantClientes'] = cant_cliente
        elif cant_cliente == 0:
            tabular_record = {
                'nombreDepartamento':departamento.nombre,
                'cantidad': tickets.objects.filter(departamento=departamento.nombre, atendido=False, fecha=fecha_actual).count()
            }
            tabular_records.append(tabular_record)
            
            if cant_ley > 0:
                ley_tk = tickets.objects.filter(tramite='7600', atendido=False, fecha=fecha_actual, departamento=departamento.nombre).count() 
                if ley_tk > 0:
                    tabular_record_citas = {
                        'nombreDepartamento':'Ley 7600',
                        'cantidad': ley_tk
                    }
                    tabular_records.append(tabular_record_citas)
            
            if cant_cliente < cantClientes:  
                status=202
            else:
                status=202
                
            request.session['cantClientes'] = cant_cliente
        else:
            status=302
    dict['tabla'] = tabular_records
    return JsonResponse(dict, safe=False, status=status)

def actualizar_tabla_citas_actuales(request):
    agente_id = request.session.get('id_agente')
    agente = agentes.objects.get(pk=agente_id)
    fecha = datetime.now().date()

    if 'departamentoAgente' in request.session:
        depart = request.session.get('departamentoAgente')
        departamento = departamentos.objects.get(nombre=depart)

    dict = {}
    if departamento.citasDepartamento:
        cita_obt = citas.objects.filter(nombreAgente=agente.nombreAgente).order_by('-fecha')
        citas_filtradas = []
        for cita in cita_obt:
            cita_fecha = datetime.strptime(cita.fecha, "%Y-%m-%d").date()
            if cita_fecha >= fecha:
                citas_filtrada = {
                    'id_citas': cita.id_citas,
                    'nombreCliente': cita.nombreCliente,
                    'fecha': cita.fecha,
                    'hora': cita.hora,
                    'estado':cita.estado
                }
                citas_filtradas.append(citas_filtrada)
    
    dict['tabla'] = citas_filtradas
    return JsonResponse(dict, safe=False, status=200)

def actualizar_tabla_citas(request):
    agente_id = request.session.get('id_agente')
    agente = agentes.objects.get(pk=agente_id)
    fecha = datetime.now().date()

    if 'departamentoAgente' in request.session:
        depart = request.session.get('departamentoAgente')
        departamento = departamentos.objects.get(nombre=depart)

    dict = {}
    if departamento.citasDepartamento:
        cita_obt = citas.objects.filter(nombreAgente=agente.nombreAgente)
        citas_filtradas = []
        for cita in cita_obt:
            cita_fecha = datetime.strptime(cita.fecha, "%Y-%m-%d").date()
            if cita_fecha == fecha:
                citas_filtrada = {
                    'nombreCliente': cita.nombreCliente,
                    'fecha': cita.fecha,
                    'hora': cita.hora
                }
                citas_filtradas.append(citas_filtrada)
    
    dict['tabla'] = citas_filtradas
    return JsonResponse(dict, safe=False, status=200)

def crear_ticket_cita(request):
    dato = request.GET.get("departamento")
    identificacion = request.GET.get("identificacion")
    
    hora_actual = datetime.now()
    hora_actual_str = hora_actual.strftime('%H:%M:%S')

    departamentoData = departamentos.objects.get(id_departamentos=dato)

    ultimoTicket = obtener_ultimo_dato(departamentoData.nombre, 'N/A')
    codigo = ultimoTicket.split('-')
    numero_siguiente = str(int(codigo[1]) + 1).zfill(3)
    fecha_actual = date.today().strftime('%Y-%m-%d')

    status=200

    data = {
        'codigo': departamentoData.codigoDepartamento+'-'+numero_siguiente,
        'departamento': departamentoData.nombre,
        'tramite': 'Cita',
        'fecha': fecha_actual,
        'hora': hora_actual_str,
        'atentido': False,
        'estado': 'N/A'
    }
    codigo = departamentoData.codigoDepartamento+'-'+numero_siguiente
    departamento = departamentoData.codigoDepartamento+', '+departamentoData.siglasDepartamento+' = '+departamentoData.nombre
    
    try:
        cita = citas.objects.get(identificacion=identificacion, fecha=fecha_actual, estado='Pendiente')
        agente = agentes.objects.get(nombreAgente=cita.nombreAgente)
        info = atencion.objects.get(agente=agente.pk)
        estado = estadosAgente.objects.filter(agente=agente.pk, fecha=fecha_actual).last()
        data_ticket = {
            'codigoCaso': codigo,
            'numeroVentanilla': info.numeroVentanilla,
            'departamento': departamentoData.siglasDepartamento,
            'fecha': str(fecha_actual)
        }
        if estado.estado == 'Disponible':
            cita.estado = 'Recibido'
            cita.codigo = codigo
            cita.save()
            save_ticket(request, data)
            imprimir(codigo, departamento)
            save_ticket_control = save_ticketcontrol(request, data_ticket)
        else:
            cita.estado = 'Asesor no disponible'
            cita.codigo = codigo
            cita.save()
            save_ticket(request, data)
            imprimir(codigo, departamento) 
    except:
        try:
            cita = citas.objects.get(Q(estado='Pendiente') | Q(estado='Atrasado'), identificacion=identificacion)
            agente = agentes.objects.get(nombreAgente=cita.nombreAgente)
            info = atencion.objects.get(agente=agente.pk)
            estado = estadosAgente.objects.filter(agente=agente.pk, fecha=fecha_actual).last()
            data_ticket = {
                'codigoCaso': codigo,
                'numeroVentanilla': info.numeroVentanilla,
                'departamento': departamentoData.siglasDepartamento,
                'fecha': str(fecha_actual)
            }
            if estado.estado == 'Disponible':
                cita.estado = 'Recibido'
                cita.codigo = codigo
                cita.fecha = fecha_actual
                cita.save()
                save_ticket(request, data)
                imprimir(codigo, departamento)
                save_ticket_control = save_ticketcontrol(request, data_ticket)
            else:
                cita.estado = 'Asesor no disponible'
                cita.codigo = codigo
                cita.fecha = fecha_actual
                cita.save()
                save_ticket(request, data)
                imprimir(codigo, departamento)
        except:
            status=302

    dic = {
        'success': True
    }

    return JsonResponse(dic, safe=False, status=status)

def actualizar_tabla_departamentos_control(request):
    fecha_actual = date.today().strftime('%Y-%m-%d')

    cantClientes = request.session.get('cantClientes')
    
    dict = {}
    tabular_records = []
    cant_cita = tickets.objects.filter(tramite='Cita', atendido=False, fecha=fecha_actual).count() 
    cant_ley = tickets.objects.filter(tramite='7600', atendido=False, fecha=fecha_actual).count()
    cant_cliente = tickets.objects.filter( atendido=False, fecha=fecha_actual).count()
    departamento = departamentos.objects.all()
    for depart in departamento:
        if cantClientes != cant_cliente:
            
            if cant_ley > 0:
                ley_tk = tickets.objects.filter(tramite='7600', atendido=False, fecha=fecha_actual, departamento=depart.nombre).count() 
                if ley_tk > 0:
                    tabular_record_citas = {
                        'nombreDepartamento':depart.nombre+' - Ley 7600',
                        'cantidad': ley_tk
                    }
                    tabular_records.append(tabular_record_citas)
            
            if cant_cita > 0:
                citas_depart = tickets.objects.filter(tramite='Cita', atendido=False, fecha=fecha_actual, departamento=depart.nombre).count() 
                if citas_depart > 0:
                    tabular_record_citas = {
                        'nombreDepartamento':'Citas de '+depart.nombre,
                        'cantidad': citas_depart
                    }
                    tabular_records.append(tabular_record_citas)
                    
                    
            if depart.tramitesDepartamento:    
                tramite = tramites.objects.filter(departamento=depart.pk)
                for tr in tramite:
                    cant = tickets.objects.filter(tramite=tr.nombre, atendido=False, fecha=fecha_actual).count()
                    if cant > 0:
                        tabular_record = {
                            'nombreDepartamento':tr.nombre,
                            'cantidad': cant
                        }
                        tabular_records.append(tabular_record)
            else:
                cant = tickets.objects.filter(departamento=depart.nombre, atendido=False, fecha=fecha_actual).count()
                tabular_record = {
                    'nombreDepartamento':depart.nombre,
                    'cantidad': cant
                }
                tabular_records.append(tabular_record)
                
    status=200
    
    dict['tabla'] = tabular_records
    return JsonResponse(dict, safe=False, status=status)

def ventanillas_disponibles(request):
    status=200
    agente_ventanillas_no = atencion.objects.exclude(estadoAtencion="Desconectado")
    agente_ventanillas_si = atencion.objects.filter(estadoAtencion="Desconectado")
    
    list_si = []
    list_no = []
    for ventanilla in agente_ventanillas_no:
        list_si.append(ventanilla.numeroVentanilla)
        
    for ventanilla2 in agente_ventanillas_si:
        list_no.append(ventanilla2.numeroVentanilla)
        
    response_data = {
        'list_si': list_si,
        'list_no': list_no
    }
    
    return JsonResponse(response_data, safe=False, status=status)

@login_required
def nueva_ley7600(request):
    departamento = request.POST.get("ley_select")
    ventanilla = request.POST.get("ventanilla")
    data = {
        'departamento': departamento,
        'ventanilla' : ventanilla
    }
    save = save_ley(request, data)
    return redirect(request.META.get('HTTP_REFERER'))

@login_required
def eliminar_ley7600(request):
    id_ley = request.GET.get("id")
    save = eliminar_ley(id_ley)
    return redirect(request.META.get('HTTP_REFERER'))

def crear_ticket_ley(request):
    dato = request.GET.get("departamento")
    
    hora_actual = datetime.now()
    hora_actual_str = hora_actual.strftime('%H:%M:%S')

    departamentoData = departamentos.objects.get(id_departamentos=dato)
    tramite = '7600'

    ultimoTicket = obtener_ultimo_dato(departamentoData.nombre, tramite)
    codigo = ultimoTicket.split('-')
    numero_siguiente = str(int(codigo[1]) + 1).zfill(3)
    fecha_actual = date.today().strftime('%Y-%m-%d')

    data = {
        'codigo': 'L-'+numero_siguiente,
        'departamento': departamentoData.nombre,
        'tramite': tramite,
        'fecha': fecha_actual,
        'hora': hora_actual_str,
        'atentido': False,
        'estado': 'N/A'
    }
    save_ticket(request, data)
    codigo = departamentoData.codigoDepartamento+'-'+numero_siguiente
    departamento = departamentoData.codigoDepartamento+', '+departamentoData.siglasDepartamento+' = '+departamentoData.nombre
    
    imprimir(codigo, departamento)
    dic = {
        'success': True
    }

    return JsonResponse(dic, safe=False)
