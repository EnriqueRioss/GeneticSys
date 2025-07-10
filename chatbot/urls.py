# chatbot/urls.py

from django.urls import path
from . import views

app_name = 'chatbot'

urlpatterns = [
    # URL para procesar los mensajes del chat.
    # Cuando se haga una petición POST a /api/chat/, se ejecutará la vista 'chat_api'.
    path('api/chat/', views.chat_api, name='chat_api'),

    # URL para obtener los recordatorios del usuario.
    # Cuando se haga una petición GET a /api/reminders/, se ejecutará la vista 'reminders_api'.
    #path('api/reminders/', views.reminders_api, name='reminders_api'),
]