# Generated by Django 4.2.2 on 2023-07-04 15:26

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='agentes',
            fields=[
                ('id_agente', models.AutoField(primary_key=True, serialize=False)),
                ('departamento', models.CharField(max_length=60)),
                ('nombreAgente', models.CharField(max_length=60)),
            ],
        ),
        migrations.CreateModel(
            name='departamentos',
            fields=[
                ('id_departamentos', models.AutoField(primary_key=True, serialize=False)),
                ('nombre', models.CharField(max_length=60)),
                ('codigoDepartamento', models.CharField(max_length=60)),
                ('siglasDepartamento', models.CharField(max_length=60)),
                ('tramitesDepartamento', models.BooleanField(default=False)),
            ],
        ),
        migrations.CreateModel(
            name='ticketControl',
            fields=[
                ('id_ticketcontrol', models.AutoField(primary_key=True, serialize=False)),
                ('codigoCaso', models.CharField(max_length=60)),
                ('numeroVentanilla', models.CharField(max_length=60)),
                ('departamento', models.CharField(max_length=60)),
                ('fecha', models.CharField(max_length=60)),
            ],
        ),
        migrations.CreateModel(
            name='tickets',
            fields=[
                ('id_ticket', models.AutoField(primary_key=True, serialize=False)),
                ('codigo', models.CharField(max_length=60)),
                ('departamento', models.CharField(max_length=60)),
                ('tramite', models.CharField(max_length=60)),
                ('fecha', models.CharField(max_length=60)),
                ('atendido', models.BooleanField(default=False)),
            ],
        ),
        migrations.CreateModel(
            name='visualizador',
            fields=[
                ('id_visualizador', models.AutoField(primary_key=True, serialize=False)),
                ('tipo_visor', models.BooleanField(default=False)),
                ('imagen1', models.BinaryField(blank=True, null=True)),
                ('imagen1_nombre', models.CharField(blank=True, max_length=255, null=True)),
                ('imagen2', models.BinaryField(blank=True, null=True)),
                ('imagen2_nombre', models.CharField(blank=True, max_length=255, null=True)),
                ('imagen3', models.BinaryField(blank=True, null=True)),
                ('imagen3_nombre', models.CharField(blank=True, max_length=255, null=True)),
                ('imagen4', models.BinaryField(blank=True, null=True)),
                ('imagen4_nombre', models.CharField(blank=True, max_length=255, null=True)),
                ('link', models.CharField(blank=True, max_length=500, null=True)),
                ('text', models.CharField(blank=True, max_length=500, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='tramites',
            fields=[
                ('id_tramites', models.AutoField(primary_key=True, serialize=False)),
                ('nombre', models.CharField(max_length=60)),
                ('codigoTramite', models.CharField(max_length=60)),
                ('departamento', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='tickets.departamentos')),
            ],
        ),
        migrations.CreateModel(
            name='tiemposAgente',
            fields=[
                ('id_tiemposagente', models.AutoField(primary_key=True, serialize=False)),
                ('codigoCaso', models.CharField(max_length=60)),
                ('fecha', models.CharField(max_length=60)),
                ('tiempoInicio', models.CharField(blank=True, max_length=60, null=True)),
                ('tiempoFinal', models.CharField(blank=True, max_length=60, null=True)),
                ('agente', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='tickets.agentes')),
            ],
        ),
        migrations.CreateModel(
            name='metricas',
            fields=[
                ('id_metrica', models.AutoField(primary_key=True, serialize=False)),
                ('codigoCaso', models.CharField(max_length=60)),
                ('estado', models.CharField(max_length=60)),
                ('fecha', models.CharField(max_length=60)),
                ('agente', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='tickets.agentes')),
            ],
        ),
        migrations.CreateModel(
            name='estadosAgente',
            fields=[
                ('id_estado', models.AutoField(primary_key=True, serialize=False)),
                ('estado', models.CharField(max_length=60)),
                ('fecha', models.CharField(max_length=60)),
                ('tiempoInicio', models.CharField(blank=True, max_length=60, null=True)),
                ('tiempoFinal', models.CharField(blank=True, max_length=60, null=True)),
                ('agente', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='tickets.agentes')),
            ],
        ),
        migrations.CreateModel(
            name='casosAgente',
            fields=[
                ('id_casoagente', models.AutoField(primary_key=True, serialize=False)),
                ('cantidadAtendidos', models.IntegerField(default=0)),
                ('cantidadTransferidos', models.IntegerField(default=0)),
                ('fecha', models.CharField(blank=True, max_length=60, null=True)),
                ('agente', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='tickets.agentes')),
            ],
        ),
        migrations.CreateModel(
            name='atencion',
            fields=[
                ('id_atencion', models.AutoField(primary_key=True, serialize=False)),
                ('numeroVentanilla', models.CharField(max_length=60)),
                ('colaAtencion', models.CharField(max_length=500)),
                ('estadoAtencion', models.CharField(max_length=60)),
                ('agente', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='tickets.agentes')),
            ],
        ),
    ]
