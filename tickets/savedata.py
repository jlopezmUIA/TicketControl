import json
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
import requests
from tickets.forms import FormularioAgente, FormularioAtencion, FormularioCasosAgente, FormularioCasosAgenteP, FormularioCitas, FormularioDepartamentos, FormularioEstadosAgente, FormularioMetricas, FormularioTicketControl, FormularioTickets, FormularioTiemposAgente, FormularioTramites
from .models import agentes, atencion, casosAgente, departamentos, estadosAgente, ticketControl, tickets, tiemposAgente, tramites, visualizador
from datetime import date

def save_configuration(request, visualizador_id, campo, nuevo_valor):
    visor = get_object_or_404(visualizador, pk=visualizador_id)
    setattr(visor, campo, nuevo_valor)
    visor.save()
    return True
 
def update_configuration(request, visualizador_id, campo, nuevo_valor, nombre_archivo):
    visor = get_object_or_404(visualizador, pk=visualizador_id)
    valor_actual = getattr(visor, campo)
    if valor_actual or valor_actual is None:
        setattr(visor, campo, nuevo_valor)
        setattr(visor, campo + '_nombre', nombre_archivo)  # Guardar el nombre del archivo
        visor.save()
        return True
    else:
        return False

def save_ticketcontrol(request, data):
    form = FormularioTicketControl(data)
    if form.is_valid():
        form.save()
        return True
    else:
        return False
     
def update_ticketcontrol(request, codigo, ventanilla, departamento):
    try:
        ticketcontrol = ticketControl.objects.get(codigoCaso=codigo)
        data_estados_agente = {
            'codigoCaso': codigo,  # Objeto de la instancia relacionada del modelo agentes
            'numeroVentanilla': ventanilla,
            'departamento': departamento,
        }
        form = FormularioTicketControl(data_estados_agente)
        if form.is_valid():
            form.save()
            return True
    except ticketControl.DoesNotExist:
        return False

    return False

def save_agente(request, data):
    form = FormularioAgente(data)
    if form.is_valid():
        form.save()
        return True
    else:
        return False
    
def delete_agente(request, agente_id):
    try:
        agente = agentes.objects.get(id_agente=agente_id)
        agente.delete()
        return True
    except agentes.DoesNotExist:
        return False

def save_atencion(request, data):
    form = FormularioAtencion(data)
    if form.is_valid():
        form.save()
        return True
    else:
        return False

def update_cola(request, agente_id, nueva_cola):
    try:
        atencion_obj = atencion.objects.get(agente=agente_id)
        atencion_obj.colaAtencion = nueva_cola
        atencion_obj.save()
        return True
    except atencion.DoesNotExist:
        return False
    
def update_estado(request, agente_id, estado_nuevo):
    try:
        atencion_obj = atencion.objects.get(agente=agente_id)
        atencion_obj.estadoAtencion = estado_nuevo
        atencion_obj.save()
        return True
    except atencion.DoesNotExist:
        return False

def save_metricas(request, data):
    form = FormularioMetricas(data)
    if form.is_valid():
        form.save()
        return True
    else:
        return False

def save_estados_agente(request, data):
    form = FormularioEstadosAgente(data)
    if form.is_valid():
        estado_agente = form.save() 
        return estado_agente 
    else:
        return None 

def eliminar_atencion(id_agente):
    try:
        atencion_obj = atencion.objects.get(agente_id=id_agente)
        atencion_obj.delete()
        return True
    except atencion.DoesNotExist:
        return False

def update_estados_agente(request, id_estado, tiempo):
    try:
        estado_agente = estadosAgente.objects.get(pk=id_estado)
        data_estados_agente = {
            'agente': request.session.get('id_agente'),  # Objeto de la instancia relacionada del modelo agentes
            'estado': estado_agente.estado,
            'fecha': estado_agente.fecha,
            'tiempoInicio': estado_agente.tiempoInicio,  # Fecha en formato YYYY-MM-DD
            'tiempoFinal': tiempo  # Fecha en formato YYYY-MM-DD
        }
        form = FormularioEstadosAgente(data_estados_agente, instance=estado_agente)
        if form.is_valid():
            form.save()
            return True
    except estadosAgente.DoesNotExist:
        return False

    return False

def save_casos_agente(request, data):
    form = FormularioCasosAgenteP(data)
    if form.is_valid():
        caso_agente = form.save() 
        return caso_agente 
    else:
        return None 

