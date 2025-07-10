"""
URL configuration for djangomain project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include  # Asegúrate de que 'include' esté importado

# Importaciones para servir archivos estáticos y de medios en modo de desarrollo
from django.conf import settings
from django.conf.urls.static import static

# --- LISTA PRINCIPAL DE RUTAS URL ---
# Django lee esta lista de arriba a abajo para encontrar una coincidencia.

urlpatterns = [
    # 1. Ruta para el panel de administración nativo de Django.
    #    Ej: http://127.0.0.1:8000/admin/
    path('admin/', admin.site.urls),

    # 2. Rutas para la API de nuestro nuevo chatbot.
    #    Esto le dice a Django que cualquier URL que llegue,
    #    se la pase al archivo 'chatbot/urls.py' para que él decida qué hacer.
    #    Ej: /api/chat/ será manejado por chatbot.urls
    path('', include('chatbot.urls')),

    # 3. Rutas para tu aplicación principal de genética.
    #    IMPORTANTE: Esta debe ser la ÚLTIMA en la lista de 'includes' principales
    #    si usa un patrón de ruta vacío (''), para que no "capture" las URLs
    #    de la API del chatbot antes de tiempo.
    #    Ej: /pacientes/, /historias/crear, etc., serán manejados por myapp.urls
    path('', include('myapp.urls')),  # Reemplaza 'myapp' por el nombre de tu app si es diferente.
]

# --- CONFIGURACIÓN PARA DESARROLLO ---
# Este bloque es crucial para que Django pueda mostrar las imágenes y otros
# archivos que subes (como las fotos de los pacientes) cuando estás en modo DEBUG.
# En producción, el servidor web (como Nginx o Apache) se encarga de esto.
if settings.DEBUG:
    # Añade las rutas para los archivos de medios (MEDIA_URL y MEDIA_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    # Django ya maneja los archivos estáticos (STATIC_URL) automáticamente en DEBUG.