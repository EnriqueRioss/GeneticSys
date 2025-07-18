# Generated by Django 5.1.6 on 2025-07-12 06:12

import django.db.models.deletion
import myapp.models
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='EvaluacionGenetica',
            fields=[
                ('evaluacion_id', models.AutoField(primary_key=True, serialize=False)),
                ('signos_clinicos', models.TextField(blank=True, help_text='Describa los signos clínicos más relevantes que inician esta evaluación.', null=True, verbose_name='Signos Clínicos Relevantes')),
                ('fecha_creacion', models.DateTimeField(auto_now_add=True)),
                ('diagnostico_final', models.TextField(blank=True, help_text='El diagnóstico definitivo o las conclusiones finales de la evaluación.', null=True, verbose_name='Diagnóstico Final y Conclusiones')),
            ],
            options={
                'verbose_name': 'Evaluación Genética',
                'verbose_name_plural': 'Evaluaciones Genéticas',
            },
        ),
        migrations.CreateModel(
            name='Parejas',
            fields=[
                ('pareja_id', models.AutoField(primary_key=True, serialize=False)),
            ],
        ),
        migrations.CreateModel(
            name='Project',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200)),
            ],
        ),
        migrations.CreateModel(
            name='DiagnosticoPresuntivo',
            fields=[
                ('diagnostico_id', models.AutoField(primary_key=True, serialize=False)),
                ('descripcion', models.TextField(help_text='Ingrese un diagnóstico presuntivo', verbose_name='Diagnóstico Presuntivo')),
                ('orden', models.PositiveIntegerField(default=0, help_text='Orden de importancia (0=más probable, 1=segundo, etc.)')),
                ('evaluacion', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='diagnosticos_presuntivos', to='myapp.evaluaciongenetica')),
            ],
            options={
                'verbose_name': 'Diagnóstico Presuntivo',
                'verbose_name_plural': 'Diagnósticos Presuntivos',
                'ordering': ['orden'],
            },
        ),
        migrations.CreateModel(
            name='Genetistas',
            fields=[
                ('genetista_id', models.AutoField(primary_key=True, serialize=False)),
                ('rol', models.CharField(choices=[('GEN', 'Genetista'), ('ADM', 'Administrador'), ('LEC', 'Lector')], default='GEN', max_length=3, verbose_name='Rol del Usuario')),
                ('associated_genetista', models.ForeignKey(blank=True, help_text="Si el rol es Lector, genetista (con rol 'Genetista') al que está asociado.", null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='lectores_asociados', to='myapp.genetistas')),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='genetistas', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='HistoriasClinicas',
            fields=[
                ('motivo_archivado', models.TextField(blank=True, null=True, verbose_name='Motivo de Archivado')),
                ('estado_previo_archivado', models.CharField(blank=True, choices=[('borrador', 'Borrador'), ('finalizada', 'Finalizada')], max_length=20, null=True, verbose_name='Estado Previo al Archivado')),
                ('fecha_ultima_modificacion', models.DateTimeField(blank=True, null=True, verbose_name='Última Modificación')),
                ('historia_id', models.AutoField(primary_key=True, serialize=False)),
                ('numero_historia', models.IntegerField(unique=True)),
                ('fecha_ingreso', models.DateTimeField(auto_now_add=True)),
                ('motivo_tipo_consulta', models.CharField(choices=[('Pareja-Asesoramiento Prenupcial', 'Pareja-Asesoramiento Prenupcial'), ('Pareja-Preconcepcional', 'Pareja-Preconcepcional'), ('Pareja-Prenatal', 'Pareja-Prenatal'), ('Proposito-Diagnóstico', 'Proposito-Diagnóstico')], max_length=35)),
                ('cursante_postgrado', models.CharField(blank=True, max_length=100, null=True)),
                ('centro_referencia', models.CharField(blank=True, max_length=100, null=True)),
                ('medico', models.CharField(blank=True, max_length=100, null=True)),
                ('especialidad', models.CharField(blank=True, max_length=100, null=True)),
                ('estado', models.CharField(choices=[('borrador', 'Borrador'), ('finalizada', 'Finalizada'), ('archivada', 'Archivada')], default='borrador', max_length=20, verbose_name='Estado de la Historia')),
                ('genetista', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='myapp.genetistas')),
            ],
        ),
        migrations.CreateModel(
            name='HistorialCambios',
            fields=[
                ('cambio_id', models.AutoField(primary_key=True, serialize=False)),
                ('fecha_cambio', models.DateTimeField(auto_now_add=True)),
                ('descripcion_cambio', models.TextField(blank=True, null=True)),
                ('historia', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='myapp.historiasclinicas')),
            ],
        ),
        migrations.AddField(
            model_name='evaluaciongenetica',
            name='pareja',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='myapp.parejas'),
        ),
        migrations.CreateModel(
            name='PlanEstudio',
            fields=[
                ('plan_id', models.AutoField(primary_key=True, serialize=False)),
                ('accion', models.TextField(help_text='Describa el plan de estudio, exámenes o pasos a seguir para la próxima consulta.', verbose_name='Acción a realizar / Exámenes solicitados')),
                ('completado', models.BooleanField(default=False, verbose_name='Plan Completado')),
                ('fecha_visita', models.DateField(blank=True, null=True, verbose_name='Fecha de Próxima Visita / Límite')),
                ('asesoramiento_evoluciones', models.TextField(blank=True, help_text='Llenar este campo cuando el paciente regrese y el plan se marque como completado.', null=True, verbose_name='Asesoramiento y Evoluciones (Resultados de la consulta)')),
                ('evaluacion', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='planes_estudio', to='myapp.evaluaciongenetica')),
            ],
            options={
                'verbose_name': 'Plan de Estudio / Consulta',
                'verbose_name_plural': 'Planes de Estudio / Consultas',
                'ordering': ['-fecha_visita', '-plan_id'],
            },
        ),
        migrations.CreateModel(
            name='ArchivoPlanEstudio',
            fields=[
                ('archivo_id', models.AutoField(primary_key=True, serialize=False)),
                ('archivo', models.FileField(upload_to=myapp.models.get_upload_path, verbose_name='Archivo Adjunto')),
                ('nombre_descriptivo', models.CharField(blank=True, help_text="Nombre corto para mostrar en la UI (ej: 'Ecocardiograma'). Si se deja en blanco, se usará el nombre del archivo.", max_length=150, null=True)),
                ('fecha_subida', models.DateTimeField(auto_now_add=True)),
                ('plan_estudio', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='archivos', to='myapp.planestudio')),
            ],
        ),
        migrations.CreateModel(
            name='Propositos',
            fields=[
                ('proposito_id', models.AutoField(primary_key=True, serialize=False)),
                ('nombres', models.CharField(max_length=100)),
                ('apellidos', models.CharField(max_length=100)),
                ('sexo', models.CharField(choices=[('M', 'Masculino'), ('F', 'Femenino')], max_length=1, verbose_name='Sexo')),
                ('lugar_nacimiento', models.CharField(max_length=100)),
                ('fecha_nacimiento', models.DateField()),
                ('escolaridad', models.CharField(max_length=100)),
                ('ocupacion', models.CharField(max_length=100)),
                ('edad', models.IntegerField(blank=True, editable=False, null=True)),
                ('identificacion', models.CharField(max_length=20, unique=True)),
                ('direccion', models.CharField(max_length=200)),
                ('telefono', models.CharField(max_length=15)),
                ('email', models.EmailField(blank=True, max_length=100, null=True)),
                ('grupo_sanguineo', models.CharField(choices=[('A', 'A'), ('B', 'B'), ('AB', 'AB'), ('O', 'O')], max_length=2)),
                ('factor_rh', models.CharField(choices=[('Positivo', 'Positivo'), ('Negativo', 'Negativo')], max_length=10)),
                ('foto', models.ImageField(blank=True, null=True, upload_to='propositos_fotos/')),
                ('estado', models.CharField(choices=[('en_seguimiento', 'En Seguimiento'), ('cerrado', 'Cerrado'), ('inactivo', 'Inactivo')], default='en_seguimiento', max_length=20, verbose_name='Estado del Propósito')),
                ('historia', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='myapp.historiasclinicas')),
            ],
        ),
        migrations.AddField(
            model_name='parejas',
            name='proposito_id_1',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='parejas_como_1', to='myapp.propositos'),
        ),
        migrations.AddField(
            model_name='parejas',
            name='proposito_id_2',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='parejas_como_2', to='myapp.propositos'),
        ),
        migrations.CreateModel(
            name='InformacionPadres',
            fields=[
                ('padre_id', models.AutoField(primary_key=True, serialize=False)),
                ('tipo', models.CharField(choices=[('Padre', 'Padre'), ('Madre', 'Madre')], max_length=10)),
                ('escolaridad', models.CharField(max_length=100)),
                ('ocupacion', models.CharField(max_length=100)),
                ('nombres', models.CharField(max_length=100)),
                ('apellidos', models.CharField(max_length=100)),
                ('lugar_nacimiento', models.CharField(max_length=100)),
                ('fecha_nacimiento', models.DateField()),
                ('edad', models.IntegerField(blank=True, editable=False, null=True)),
                ('identificacion', models.CharField(max_length=20, unique=True)),
                ('grupo_sanguineo', models.CharField(choices=[('A', 'A'), ('B', 'B'), ('AB', 'AB'), ('O', 'O')], max_length=2)),
                ('factor_rh', models.CharField(choices=[('Positivo', 'Positivo'), ('Negativo', 'Negativo')], max_length=10)),
                ('telefono', models.CharField(max_length=15)),
                ('email', models.EmailField(blank=True, max_length=100, null=True)),
                ('direccion', models.CharField(max_length=200)),
                ('proposito', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='myapp.propositos')),
            ],
        ),
        migrations.CreateModel(
            name='Genealogia',
            fields=[
                ('genealogia_id', models.AutoField(primary_key=True, serialize=False)),
                ('tipo_familiar', models.CharField(choices=[('proposito', 'Propósito'), ('pareja', 'Pareja'), ('padre', 'Padre'), ('madre', 'Madre'), ('abuelo_paterno', 'Abuelo Paterno'), ('abuela_paterna', 'Abuela Paterna'), ('abuelo_materno', 'Abuelo Materno'), ('abuela_materna', 'Abuela Materna'), ('hermano', 'Hermano/a'), ('hijo', 'Hijo/a')], max_length=20)),
                ('nombres', models.CharField(max_length=100)),
                ('apellidos', models.CharField(max_length=100)),
                ('fecha_nacimiento', models.DateField(blank=True, null=True)),
                ('fecha_fallecimiento', models.DateField(blank=True, null=True)),
                ('estado_salud', models.TextField(blank=True, null=True)),
                ('notas', models.TextField(blank=True, null=True)),
                ('consanguinidad', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='myapp.genealogia')),
                ('pareja', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='genealogia_pareja', to='myapp.parejas')),
                ('proposito', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='genealogia_proposito', to='myapp.propositos')),
            ],
        ),
        migrations.CreateModel(
            name='ExamenFisico',
            fields=[
                ('examen_id', models.AutoField(primary_key=True, serialize=False)),
                ('fecha_examen', models.DateField(auto_now_add=True)),
                ('medida_abrazada', models.DecimalField(blank=True, decimal_places=2, max_digits=5, null=True)),
                ('segmento_inferior', models.DecimalField(blank=True, decimal_places=2, max_digits=5, null=True)),
                ('segmento_superior', models.DecimalField(blank=True, decimal_places=2, max_digits=5, null=True)),
                ('circunferencia_cefalica', models.DecimalField(blank=True, decimal_places=2, max_digits=5, null=True)),
                ('talla', models.DecimalField(blank=True, decimal_places=2, max_digits=5, null=True)),
                ('distancia_intermamilar', models.DecimalField(blank=True, decimal_places=2, max_digits=5, null=True)),
                ('distancia_interc_interna', models.DecimalField(blank=True, decimal_places=2, max_digits=5, null=True)),
                ('distancia_interpupilar', models.DecimalField(blank=True, decimal_places=2, max_digits=5, null=True)),
                ('longitud_mano_derecha', models.DecimalField(blank=True, decimal_places=2, max_digits=5, null=True)),
                ('longitud_mano_izquierda', models.DecimalField(blank=True, decimal_places=2, max_digits=5, null=True)),
                ('peso', models.DecimalField(blank=True, decimal_places=2, max_digits=5, null=True)),
                ('ss_si', models.DecimalField(blank=True, decimal_places=2, max_digits=5, null=True)),
                ('distancia_interc_externa', models.DecimalField(blank=True, decimal_places=2, max_digits=5, null=True)),
                ('ct', models.DecimalField(blank=True, decimal_places=2, max_digits=5, null=True)),
                ('pabellones_auriculares', models.DecimalField(blank=True, decimal_places=2, max_digits=5, null=True)),
                ('tension_arterial_sistolica', models.DecimalField(blank=True, decimal_places=2, max_digits=5, null=True)),
                ('tension_arterial_diastolica', models.DecimalField(blank=True, decimal_places=2, max_digits=5, null=True)),
                ('observaciones_cabeza', models.TextField(blank=True, null=True)),
                ('observaciones_cuello', models.TextField(blank=True, null=True)),
                ('observaciones_torax', models.TextField(blank=True, null=True)),
                ('observaciones_abdomen', models.TextField(blank=True, null=True)),
                ('observaciones_genitales', models.TextField(blank=True, null=True)),
                ('observaciones_espalda', models.TextField(blank=True, null=True)),
                ('observaciones_miembros_superiores', models.TextField(blank=True, null=True)),
                ('observaciones_miembros_inferiores', models.TextField(blank=True, null=True)),
                ('observaciones_piel', models.TextField(blank=True, null=True)),
                ('observaciones_osteomioarticular', models.TextField(blank=True, null=True)),
                ('observaciones_neurologico', models.TextField(blank=True, null=True)),
                ('observaciones_pliegues', models.TextField(blank=True, null=True)),
                ('proposito', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='myapp.propositos', unique=True)),
            ],
        ),
        migrations.CreateModel(
            name='EvolucionDesarrollo',
            fields=[
                ('evolucion_id', models.AutoField(primary_key=True, serialize=False)),
                ('fecha', models.DateField(blank=True, null=True)),
                ('historial_enfermedades', models.TextField(blank=True, null=True)),
                ('hospitalizaciones', models.TextField(blank=True, null=True)),
                ('cirugias', models.TextField(blank=True, null=True)),
                ('convulsiones', models.TextField(blank=True, null=True)),
                ('otros_antecedentes', models.TextField(blank=True, null=True)),
                ('resultados_examenes', models.FileField(blank=True, null=True, upload_to='')),
                ('proposito', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='myapp.propositos')),
            ],
        ),
        migrations.AddField(
            model_name='evaluaciongenetica',
            name='proposito',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='myapp.propositos'),
        ),
        migrations.CreateModel(
            name='DesarrolloPsicomotor',
            fields=[
                ('desarrollo_id', models.AutoField(primary_key=True, serialize=False)),
                ('sostener_cabeza', models.CharField(blank=True, max_length=100, null=True)),
                ('sonrisa_social', models.CharField(blank=True, max_length=100, null=True)),
                ('sentarse', models.CharField(blank=True, max_length=100, null=True)),
                ('gatear', models.CharField(blank=True, max_length=100, null=True)),
                ('pararse', models.CharField(blank=True, max_length=100, null=True)),
                ('caminar', models.CharField(blank=True, max_length=100, null=True)),
                ('primeras_palabras', models.CharField(blank=True, max_length=100, null=True)),
                ('primeros_dientes', models.CharField(blank=True, max_length=100, null=True)),
                ('progreso_escuela', models.CharField(blank=True, max_length=100, null=True)),
                ('progreso_peso', models.CharField(blank=True, max_length=100, null=True)),
                ('progreso_talla', models.CharField(blank=True, max_length=100, null=True)),
                ('pareja', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='myapp.parejas')),
                ('proposito', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='myapp.propositos')),
            ],
        ),
        migrations.CreateModel(
            name='Autorizaciones',
            fields=[
                ('autorizacion_id', models.AutoField(primary_key=True, serialize=False)),
                ('autorizacion_examenes', models.BooleanField(default=False, verbose_name='¿Autoriza la realización de exámenes genéticos?')),
                ('archivo_autorizacion', models.FileField(blank=True, null=True, upload_to='autorizaciones/', verbose_name='Archivo de Autorización Firmado')),
                ('fecha_autorizacion', models.DateTimeField(auto_now_add=True)),
                ('representante_padre', models.ForeignKey(blank=True, help_text='El padre/madre que autoriza, solo si el propósito es menor de edad.', null=True, on_delete=django.db.models.deletion.SET_NULL, to='myapp.informacionpadres')),
                ('proposito', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='autorizacion', to='myapp.propositos')),
            ],
        ),
        migrations.CreateModel(
            name='AntecedentesPersonales',
            fields=[
                ('antecedente_id', models.AutoField(primary_key=True, serialize=False)),
                ('enfermedad_actual', models.TextField(blank=True, help_text='Descripción de la enfermedad actual, motivo de consulta y cronología.', null=True, verbose_name='Enfermedad Actual')),
                ('fur', models.DateField(blank=True, null=True)),
                ('edad_gestacional', models.IntegerField(blank=True, null=True)),
                ('controles_prenatales', models.CharField(blank=True, default='', max_length=100)),
                ('numero_partos', models.IntegerField(blank=True, null=True)),
                ('numero_gestas', models.IntegerField(blank=True, null=True)),
                ('numero_cesareas', models.IntegerField(blank=True, null=True)),
                ('numero_abortos', models.IntegerField(blank=True, null=True)),
                ('numero_mortinatos', models.IntegerField(blank=True, null=True)),
                ('numero_malformaciones', models.IntegerField(blank=True, null=True)),
                ('complicaciones_embarazo', models.TextField(blank=True, null=True)),
                ('exposicion_teratogenos', models.CharField(blank=True, choices=[('Físicos', 'Físicos'), ('Químicos', 'Químicos'), ('Biológicos', 'Biológicos')], max_length=20, null=True)),
                ('descripcion_exposicion', models.TextField(blank=True, null=True)),
                ('enfermedades_maternas', models.TextField(blank=True, null=True)),
                ('complicaciones_parto', models.TextField(blank=True, null=True)),
                ('otros_antecedentes', models.TextField(blank=True, null=True)),
                ('observaciones', models.TextField(blank=True, null=True)),
                ('pareja', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='myapp.parejas')),
                ('proposito', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='myapp.propositos')),
            ],
        ),
        migrations.CreateModel(
            name='AntecedentesFamiliaresPreconcepcionales',
            fields=[
                ('antecedente_familiar_id', models.AutoField(primary_key=True, serialize=False)),
                ('antecedentes_padre', models.TextField(blank=True, null=True)),
                ('antecedentes_madre', models.TextField(blank=True, null=True)),
                ('estado_salud_padre', models.TextField(blank=True, null=True)),
                ('estado_salud_madre', models.TextField(blank=True, null=True)),
                ('fecha_union_pareja', models.DateField(blank=True, null=True)),
                ('consanguinidad', models.CharField(blank=True, choices=[('Sí', 'Sí'), ('No', 'No')], max_length=2, null=True)),
                ('grado_consanguinidad', models.CharField(blank=True, max_length=50, null=True)),
                ('pareja', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='myapp.parejas')),
                ('proposito', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='myapp.propositos')),
            ],
        ),
        migrations.CreateModel(
            name='Task',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=200)),
                ('description', models.TextField()),
                ('done', models.BooleanField(default=False)),
                ('project', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='myapp.project')),
            ],
        ),
        migrations.CreateModel(
            name='PeriodoNeonatal',
            fields=[
                ('neonatal_id', models.AutoField(primary_key=True, serialize=False)),
                ('peso_nacer', models.DecimalField(blank=True, decimal_places=2, max_digits=5, null=True)),
                ('talla_nacer', models.DecimalField(blank=True, decimal_places=2, max_digits=5, null=True)),
                ('circunferencia_cefalica', models.DecimalField(blank=True, decimal_places=2, max_digits=5, null=True)),
                ('cianosis', models.CharField(blank=True, max_length=100, null=True)),
                ('ictericia', models.CharField(blank=True, max_length=100, null=True)),
                ('hemorragia', models.CharField(blank=True, max_length=100, null=True)),
                ('infecciones', models.CharField(blank=True, max_length=100, null=True)),
                ('convulsiones', models.CharField(blank=True, max_length=100, null=True)),
                ('vomitos', models.CharField(blank=True, max_length=100, null=True)),
                ('observacion_complicaciones', models.TextField(blank=True, null=True)),
                ('otros_complicaciones', models.TextField(blank=True, null=True)),
                ('tipo_alimentacion', models.CharField(blank=True, choices=[('Lactancia Materna', 'Lactancia Materna'), ('Artificial', 'Artificial'), ('Mixta', 'Mixta')], max_length=20, null=True)),
                ('observaciones_alimentacion', models.TextField(blank=True, null=True)),
                ('evolucion', models.TextField(blank=True, null=True)),
                ('observaciones_habitos_psicologicos', models.TextField(blank=True, null=True)),
                ('pareja', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='myapp.parejas')),
                ('proposito', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='myapp.propositos')),
            ],
            options={
                'constraints': [models.CheckConstraint(condition=models.Q(models.Q(('pareja__isnull', True), ('proposito__isnull', False)), models.Q(('pareja__isnull', False), ('proposito__isnull', True)), _connector='OR'), name='check_periodo_proposito_or_pareja'), models.UniqueConstraint(condition=models.Q(('proposito__isnull', False)), fields=('proposito',), name='unique_periodo_proposito'), models.UniqueConstraint(condition=models.Q(('pareja__isnull', False)), fields=('pareja',), name='unique_periodo_pareja')],
            },
        ),
        migrations.AlterUniqueTogether(
            name='parejas',
            unique_together={('proposito_id_1', 'proposito_id_2')},
        ),
        migrations.AddConstraint(
            model_name='informacionpadres',
            constraint=models.UniqueConstraint(fields=('proposito', 'tipo'), name='unique_tipo_por_proposito'),
        ),
        migrations.AddConstraint(
            model_name='informacionpadres',
            constraint=models.CheckConstraint(condition=models.Q(('tipo__in', ['Padre', 'Madre'])), name='tipo_valido'),
        ),
        migrations.AddConstraint(
            model_name='genealogia',
            constraint=models.CheckConstraint(condition=models.Q(models.Q(('pareja__isnull', True), ('proposito__isnull', False)), models.Q(('pareja__isnull', False), ('proposito__isnull', True)), _connector='OR'), name='genealogia_proposito_or_pareja'),
        ),
        migrations.AddConstraint(
            model_name='evaluaciongenetica',
            constraint=models.UniqueConstraint(condition=models.Q(('proposito__isnull', False)), fields=('proposito',), name='unique_evaluacion_proposito'),
        ),
        migrations.AddConstraint(
            model_name='evaluaciongenetica',
            constraint=models.UniqueConstraint(condition=models.Q(('pareja__isnull', False)), fields=('pareja',), name='unique_evaluacion_pareja'),
        ),
        migrations.AddConstraint(
            model_name='desarrollopsicomotor',
            constraint=models.CheckConstraint(condition=models.Q(models.Q(('pareja__isnull', True), ('proposito__isnull', False)), models.Q(('pareja__isnull', False), ('proposito__isnull', True)), _connector='OR'), name='check_desarrollo_proposito_or_pareja'),
        ),
        migrations.AddConstraint(
            model_name='desarrollopsicomotor',
            constraint=models.UniqueConstraint(condition=models.Q(('proposito__isnull', False)), fields=('proposito',), name='unique_desarrollo_proposito'),
        ),
        migrations.AddConstraint(
            model_name='desarrollopsicomotor',
            constraint=models.UniqueConstraint(condition=models.Q(('pareja__isnull', False)), fields=('pareja',), name='unique_desarrollo_pareja'),
        ),
        migrations.AddConstraint(
            model_name='antecedentespersonales',
            constraint=models.CheckConstraint(condition=models.Q(models.Q(('pareja__isnull', True), ('proposito__isnull', False)), models.Q(('pareja__isnull', False), ('proposito__isnull', True)), _connector='OR'), name='check_proposito_or_pareja_personales'),
        ),
        migrations.AddConstraint(
            model_name='antecedentespersonales',
            constraint=models.UniqueConstraint(condition=models.Q(('proposito__isnull', False)), fields=('proposito',), name='unique_antecedente_personal_proposito'),
        ),
        migrations.AddConstraint(
            model_name='antecedentespersonales',
            constraint=models.UniqueConstraint(condition=models.Q(('pareja__isnull', False)), fields=('pareja',), name='unique_antecedente_personal_pareja'),
        ),
        migrations.AddConstraint(
            model_name='antecedentesfamiliarespreconcepcionales',
            constraint=models.CheckConstraint(condition=models.Q(models.Q(('pareja__isnull', True), ('proposito__isnull', False)), models.Q(('pareja__isnull', False), ('proposito__isnull', True)), _connector='OR'), name='check_proposito_or_pareja_familiares'),
        ),
        migrations.AddConstraint(
            model_name='antecedentesfamiliarespreconcepcionales',
            constraint=models.UniqueConstraint(condition=models.Q(('proposito__isnull', False)), fields=('proposito',), name='unique_antecedente_familiar_proposito'),
        ),
        migrations.AddConstraint(
            model_name='antecedentesfamiliarespreconcepcionales',
            constraint=models.UniqueConstraint(condition=models.Q(('pareja__isnull', False)), fields=('pareja',), name='unique_antecedente_familiar_pareja'),
        ),
    ]
