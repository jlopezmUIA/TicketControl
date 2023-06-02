from django.shortcuts import get_object_or_404
from tickets.forms import FormularioAdmisiones, FormularioAgente, FormularioAtencion, FormularioCajas, FormularioCasosAgente, FormularioCasosAgenteP, FormularioCursosLibres, FormularioEstadosAgente, FormularioRegistro, FormularioTicketControl, FormularioTiemposAgente
from .models import admisiones, agentes, atencion, cajas, casosAgente, cursoslibres, estadosAgente, registro, ticketControl, tiemposAgente, visualizador
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

def marcar_admision(codigo):
    try:
        fecha_actual = date.today().strftime('%Y-%m-%d')
        admision_obj = admisiones.objects.get(codigo=codigo, fecha=fecha_actual)
        admision_obj.atendido = True
        admision_obj.save()
        return True
    except admisiones.DoesNotExist:
        return False
    
def marcar_cajas(codigo):
    try:
        fecha_actual = date.today().strftime('%Y-%m-%d')
        cajas_obj = cajas.objects.get(codigo=codigo, fecha=fecha_actual)
        cajas_obj.atendido = True
        cajas_obj.save()
        return True
    except cajas.DoesNotExist:
        return False
    
def marcar_cursoslibres(codigo):
    try:
        fecha_actual = date.today().strftime('%Y-%m-%d')
        cursoslibres_obj = cursoslibres.objects.get(codigo=codigo, fecha=fecha_actual)
        cursoslibres_obj.atendido = True
        cursoslibres_obj.save()
        return True
    except cursoslibres.DoesNotExist:
        return False
    
def marcar_registro(codigo):
    try:
        fecha_actual = date.today().strftime('%Y-%m-%d')
        registro_obj = registro.objects.get(codigo=codigo, fecha=fecha_actual)
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
        return ultimo_dato.codigo
    except admisiones.DoesNotExist:
        return "PR-000"

def obtener_ultimo_dato_cajas():
    try:
        fecha_actual = date.today().strftime('%Y-%m-%d')
        ultimo_dato = cajas.objects.filter(fecha=fecha_actual).latest('id_cajas')
        return ultimo_dato.codigo
    except cajas.DoesNotExist:
        return "PR-0000"

def obtener_ultimo_dato_cursoslibres():
    try:
        fecha_actual = date.today().strftime('%Y-%m-%d')
        ultimo_dato = cursoslibres.objects.filter(fecha=fecha_actual).latest('id_cursolibres')
        return ultimo_dato.codigo
    except cursoslibres.DoesNotExist:
        return "PR-0000"

def obtener_ultimo_dato_registro():
    try:
        fecha_actual = date.today().strftime('%Y-%m-%d')
        ultimo_dato = registro.objects.filter(fecha=fecha_actual).latest('id_registro')
        return ultimo_dato.codigo
    except registro.DoesNotExist:
        return "PR-0000"
    
def obtener_primero_dato_admisiones():
    try:
        fecha_actual = date.today().strftime('%Y-%m-%d')
        ultimo_dato = admisiones.objects.filter(atendido=False, fecha=fecha_actual).earliest('codigo')
        return ultimo_dato.codigo
    except admisiones.DoesNotExist:
        return "0000"

def obtener_primero_dato_cajas():
    try:
        fecha_actual = date.today().strftime('%Y-%m-%d')
        ultimo_dato = cajas.objects.filter(atendido=False, fecha=fecha_actual).earliest('id_cajas')
        return ultimo_dato.codigo
    except cajas.DoesNotExist:
        return "0000"

def obtener_primero_dato_cursoslibres():
    try:
        fecha_actual = date.today().strftime('%Y-%m-%d')
        ultimo_dato = cursoslibres.objects.filter(atendido=False, fecha=fecha_actual).earliest('id_cursolibres')
        return ultimo_dato.codigo
    except cursoslibres.DoesNotExist:
        return "0000"

def obtener_primero_dato_registro(cola):
    try:
        fecha_actual = date.today().strftime('%Y-%m-%d')
        ultimo_dato = registro.objects.filter(atendido=False, fecha=fecha_actual, departamento=cola).earliest('id_registro')
        return ultimo_dato.codigo
    except registro.DoesNotExist:
        return "0000"
 
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
        departamento = atencion_obj.departamento
        if departamento == "Admisiones":
            departamento = 'Adm'
        elif departamento == "Registro":
            departamento = 'Reg'
        elif departamento == "Cajas":
            departamento = 'Cja'
        elif departamento == "Cursos Libres":
            departamento = 'C.L.'
        return departamento
    except agentes.DoesNotExist:
        return None