from django import forms
from .models import agentes, atencion, admisiones, cajas, cursoslibres, registro, estadosAgente, casosAgente, ticketControl, tiemposAgente

class FormularioAgente(forms.ModelForm):
    class Meta:
        model = agentes
        fields = ('departamento', 'nombreAgente')

class FormularioAtencion(forms.ModelForm):
    class Meta:
        model = atencion
        fields = ('agente', 'numeroVentanilla', 'colaAtencion', 'estadoAtencion')

class FormularioAdmisiones(forms.ModelForm):
    class Meta:
        model = admisiones
        fields = ('codigo', 'departamento', 'fecha', 'atendido')

class FormularioCajas(forms.ModelForm):
    class Meta:
        model = cajas
        fields = ('codigo', 'departamento', 'fecha', 'atendido')

class FormularioCursosLibres(forms.ModelForm):
    class Meta:
        model = cursoslibres
        fields = ('codigo', 'departamento', 'fecha', 'atendido')

class FormularioRegistro(forms.ModelForm):
    class Meta:
        model = registro
        fields = ('codigo', 'departamento', 'fecha', 'atendido')

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