def update_casos_agente(request, id_caso, accion):
    try:
        casos_agente = casosAgente.objects.get(pk=id_caso)
        if accion == "caso":
            cantAten = casos_agente.cantidadAtendidos
            cantAten+=1
            cantTrans = casos_agente.cantidadTransferidos
        elif accion == "transferencia":
            cantTrans = casos_agente.cantidadTransferidos
            cantTrans+=1
            cantAten = casos_agente.cantidadAtendidos
    
        data_estados_agente = {
            'agente': request.session.get('id_agente'),  # Objeto de la instancia relacionada del modelo agentes
            'cantidadAtendidos': cantAten,
            'cantidadTransferidos': cantTrans,
            'fecha': casos_agente.fecha,  # Fecha en formato YYYY-MM-DD
        }
        form = FormularioCasosAgente(data_estados_agente, instance=casos_agente)
        if form.is_valid():
            form.save()
            return True
    except estadosAgente.DoesNotExist:
        return False

    return False

def save_tiempos_agente(request, data):
    form = FormularioTiemposAgente(data)
    if form.is_valid():
        tiempo_agente = form.save() 
        return tiempo_agente 
    else:
        return False

def update_tiempos_agente(request, id_tiempo, tiempo):
    try:
        tiempo_agente = tiemposAgente.objects.get(pk=id_tiempo)
        data_estados_agente = {
            'agente': request.session.get('id_agente'),  # Objeto de la instancia relacionada del modelo agentes
            'codigoCaso': tiempo_agente.codigoCaso,
            'fecha': tiempo_agente.fecha,
            'tiempoInicio': tiempo_agente.tiempoInicio,  # Fecha en formato YYYY-MM-DD
            'tiempoFinal': tiempo  # Fecha en formato YYYY-MM-DD
        }
        form = FormularioTiemposAgente(data_estados_agente, instance=tiempo_agente)
        if form.is_valid():
            form.save()
            return True
    except estadosAgente.DoesNotExist:
        return False

    return False

def obtener_caso(id):
    fecha_actual = date.today().strftime('%Y-%m-%d')
    try:
        atencion_obj = casosAgente.objects.filter(agente=id, fecha = fecha_actual).first()
        if atencion_obj is not None:
            casoid = atencion_obj.id_casoagente
            return casoid
        else:
            return False
    except casosAgente.DoesNotExist:
        return False
 
def obtener_cola(id):
    try:
        atencion_obj = atencion.objects.get(agente=id)
        cola = atencion_obj.colaAtencion
        return cola
    except atencion.DoesNotExist:
        return None

def obtener_ventanilla(id):
    try:
        atencion_obj = atencion.objects.get(agente=id)
        ventanilla = atencion_obj.numeroVentanilla
        return ventanilla
    except atencion.DoesNotExist:
        return None
    
def obtener_agenteAtencion(id):
    try:
        atencion_obj = atencion.objects.get(agente=id)
        ventanilla = atencion_obj.numeroVentanilla
        return ventanilla
    except atencion.DoesNotExist:
        return None

def obtener_departamento(id):
    try:
        atencion_obj = agentes.objects.get(id_agente=id)
        departamento = departamentos.objects.get(nombre=atencion_obj.departamento)
        return departamento.siglasDepartamento
    except agentes.DoesNotExist:
        return None

def save_departamento(request, data):
    form = FormularioDepartamentos(data)
    if form.is_valid():
        form.save()
        return True
    else:
        return False
    
def update_departamento(request, data):
    try:
        atencion_obj = departamentos.objects.get(id_departamentos=data['id_departamentos'])
        if atencion_obj.nombre != data['nombre']:
            agentes_cambio = agentes.objects.filter(departamento=atencion_obj.nombre)
            agentes_cambio.update(departamento=data['nombre'])
            ticket = tickets.objects.filter(departamento=atencion_obj.nombre)
            ticket.update(departamento=data['nombre'])
        atencion_obj.nombre = data['nombre']
        atencion_obj.alias = data['alias']
        atencion_obj.codigoDepartamento = data['codigoDepartamento']
        atencion_obj.siglasDepartamento = data['siglasDepartamento']
        atencion_obj.tramitesDepartamento = data['tramitesDepartamento']
        atencion_obj.citasDepartamento = data['citasDepartamento']
        atencion_obj.save()
        return True
    except departamentos.DoesNotExist:
        return False
    
def eliminar_departamento(request, data):
    try:
        try:
            tickets_obj = tramites.objects.get(departamento=data['id_departamentos'])
            return False
        except tramites.DoesNotExist:
            atencion_obj = departamentos.objects.get(id_departamentos=data['id_departamentos'])
            atencion_obj.delete()
            return True
    except departamentos.DoesNotExist:
        return False

def save_tramite(request, data):
    form = FormularioTramites(data)
    if form.is_valid():
        form.save()
        return True
    else:
        return False
    
def save_ticket(request, data):
    form = FormularioTickets(data)
    if form.is_valid():
        form.save()
        return True
    else:
        return False

def save_tramite(request, data):
    form = FormularioTramites(data)
    if form.is_valid():
        form.save()
        return True
    else:
        return False
    
