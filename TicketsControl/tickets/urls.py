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
    eliminaragente,
    cambiar_cola,
    cambiar_visual,
    nuevoagente,
    colasatencion,
    configuracion,
    reproductor,
    estadosagente,
    crear_ticket_admision,
    crear_ticket_cajas,
    crear_ticket_cursolibre,
    crear_ticket_registro,
    crear_ticket_registro_tesis,
    crear_ticket_registro_convalidacion,
    crear_ticket_registro_retiros,
    crear_ticket_registro_suficiencia,
    crear_ticket_registro_graduacion,
    Logueo,
    RegistroAdmin,
)
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
    path('eliminar-agente/', eliminaragente, name='eliminar_agente'),
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
    path('crear-ticket-admision/', crear_ticket_admision, name='crear_ticket_admision'),
    path('crear-ticket-cajas/', crear_ticket_cajas, name='crear_ticket_cajas'),
    path('crear-ticket-cursolibre/', crear_ticket_cursolibre, name='crear_ticket_cursolibre'),
    path('crear-ticket-registro/', crear_ticket_registro, name='crear_ticket_registro'),
    path('crear-ticket-registro-tesis/', crear_ticket_registro_tesis, name='crear_ticket_registro_tesis'),
    path('crear-ticket-registro-convalidacion/', crear_ticket_registro_convalidacion, name='crear_ticket_registro_convalidacion'),
    path('crear-ticket-registro-retiros/', crear_ticket_registro_retiros, name='crear_ticket_registro_retiros'),
    path('crear-ticket-registro-suficiencia/', crear_ticket_registro_suficiencia, name='crear_ticket_registro_suficiencia'),
    path('crear-ticket-registro-graduacion/', crear_ticket_registro_graduacion, name='crear_ticket_registro_graduacion'),

]