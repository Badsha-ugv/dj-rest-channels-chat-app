from rest_framework import serializers
from .models import ChatGroup, Message
from django.contrib.auth.models import User

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email']

class ChatGroupSerializer(serializers.ModelSerializer):
    members = UserSerializer(many=True, read_only=True)
    admin = UserSerializer(read_only=True)

    class Meta:
        model = ChatGroup
        fields = ['id', 'name', 'created_at', 'admin', 'members']

class MessageSerializer(serializers.ModelSerializer):
    sender = UserSerializer(read_only=True)
    recipient = UserSerializer(read_only=True)
    group = ChatGroupSerializer(read_only=True)

    class Meta:
        model = Message
        fields = ['id', 'sender', 'recipient', 'group', 'content', 'timestamp', 'is_read']
