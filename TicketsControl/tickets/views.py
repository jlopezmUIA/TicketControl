import base64
import json
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render
from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.views.generic.edit import FormView
from tickets.models import agentes, departamentos, metricas, atencion, casosAgente, estadosAgente, ticketControl, tickets, tiemposAgente, tramites, visualizador
from datetime import datetime
from datetime import date
from django.contrib.auth.forms import UserCreationForm
import threading
from .impresion import imprimir
from django.contrib.auth.forms import AuthenticationForm
from tickets.savedata import delete_agente, eliminar_atencion, eliminar_departamento, eliminar_tramite, marcar_ticket, obtener_caso, obtener_cola, obtener_departamento, obtener_primero_dato, obtener_ultimo_dato, obtener_ventanilla, save_agente, save_atencion, save_casos_agente, save_configuration, save_departamento, save_estados_agente, save_metricas, save_ticket, save_ticketcontrol, save_tiempos_agente, save_tramite, update_agente, update_casos_agente, update_cola, update_configuration, update_departamento, update_estado, update_estados_agente, update_tiempos_agente, update_tramite

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
    departamento = departamentos.objects.all()
    tramite = tramites.objects.all()
    records = atencion.objects.all()
    return render(request, 'administracion/admin.html', {'records':records, 'departamentos': departamento, 'tramites': tramite})

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
    departamento = departamentos.objects.all()
    ticket = tickets.objects.all()
    records = ticketControl.objects.all()
    return render(request, 'administracion/ticketsagente.html', {'records':records, 'departamento': departamento, 'ticket': ticket})

@login_required
def datosagente(request):
    agente = agentes.objects.all()
    records = tiemposAgente.objects.all()
    encuestas = metricas.objects.all()
    return render(request, 'administracion/datosagente.html', {'records':records, 'agentes': agente, 'encuestas': encuestas})

@login_required
def nuevoagente(request):
    nombreagente = request.POST.get('name')
    departamento_select = request.POST.get('tramite_select')
    departamento = departamentos.objects.get(id_departamentos=departamento_select)
    data_agente = {
        'departamento': departamento.nombre,
        'nombreAgente': nombreagente
    }
    save = save_agente(request, data_agente)
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
                
                return redirect('atencion_agentes')

def atencion_agentes(request):
    agente_id = request.session.get('id_agente')
    cola = obtener_cola(agente_id)
    departamento = departamentos.objects.get(nombre=cola)
    tranferDepartamentos = departamentos.objects.all()
    tranferTramites = tramites.objects.all()
    if departamento.tramitesDepartamento:
        tramite = tramites.objects.filter(departamento=departamento.pk)
        return render(request, 'agentes/inicio_atencion.html', {'agente':agente_id, 'cola': cola, 'departamento':departamento, 'tramites':tramite, 'tranferDepartamentos':tranferDepartamentos, 'tranferTramites':tranferTramites})
    else:
        return render(request, 'agentes/inicio_atencion.html', {'agente':agente_id, 'cola': cola, 'departamento':departamento, 'tranferDepartamentos':tranferDepartamentos, 'tranferTramites':tranferTramites})

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

    agente_departamento  = agentes.objects.get(id_agente=request.session.get('id_agente'))
    deparData = departamentos.objects.get(nombre=agente_departamento.departamento)

    if deparData.tramitesDepartamento:
        numero = obtener_primero_dato(deparData.nombre, cola)
    else: 
        numero = obtener_primero_dato(deparData.nombre, 'N/A')

    if "000" in numero.codigo:
        data = {'codigo': 'N/C'}
    else:
        data = {'codigo': numero.codigo}
        marcar_ticket(numero.pk)
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

        request.session['cliente'] = numero.pk

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
    departamento = request.GET.get("departamento")
    codigo = request.session.get('cliente')
    fecha_actual = date.today().strftime('%Y-%m-%d')

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
                departamento = departamentos.objects.get(siglasDepartamento=registro.departamento)
                codigo = str(registro.codigoCaso).split('-')
                numero = int(codigo[1].lstrip("0"))
                texto = codigo[0]+"-"+str(numero) + ", dirigirse a la Ventanilla número " + registro.numeroVentanilla+" del área de "+ departamento.nombre
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

        departamento = departamentos.objects.get(nombre=request.POST.get('departamento'))

        request.session['agenteEncuesta'] = agente
        request.session['ventanillaEncuesta'] = numeroVentanilla
        request.session['departamentoEncuesta'] = departamento.siglasDepartamento
        
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
    codigodepartamento = request.POST.get('codigoDepartamento')
    siglasdepartamento = request.POST.get('siglasDepartamento')

    data_agente = {
        'nombre': nombredepartamento,
        'codigoDepartamento': codigodepartamento,
        'siglasDepartamento': siglasdepartamento,
        'tramitesDepartamento': False
    }

    save = save_departamento(request, data_agente)
    return redirect(request.META.get('HTTP_REFERER'))

@login_required
def modificardepartamento(request):
    iddepartamento = request.POST.get('idDepartamento')
    nombredepartamento = request.POST.get('nombreDepartamento')
    codigodepartamento = request.POST.get('codigoDepartamento')
    siglasdepartamento = request.POST.get('siglasDepartamento')

    departamentoSelected = departamentos.objects.get(id_departamentos=iddepartamento)

    data = {
        'id_departamentos': iddepartamento,
        'nombre': nombredepartamento,
        'codigoDepartamento': codigodepartamento,
        'siglasDepartamento': siglasdepartamento,
        'tramitesDepartamento': departamentoSelected.tramites
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
        'codigoDepartamento': departamentoSelected.codigoDepartamento,
        'siglasDepartamento': departamentoSelected.siglasDepartamento,
        'tramitesDepartamento': True
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
    tramite = tramites.objects.all()
    return render(request, 'ticket/ticketmaker.html', {'departamentos': departamento, 'tramites': tramite})

def crear_ticket(request):
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
    idagente = request.POST.get('id_agente')
    save = delete_agente(request, idagente)
    return redirect(request.META.get('HTTP_REFERER'))

@login_required
def modificaragente(request):
    id_agente = request.POST.get('id_agente')
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