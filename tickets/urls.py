from django.urls import path
from .views import (
    home,
    registroAgente,
    ticket_maker,
    obtener_agentes,
    inicio_atencion,
    atencion_agentes,
    estados_reporte,
    numero_agente,
    transferencia,
    ticketcontrol,
    adminside,
    cambiar_link_text,
    ticketsagente,
    datosagente,
    cambiar_imagen,
    casosagente,
    cambiar_cola,
    cambiar_visual,
    nuevoagente,
    colasatencion,
    configuracion,
    reproductor,
    estadosagente,
    ticketcontrolEncuesta,
    inicio_encuesta,
    registroEncuesta,
    metricas_guardado,
    digital_ticket_maker,
    digital_crear_ticket,
    numero_agente_cita,
    
    Logueo,
    RegistroAdmin,

    nuevodepartamento,
    modificardepartamento,
    eliminardepartamento,
    obtener_departamentos,

    nuevotramite,
    modificartramite,
    eliminartramite,

    crear_ticket,
    cargar_tramites,

    obtener_todos_departamentos,
    eliminaragente,
    modificaragente,

    control_citas,
    control_citas_callcenter,

    actualizar_tabla,

    nuevacita,
    nuevacitaagente,
    obtener_departamentos_cita,
    actualizar_tabla_departamentos,
    actualizar_tabla_departamentos_control,
    actualizar_tabla_citas_actuales,
    actualizar_tabla_citas,
    crear_ticket_cita,

    terminar_ticket,
    terminar_ticket_varios,
    siguiente_ticket,
    no_presente,
    llamar_ticket,

    modificarcita,
    eliminarcita,
    
    ticket_encuesta,
    reproductor_cliente,
    
    recepcion,
    ventanillas_disponibles,
    nueva_ley7600,
    eliminar_ley7600,
    crear_ticket_ley,
    
    error_500,
    error_404,
    
    eliminaragentecita,
    nuevoagentecita,
)

from .savedata import obtener_datos, procesador_datos_crm
from django.contrib.auth.views import LogoutView

