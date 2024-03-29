from django.db import models

class agentes(models.Model):
    id_agente = models.AutoField(primary_key=True)
    departamento = models.CharField(max_length=60)
    nombreAgente = models.CharField(max_length=60)

class atencion(models.Model):
    id_atencion = models.AutoField(primary_key=True)
    agente = models.ForeignKey(agentes,
                            on_delete=models.CASCADE,
                            null=True,
                            blank=True)
    numeroVentanilla = models.CharField(max_length=60)
    colaAtencion = models.CharField(max_length=500)
    estadoAtencion = models.CharField(max_length=60)

class estadosAgente(models.Model):
    id_estado = models.AutoField(primary_key=True)
    agente = models.ForeignKey(agentes,
                            on_delete=models.CASCADE,
                            null=True,
                            blank=True)
    estado = models.CharField(max_length=60)
    fecha = models.CharField(max_length=60)
    tiempoInicio = models.CharField(max_length=60, null=True, blank=True)
    tiempoFinal = models.CharField(max_length=60, null=True, blank=True)

class casosAgente(models.Model):
    id_casoagente = models.AutoField(primary_key=True)
    agente = models.ForeignKey(agentes,
                            on_delete=models.CASCADE,
                            null=True,
                            blank=True)
    cantidadAtendidos = models.IntegerField(default=0)
    cantidadTransferidos = models.IntegerField(default=0)
    fecha = models.CharField(max_length=60, null=True, blank=True)

class tiemposAgente(models.Model):
    id_tiemposagente = models.AutoField(primary_key=True)
    agente = models.ForeignKey(agentes,
                            on_delete=models.CASCADE,
                            null=True,
                            blank=True)
    codigoCaso = models.CharField(max_length=60)
    fecha = models.CharField(max_length=60)
    tiempoInicio = models.CharField(max_length=60, null=True, blank=True)
    tiempoFinal = models.CharField(max_length=60, null=True, blank=True)

class ticketControl(models.Model):
    id_ticketcontrol = models.AutoField(primary_key=True)
    codigoCaso = models.CharField(max_length=60)
    numeroVentanilla = models.CharField(max_length=60)
    departamento = models.CharField(max_length=60)
    fecha = models.CharField(max_length=60)

class visualizador(models.Model):
    id_visualizador = models.AutoField(primary_key=True)
    tipo_visor = models.BooleanField(default=False)
    imagen1 = models.BinaryField(null=True, blank=True)
    imagen1_nombre = models.CharField(max_length=255, null=True, blank=True)
    imagen2 = models.BinaryField(null=True, blank=True)
    imagen2_nombre = models.CharField(max_length=255, null=True, blank=True)
    imagen3 = models.BinaryField(null=True, blank=True)
    imagen3_nombre = models.CharField(max_length=255, null=True, blank=True)
    imagen4 = models.BinaryField(null=True, blank=True)
    imagen4_nombre = models.CharField(max_length=255, null=True, blank=True)
    link = models.CharField(max_length=500, null=True, blank=True)
    text = models.CharField(max_length=500, null=True, blank=True)

class metricas(models.Model):
    id_metrica = models.AutoField(primary_key=True)
    agente = models.ForeignKey(agentes,
                            on_delete=models.CASCADE,
                            null=True,
                            blank=True)
    codigoCaso = models.CharField(max_length=60)
    estado = models.CharField(max_length=60)
    fecha = models.CharField(max_length=60)

class departamentos(models.Model):
    id_departamentos = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=60)
    alias = models.CharField(max_length=60)
    codigoDepartamento = models.CharField(max_length=60)
    siglasDepartamento = models.CharField(max_length=60)
    tramitesDepartamento = models.BooleanField(default=False)
    citasDepartamento = models.BooleanField(default=False)
    notiDepartamento = models.BooleanField(default=False)

class tramites(models.Model):  
    id_tramites = models.AutoField(primary_key=True)
    departamento = models.ForeignKey(departamentos,
                            on_delete=models.CASCADE,
                            null=True,
                            blank=True)
    nombre = models.CharField(max_length=60)
    codigoTramite = models.CharField(max_length=60)

class tickets(models.Model): 
    id_ticket = models.AutoField(primary_key=True)
    codigo = models.CharField(max_length=60)
    departamento = models.CharField(max_length=60)
    tramite = models.CharField(max_length=60)
    fecha = models.CharField(max_length=60)
    hora = models.CharField(max_length=60)
    atendido = models.BooleanField(default=False)
    estado = models.CharField(max_length=60)

class citas(models.Model): 
    id_citas = models.AutoField(primary_key=True)
    id_crm = models.CharField(max_length=60)
    codigo = models.CharField(max_length=60)
    departamento = models.CharField(max_length=60)
    nombreAgente = models.CharField(max_length=70)
    identificacion = models.CharField(max_length=60)
    nombreCliente = models.CharField(max_length=70)
    telefono = models.CharField(max_length=60)
    fecha = models.CharField(max_length=60)
    hora = models.CharField(max_length=60) 
    estado = models.CharField(max_length=255, null=True, blank=True)

class llamado(models.Model):
    id_llamado = models.AutoField(primary_key=True)
    texto = models.CharField(max_length=300)

class ley700(models.Model):
    id_ley = models.AutoField(primary_key=True)
    departamento = models.ForeignKey(departamentos,
                            on_delete=models.CASCADE,
                            null=True,
                            blank=True)
    ventanilla = models.CharField(max_length=60) 

class agentes_citas(models.Model):
    id_agente_cita = models.AutoField(primary_key=True)
    nombreAgente = models.CharField(max_length=60)