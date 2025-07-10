# chatbot/models.py
from django.db import models
from django.conf import settings # Para obtener el modelo de usuario de Django

class ChatInteraction(models.Model):
    interaction_id = models.AutoField(primary_key=True)
    # Relación con el modelo de usuario nativo de Django
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    user_query = models.TextField()
    bot_response = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Interaction with {self.user.username} at {self.timestamp}"

class Reminder(models.Model):
    reminder_id = models.AutoField(primary_key=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    message = models.TextField()
    due_date = models.DateTimeField(null=True, blank=True)
    is_completed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.message