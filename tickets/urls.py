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

    actualizar_tabla,

    nuevacita,
    nuevacitaagente,
    obtener_departamentos_cita,
    actualizar_tabla_departamentos,
    actualizar_tabla_citas_actuales,
    actualizar_tabla_citas,
    crear_ticket_cita,

    terminar_ticket,
    siguiente_ticket,
)

from .savedata import obtener_datos
from django.contrib.auth.views import LogoutView

# Create your models here.
urlpatterns = [
    path('', home, name='home'),
    path('login/', Logueo.as_view(), name='login'),
    path('registro-admin/', RegistroAdmin.as_view(), name='registro_admin'),
    path('logout/', LogoutView.as_view(next_page='login'), name='logout'),
    path('admin-side/', adminside, name='admin_side'),
    path('reproductor/', reproductor, name='reproductor'),
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

    path('obtener-datos/', obtener_datos, name='obtener_datos'),
    path('control-citas/', control_citas, name='control_citas'),

    path('actualizar-tabla/', actualizar_tabla, name='actualizar_tabla'),

    path('nueva-cita/', nuevacita, name='nueva_cita'),
    path('nueva-cita-agente/', nuevacitaagente, name='nueva_cita_agente'),
    path('obtener-departamentos-cita/', obtener_departamentos_cita, name='obtener_departamentos_cita'),
    path('actualizar-tabla-departamentos/', actualizar_tabla_departamentos, name='actualizar_tabla_departamentos'),
    path('actualizar-tabla-citas-actuales/', actualizar_tabla_citas_actuales, name='actualizar_tabla_citas_actuales'),
    path('actualizar-tabla-citas/', actualizar_tabla_citas, name='actualizar_tabla_citas'),
    path('crear-ticket-cita/', crear_ticket_cita, name='crear_ticket_cita'),

    path('terminar-ticket/', terminar_ticket, name='terminar_ticket'),
    path('siguiente-ticket/', siguiente_ticket, name='siguiente_ticket'),
]