from django.contrib import admin
from .models import Project, Task, AntecedentesFamiliaresPreconcepcionales,Autorizaciones,AntecedentesPersonales,PeriodoNeonatal,Propositos,DesarrolloPsicomotor,InformacionPadres,EvolucionDesarrollo,Genealogia,Genetistas,HistorialCambios,HistoriasClinicas,Parejas,ExamenFisico,PlanEstudio,DiagnosticoPresuntivo,EvaluacionGenetica


# Readers
class Dateread(admin.ModelAdmin):
    readonly_fields =("fecha_ingreso", )
    
class Dateexamen(admin.ModelAdmin):
    readonly_fields =("fecha_examen" ,)
# Register your models here.
admin.site.register(AntecedentesFamiliaresPreconcepcionales)
admin.site.register(Autorizaciones)
admin.site.register(AntecedentesPersonales)
admin.site.register(PeriodoNeonatal)
admin.site.register(Propositos)
admin.site.register(DesarrolloPsicomotor)
admin.site.register(InformacionPadres)
class DiagnosticoPresuntivoInline(admin.TabularInline):
    model = DiagnosticoPresuntivo
    extra = 1 # Muestra un campo vacío para añadir uno nuevo.
    ordering = ('orden',)

class PlanEstudioInline(admin.StackedInline):
    model = PlanEstudio
    extra = 0 # No mostrar uno nuevo por defecto, ya que se crean con el tiempo.
    ordering = ('-fecha_visita', '-plan_id')

@admin.register(EvaluacionGenetica)
class EvaluacionGeneticaAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'proposito', 'pareja', 'fecha_creacion')
    inlines = [DiagnosticoPresuntivoInline, PlanEstudioInline]
    search_fields = ('proposito__nombres', 'proposito__apellidos', 'pareja__proposito_id_1__nombres')

admin.site.register(ExamenFisico,Dateexamen)
admin.site.register(EvolucionDesarrollo)
admin.site.register(Genealogia)
admin.site.register(Genetistas)
admin.site.register(HistorialCambios)
admin.site.register(HistoriasClinicas,Dateread)
admin.site.register(Project)
admin.site.register(Parejas)
admin.site.register(Task)