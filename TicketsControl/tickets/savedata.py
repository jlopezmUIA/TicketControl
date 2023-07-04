from django.shortcuts import get_object_or_404
from tickets.forms import FormularioAdmisiones, FormularioAgente, FormularioAtencion, FormularioCajas, FormularioCasosAgente, FormularioCasosAgenteP, FormularioCursosLibres, FormularioDepartamentos, FormularioEstadosAgente, FormularioMetricas, FormularioRegistro, FormularioTicketControl, FormularioTickets, FormularioTiemposAgente, FormularioTramites
from .models import admisiones, agentes, atencion, cajas, casosAgente, cursoslibres, departamentos, estadosAgente, registro, ticketControl, tickets, tiemposAgente, tramites, visualizador
from datetime import datetime
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

def save_admisiones(request, data):
    form = FormularioAdmisiones(data)
    if form.is_valid():
        form.save()
        return True
    else:
        return False

def save_cajas(request, data):
    form = FormularioCajas(data)
    if form.is_valid():
        form.save()
        return True
    else:
        return False

def save_cursoslibres(request, data):
    form = FormularioCursosLibres(data)
    if form.is_valid():
        form.save()
        return True
    else:
        return False

def save_registro(request, data):
    form = FormularioRegistro(data)
    if form.is_valid():
        form.save()
        return True
    else:
        return False

def marcar_admision(id):
    try:
        fecha_actual = date.today().strftime('%Y-%m-%d')
        admision_obj = admisiones.objects.get(pk=id, fecha=fecha_actual)
        admision_obj.atendido = True
        admision_obj.save()
        return True
    except admisiones.DoesNotExist:
        return False
    
def marcar_cajas(id):
    try:
        fecha_actual = date.today().strftime('%Y-%m-%d')
        cajas_obj = cajas.objects.get(pk=id, fecha=fecha_actual)
        cajas_obj.atendido = True
        cajas_obj.save()
        return True
    except cajas.DoesNotExist:
        return False
    
def marcar_cursoslibres(id):
    try:
        fecha_actual = date.today().strftime('%Y-%m-%d')
        cursoslibres_obj = cursoslibres.objects.get(pk=id, fecha=fecha_actual)
        cursoslibres_obj.atendido = True
        cursoslibres_obj.save()
        return True
    except cursoslibres.DoesNotExist:
        return False
    
def marcar_registro(id):
    try:
        fecha_actual = date.today().strftime('%Y-%m-%d')
        registro_obj = registro.objects.get(pk=id, fecha=fecha_actual)
        registro_obj.atendido = True
        registro_obj.save()
        return True
    except registro.DoesNotExist:
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

def obtener_ultimo_dato_admisiones():
    try:
        fecha_actual = date.today().strftime('%Y-%m-%d')
        ultimo_dato = admisiones.objects.filter(fecha=fecha_actual).latest('id_admision')
        pr = ultimo_dato.codigo.split('-')
        if pr[1] == "999":
            return "PR-000"
        else:
            return ultimo_dato.codigo
    except admisiones.DoesNotExist:
        return "PR-000"

def obtener_ultimo_dato_cajas():
    try:
        fecha_actual = date.today().strftime('%Y-%m-%d')
        ultimo_dato = cajas.objects.filter(fecha=fecha_actual).latest('id_cajas')
        pr = ultimo_dato.codigo.split('-')
        if pr[1] == "999":
            return "PR-000"
        else:
            return ultimo_dato.codigo
    except cajas.DoesNotExist:
        return "PR-000"

def obtener_ultimo_dato_cursoslibres():
    try:
        fecha_actual = date.today().strftime('%Y-%m-%d')
        ultimo_dato = cursoslibres.objects.filter(fecha=fecha_actual).latest('id_cursolibres')
        pr = ultimo_dato.codigo.split('-')
        if pr[1] == "999":
            return "PR-000"
        else:
            return ultimo_dato.codigo
    except cursoslibres.DoesNotExist:
        return "PR-000"

def obtener_ultimo_dato_registro():
    try:
        fecha_actual = date.today().strftime('%Y-%m-%d')
        ultimo_dato = registro.objects.filter(fecha=fecha_actual).latest('id_registro')
        pr = ultimo_dato.codigo.split('-')
        if pr[1] == "999":
            return "PR-000"
        else:
            return ultimo_dato.codigo
    except registro.DoesNotExist:
        return "PR-000"
    
def obtener_primero_dato_admisiones():
    try:
        fecha_actual = date.today().strftime('%Y-%m-%d')
        ultimo_dato = admisiones.objects.filter(atendido=False, fecha=fecha_actual).earliest('id_admision')
        return ultimo_dato
    except admisiones.DoesNotExist:
        dato = admisiones(codigo = '000')
        return dato

def obtener_primero_dato_cajas():
    try:
        fecha_actual = date.today().strftime('%Y-%m-%d')
        ultimo_dato = cajas.objects.filter(atendido=False, fecha=fecha_actual).earliest('id_cajas')
        return ultimo_dato
    except cajas.DoesNotExist:
        dato = cajas(codigo = '000')
        return dato

def obtener_primero_dato_cursoslibres():
    try:
        fecha_actual = date.today().strftime('%Y-%m-%d')
        ultimo_dato = cursoslibres.objects.filter(atendido=False, fecha=fecha_actual).earliest('id_cursolibres')
        return ultimo_dato
    except cursoslibres.DoesNotExist:
        dato = cursoslibres(codigo = '000')
        return dato

def obtener_primero_dato_registro(cola):
    try:
        colas = cola.split(",")
        fecha_actual = date.today().strftime('%Y-%m-%d')
        # ultimo_dato = registro.objects.filter(atendido=False, fecha=fecha_actual, departamento=cola).earliest('id_registro')
        ultimo_dato = None

        for cola in colas:
            registros = registro.objects.filter(atendido=False, fecha=fecha_actual, departamento=cola)
            if registros.exists():
                ultimo_registro = registros.latest('id_registro')
                if ultimo_dato is None or ultimo_registro.fecha > ultimo_dato.fecha:
                    ultimo_dato = ultimo_registro
        if ultimo_dato is None:
            dato = registro(codigo = '000')
            return dato
        else:
            return ultimo_dato
    except registro.DoesNotExist:
        dato = registro(codigo = '000')
        return dato
 
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
        atencion_obj.nombre = data['nombre']
        atencion_obj.codigoDepartamento = data['codigoDepartamento']
        atencion_obj.siglasDepartamento = data['siglasDepartamento']
        atencion_obj.tramitesDepartamento = data['tramitesDepartamento']
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
        atencion_obj.nombre = data['nombre']
        atencion_obj.codigoTramite = data['codigoTramite']
        atencion_obj.save()
        return True
    except tramites.DoesNotExist:
        return False

def eliminar_tramite(request, data):
    try:
        atencion_obj = tramites.objects.get(id_tramites=data['id_tramites'])
        atencion_obj.delete()
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
    
