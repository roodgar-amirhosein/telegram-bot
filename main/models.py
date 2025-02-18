from django.db import models

class ChatMessage(models.Model):
    user_id = models.CharField(max_length=255)
    message = models.TextField()
    response = models.TextField()
    active_memory = models.BooleanField(default=True)
    timestamp = models.DateTimeField(auto_now_add=True)
