from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q
from .models import ChatGroup, Message
from .serializers import ChatGroupSerializer, MessageSerializer

class DirectMessageAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, recipient_id):
        messages = Message.objects.filter(
            Q(sender=request.user, recipient_id=recipient_id) |
            Q(sender_id=recipient_id, recipient=request.user)
        ).order_by('timestamp')
        serializer = MessageSerializer(messages, many=True)
        return Response(serializer.data)

    def post(self, request, recipient_id):
        serializer = MessageSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(sender=request.user, recipient_id=recipient_id)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class GroupMessageAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, group_id):
        messages = Message.objects.filter(group_id=group_id)
        serializer = MessageSerializer(messages, many=True)
        return Response(serializer.data)

    def post(self, request, group_id):
        group = ChatGroup.objects.get(id=group_id)
        if request.user not in group.members.all():
            return Response({"error": "Not a member of this group"}, status=status.HTTP_403_FORBIDDEN)
        
        serializer = MessageSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(sender=request.user, group_id=group_id)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ChatGroupAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        groups = ChatGroup.objects.filter(members=request.user)
        serializer = ChatGroupSerializer(groups, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = ChatGroupSerializer(data=request.data)
        if serializer.is_valid():
            group = serializer.save(admin=request.user)
            group.members.add(request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class GroupManagementAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request, group_id):
        group = ChatGroup.objects.get(id=group_id)
        if request.user != group.admin:
            return Response({"error": "Only admin can modify group"}, status=status.HTTP_403_FORBIDDEN)
        
        serializer = ChatGroupSerializer(group, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, group_id):
        group = ChatGroup.objects.get(id=group_id)
        if request.user != group.admin:
            return Response({"error": "Only admin can delete group"}, status=status.HTTP_403_FORBIDDEN)
        group.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