# Create your models here.
urlpatterns = [
    path('', home, name='home'),
    path('login/', Logueo.as_view(), name='login'),
    path('registro-admin/', RegistroAdmin.as_view(), name='registro_admin'),
    path('logout/', LogoutView.as_view(next_page='login'), name='logout'),
    path('admin-side/', adminside, name='admin_side'),
    path('reproductor/', reproductor, name='reproductor'),
    path('reproductor-cliente/', reproductor_cliente, name='reproductor_cliente'),
    path('cambiar-link-text/', cambiar_link_text, name='cambiar_link_text'),
    path('cambiar-imagen/', cambiar_imagen, name='cambiar_imagen'),
    path('cambiar-visual/', cambiar_visual, name='cambiar_visual'),
    path('nuevo-agente/', nuevoagente, name='nuevo_agente'),
    path('configuracion/', configuracion, name='configuracion'),
    path('cambiar-cola/', cambiar_cola, name='cambiar_cola'),
    path('colas-atencion/', colasatencion, name='colas_atencion'),
    path('estados_agente/', estadosagente, name='estados_agente'),
    path('casos-agente/', casosagente, name='casos_agente'),
    path('tickets-agente/', ticketsagente, name='tickets_agente'),
    path('datos-agente/', datosagente, name='datos_agente'),
    path('registro-agente/', registroAgente, name='registro_agente'),
    path('obtener-agentes/', obtener_agentes, name='obtener_agentes'),
    
    path('numero-agente/', numero_agente, name='numero_agente'),
    path('numero-agente-cita/', numero_agente_cita, name='numero_agente_cita'),
    
    path('ticket-maker/', ticket_maker, name='ticket_maker'),
    path('ticket-control/', ticketcontrol, name='ticket_control'),
    path('transferencia/', transferencia, name='transferencia'),
    path('atencion-agentes/', atencion_agentes, name='atencion_agentes'),
    path('inicio-atencion/', inicio_atencion, name='inicio_atencion'),
    path('estados-reporte/', estados_reporte, name='estados_reporte'),

    path('ticket-control-encuesta/', ticketcontrolEncuesta, name='ticket_control_encuesta'),
    path('registro-encuesta/', registroEncuesta, name='registro_encuesta'),
    path('inicio-encuesta/', inicio_encuesta, name='inicio_encuesta'),
    path('metricas/', metricas_guardado, name='metricas'),

    path('digital-ticket-maker/', digital_ticket_maker, name='digital_ticket_maker'),
    path('digital-crear-ticket/', digital_crear_ticket, name='digital_crear_ticket'),


    path('nuevo-departamento/', nuevodepartamento, name='nuevo_departamento'),
    path('modificar-departamento/', modificardepartamento, name='modificar_departamento'),
    path('eliminar-departamento/', eliminardepartamento, name='eliminar_departamento'),
    path('obtener-departamentos/', obtener_departamentos, name='obtener_departamentos'),

    path('nuevo-tramite/', nuevotramite, name='nuevo_tramite'),
    path('modificar-tramite/', modificartramite, name='modificar_tramite'),
    path('eliminar-tramite/', eliminartramite, name='eliminar_tramite'),

    path('crear-ticket/', crear_ticket, name='crear_ticket'),
    path('cargar-tramites/', cargar_tramites, name='cargar_tramites'),

    path('obtener-todos-departamentos/', obtener_todos_departamentos, name='obtener_todos_departamentos'),
    path('eliminar-agente/', eliminaragente, name='eliminar_agente'),
    path('modificar-agente/', modificaragente, name='modificar_agente'),
    
    path('eliminar-agente-cita/', eliminaragentecita, name='eliminar_agente_cita'),
    path('nuevo-agente-cita/', nuevoagentecita, name='nuevo_agente_cita'),

    path('obtener-datos/', obtener_datos, name='obtener_datos'),
    path('control-citas/', control_citas, name='control_citas'),
    path('control-citas-callcenter/', control_citas_callcenter, name='control_citas_callcenter'),

    path('actualizar-tabla/', actualizar_tabla, name='actualizar_tabla'),

    path('nueva-cita/', nuevacita, name='nueva_cita'),
    path('nueva-cita-agente/', nuevacitaagente, name='nueva_cita_agente'),
    path('obtener-departamentos-cita/', obtener_departamentos_cita, name='obtener_departamentos_cita'),
    path('actualizar-tabla-departamentos/', actualizar_tabla_departamentos, name='actualizar_tabla_departamentos'),
    path('actualizar-tabla-departamentos-control/', actualizar_tabla_departamentos_control, name='actualizar_tabla_departamentos_control'),
    path('actualizar-tabla-citas-actuales/', actualizar_tabla_citas_actuales, name='actualizar_tabla_citas_actuales'),
    path('actualizar-tabla-citas/', actualizar_tabla_citas, name='actualizar_tabla_citas'),
    path('crear-ticket-cita/', crear_ticket_cita, name='crear_ticket_cita'),

    path('terminar-ticket/', terminar_ticket, name='terminar_ticket'),
    path('terminar-ticket-varios/', terminar_ticket_varios, name='terminar_ticket_varios'),
    path('siguiente-ticket/', siguiente_ticket, name='siguiente_ticket'),
    path('no-presente/', no_presente, name='no_presente'),
    path('llamar-ticket/', llamar_ticket, name='llamar_ticket'),

    path('modificar-cita/', modificarcita, name='modificar_cita'),
    path('eliminar-cita/', eliminarcita, name='eliminar_cita'),
    
    path('ticket-encuesta/', ticket_encuesta, name='ticket_encuesta'),
    
    path('recepcion/', recepcion, name='recepcion'),
    
    path('ventanillas-disponibles/', ventanillas_disponibles, name='ventanillas_disponibles'),
    
    path('nueva-ley/', nueva_ley7600, name='nueva_ley'),
    path('eliminar-ley/', eliminar_ley7600, name='eliminar_ley'),
    path('crear-ticket-ley/', crear_ticket_ley, name='crear_ticket_ley'),
    
    path('500/', error_500, name='error_500'),
    path('404/', error_404, name='error_404'),
    
    path('procesador-datos-crm/', procesador_datos_crm, name='procesador_datos_crm'),
]