def update_tramite(request, data):
    try:
        atencion_obj = tramites.objects.get(id_tramites=data['id_tramites'])
        if atencion_obj.nombre != data['nombre']:
            ticket = tickets.objects.filter(tramite=atencion_obj.nombre)
            ticket.update(tramite=data['nombre'])
        atencion_obj.nombre = data['nombre']
        atencion_obj.codigoTramite = data['codigoTramite']
        atencion_obj.save()
        return True
    except tramites.DoesNotExist:
        return False

def eliminar_tramite(request, data):
    try:
        atencion_obj = tramites.objects.get(id_tramites=data['id_tramites'])
        depart = atencion_obj.departamento
        atencion_obj.delete()

        deparTramite = tramites.objects.filter(departamento=depart).count()
        if deparTramite == 0:
            mod = departamentos.objects.get(nombre=depart.nombre)
            mod.tramitesDepartamento = False
            mod.save()
        return True
    except tramites.DoesNotExist:
        return False
    
def save_ticket(request, data):
    form = FormularioTickets(data)
    if form.is_valid():
        form.save()
        return True
    else:
        return False
    
def obtener_primero_dato(departamentoNombre, tramiteNombre):
    try:
        fecha_actual = date.today().strftime('%Y-%m-%d')
        if tramiteNombre == 'N/A':
            ultimo_dato = tickets.objects.filter(atendido=False, fecha=fecha_actual, departamento=departamentoNombre).earliest('id_ticket')
            return ultimo_dato
        else:
            tramiteNombre = tramiteNombre.split(",")
            ultimo_dato = None

            for tramite in tramiteNombre:
                ticket = tickets.objects.filter(atendido=False, fecha=fecha_actual, departamento=departamentoNombre, tramite=tramite)
                if ticket.exists():
                    ultimo_registro = ticket.earliest('id_ticket')
                    if ultimo_dato is None or ultimo_registro.fecha > ultimo_dato.fecha:
                        ultimo_dato = ultimo_registro
            if ultimo_dato is None:
                dato = tickets(codigo = '000')
                return dato
            else:
                return ultimo_dato
    except tickets.DoesNotExist:
        dato = tickets(codigo = '000')
        return dato

def obtener_ultimo_dato(departamentoNombre, tramiteNombre):
    try:
        fecha_actual = date.today().strftime('%Y-%m-%d')
        if tramiteNombre == 'N/A':
            ultimo_dato = tickets.objects.filter(fecha=fecha_actual, departamento=departamentoNombre).latest('id_ticket')
        else:
            ultimo_dato = tickets.objects.filter(fecha=fecha_actual, departamento=departamentoNombre, tramite=tramiteNombre).latest('id_ticket')

        pr = ultimo_dato.codigo.split('-')
        if pr[1] == "999":
            return "PR-000"
        else:
            return ultimo_dato.codigo
    except tickets.DoesNotExist:
        return "PR-000"

def marcar_ticket(id):
    try:
        fecha_actual = date.today().strftime('%Y-%m-%d')
        admision_obj = tickets.objects.get(pk=id, fecha=fecha_actual)
        admision_obj.atendido = True
        admision_obj.save()
        return True
    except tickets.DoesNotExist:
        return False 

def update_agente(request, data):
    try:
        atencion_obj = agentes.objects.get(id_agente=data['id_agente'])
        atencion_obj.nombreAgente = data['nombreAgente']
        atencion_obj.departamento = data['departamento']
        atencion_obj.save()
        return True
    except agentes.DoesNotExist:
        return False
    
def obtener_datos(request):
    id = request.GET.get("identificacion")
    if len(id) == 9:
        url = 'https://api.hacienda.go.cr/fe/ae?identificacion=' + id
        response = requests.get(url)
        data_usuario = json.loads(response.text)
        if response.status_code != 404 and response.status_code != 500:
            data_nombre = data_usuario["nombre"]
        else:
            data_nombre = None
        if data_nombre is not None:
            data = [data_nombre]
            status2 = 200
        else:
            data = []
            status2 = 404

    elif len(id) >= 10 and len(id) <= 12:
        url = 'https://api.hacienda.go.cr/fe/ae?identificacion=' + id
        response = requests.get(url)

        data_usuario = json.loads(response.text)
        if response.status_code != 404 and response.status_code != 500:
            data_nombre = data_usuario["nombre"]
        else:
            data_nombre = None
        if data_nombre is not None:
            data = [data_nombre]
            status2 = 200
        else:
            data = []
            status2 = 404
    else:
        data = []
        status2 = 404

    data_completa = json.dumps(data)
    return JsonResponse(data_completa, safe=False, status=status2)

def save_cita(request, data):
    form = FormularioCitas(data)
    if form.is_valid():
        form.save()
        return True
    else:
        return False



