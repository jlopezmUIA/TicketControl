from django import forms

import tickets
from .models import agentes, agentes_citas, atencion, citas, departamentos, ley700, llamado, metricas, estadosAgente, casosAgente, ticketControl, tiemposAgente, tramites, tickets

class FormularioAgente(forms.ModelForm):
    class Meta:
        model = agentes
        fields = ('departamento', 'nombreAgente')

class FormularioAtencion(forms.ModelForm):
    class Meta:
        model = atencion
        fields = ('agente', 'numeroVentanilla', 'colaAtencion', 'estadoAtencion')

class FormularioEstadosAgente(forms.ModelForm):
    class Meta:
        model = estadosAgente
        fields = ('agente', 'estado', 'fecha', 'tiempoInicio', 'tiempoFinal')

class FormularioCasosAgenteP(forms.ModelForm):
    class Meta:
        model = casosAgente
        fields = ('agente', 'fecha')

class FormularioCasosAgente(forms.ModelForm):
    class Meta:
        model = casosAgente
        fields = ('agente', 'cantidadAtendidos', 'cantidadTransferidos', 'fecha')

class FormularioTiemposAgente(forms.ModelForm):
    class Meta:
        model = tiemposAgente
        fields = ('agente', 'codigoCaso', 'fecha', 'tiempoInicio', 'tiempoFinal')

class FormularioTicketControl(forms.ModelForm):
    class Meta:
        model = ticketControl
        fields = ('codigoCaso', 'numeroVentanilla', 'departamento', 'fecha')

class FormularioMetricas(forms.ModelForm):
    class Meta:
        model = metricas
        fields = ('agente', 'codigoCaso', 'estado', 'fecha')

class FormularioDepartamentos(forms.ModelForm):
    class Meta:
        model = departamentos
        fields = ('nombre', 'alias', 'codigoDepartamento', 'siglasDepartamento','tramitesDepartamento', 'citasDepartamento', 'notiDepartamento')

class FormularioTramites(forms.ModelForm):
    class Meta:
        model = tramites
        fields = ('departamento', 'nombre', 'codigoTramite')

class FormularioTickets(forms.ModelForm):
    class Meta:
        model = tickets
        fields = ('codigo', 'departamento', 'tramite', 'fecha', 'hora', 'atendido', 'estado')

class FormularioCitas(forms.ModelForm):
    class Meta:
        model = citas
        fields = ('id_crm', 'departamento', 'identificacion', 'nombreAgente', 'nombreCliente', 'telefono', 'fecha', 'hora', 'estado')
        
class FormularioLlamado(forms.ModelForm):
    class Meta:
        model = llamado
        fields = ('texto', )
        
class FormularioLey(forms.ModelForm):
    class Meta:
        model = ley700
        fields = ('departamento', 'ventanilla' )
        
class FormularioAgentesCitas(forms.ModelForm):
    class Meta:
        model = agentes_citas
        fields = ('nombreAgente', )