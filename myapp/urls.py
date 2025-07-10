from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from . import views

urlpatterns = [
    path('', views.index_view, name="index"),
    path('about/', views.about, name="about"),
    path('hello/<str:username>/', views.hello, name="hello_user"),
    path('projects/', views.projects, name="project_list"),
    path('projects/create/', views.create_project, name="project_create"),
    path('projects/<int:id>/', views.project_detail, name="project_detail"),
    path('tasks/', views.tasks, name="task_list"),
    path('tasks/create/', views.create_task, name="task_create"),

    path('signup/', views.signup, name="signup"),
    path('login/', views.login_medico, name="login"),
    path('logout/', views.signout, name="logout"),

    # Role-specific "Pacientes" list access points
    path('gestion/pacientes/', views.gestion_pacientes_view, name='gestion_pacientes'),
    #path('pacientes/admin/', views.gestion_pacientes_view, name="pacientes_admin_list"),
    #path('pacientes/genetista/', views.pacientes_genetista_view, name="pacientes_genetista_list"),
    #path('pacientes/lector/<int:genetista_id>/', views.pacientes_lector_view, name="pacientes_lector_list"),
    # Redirector for the generic "Pacientes" sidebar link
    path('pacientes/', views.pacientes_redirect_view, name="pacientes_list_redirect"),
    path('historias/delete/<int:historia_id>/', views.delete_historia, name='historia_delete'),

    path('historias/crear/', views.crear_editar_historia, name="historia_crear"),
     path('historias/<int:historia_id>/pdf/', views.generar_pdf_historia, name='historia_pdf'),
path('historias/<int:historia_id>/editar/', views.crear_editar_historia, name="historia_editar"),
    path('historias/<int:historia_id>/paciente/crear/', views.crear_paciente, name="paciente_crear"),
    path('historias/<int:historia_id>/pareja/crear/', views.crear_pareja, name="pareja_crear"),
    path('historias/<int:historia_id>/proposito/<int:proposito_id>/padres/', views.padres_proposito, name="padres_proposito_crear"),
    path('historias/<int:historia_id>/<str:tipo>/<int:objeto_id>/antecedentes-personales/', 
         views.crear_antecedentes_personales, name="antecedentes_personales_crear"),
    path('historias/<int:historia_id>/<str:tipo>/<int:objeto_id>/antecedentes-preconcepcionales/', 
         views.crear_antecedentes_preconcepcionales, name="antecedentes_preconcepcionales_crear"),
    path('propositos/<int:proposito_id>/examen-fisico/', views.crear_examen_fisico, name='examen_fisico_crear_editar'),
    path('propositos/<int:proposito_id>/', views.ver_proposito, name='proposito_detalle'), 
    path('historias/<int:historia_id>/<str:tipo>/<int:objeto_id>/evaluacion-genetica/', 
         views.diagnosticos_plan_estudio, name='evaluacion_genetica_crear_editar'),
         path('historias/<int:historia_id>/<str:tipo>/<int:objeto_id>/autorizaciones/',
         views.autorizaciones_view, name='autorizaciones_crear'),

     path('evaluacion/<int:evaluacion_id>/nueva-consulta/', 
         views.nueva_consulta_view, name='nueva_consulta'),

     path('ajax/historia-details/<int:historia_id>/', views.get_historia_details_ajax, name='ajax_get_historia_details'),



    path('ajax/buscar-propositos/', views.buscar_propositos, name='ajax_buscar_propositos'), 
path('ajax/get-historia-clinica/<int:proposito_id>/', views.get_historia_clinica_data, name='ajax_get_historia_clinica'),
    path('ajax/edit-plan-estudio/<int:plan_id>/', views.edit_plan_estudio, name='ajax_edit_plan_estudio'),
    path('reports/', views.reports_view, name="reports_dashboard"),
    path('ver_historias/', views.ver_historias, name="ver_historias"),
    path('autorizaciones/', views.autorizaciones_view, name="autorizaciones"),
    path('reports/export/<str:export_format>/', views.export_report_data, name='export_report_data'),
    path('gestion/usuarios/', views.gestion_usuarios_view, name='gestion_usuarios'),
    path('gestion/usuarios/toggle-status/<int:user_id>/', views.toggle_user_active_status, name='toggle_user_active'),
   # path('gestion/usuarios/delete/<int:user_id>/', views.delete_user_admin, name='delete_user_admin'),
   #path('pacientes/inactivar/', views.inactivar_pacientes_view, name='pacientes_inactivar'), 
path('gestion/usuarios/reset-password/<int:user_id>/', views.reset_password_admin, name='reset_password_admin'),
path('gestion/usuarios/edit/<int:user_id>/', views.edit_user_admin, name='edit_user_admin'), 
 path('ajax/evaluacion/<int:evaluacion_id>/guardar-diagnostico-final/', views.guardar_diagnostico_final_ajax, name='ajax_guardar_diagnostico_final'),


path('historias/archive/<int:historia_id>/', views.archive_historia, name='historia_archive'),
    path('historias/unarchive/<int:historia_id>/', views.unarchive_historia, name='historia_unarchive'),
]


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)