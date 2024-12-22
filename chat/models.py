from django.db import models
from django.contrib.auth.models import User

class ChatGroup(models.Model):
    name = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    admin = models.ForeignKey(User, on_delete=models.CASCADE, related_name='administered_groups')
    members = models.ManyToManyField(User, related_name='chat_groups')

    def __str__(self):
        return self.name

class Message(models.Model):
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages')
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)
    
    # For direct messages
    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_messages', null=True, blank=True)
    
    # For group messages
    group = models.ForeignKey(ChatGroup, on_delete=models.CASCADE, related_name='messages', null=True, blank=True)

    class Meta:
        ordering = ['timestamp']

    def __str__(self):
        return f'{self.sender} -> {self.recipient or self.group}: {self.content[:50]}'
