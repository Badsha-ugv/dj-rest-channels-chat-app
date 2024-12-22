from django.urls import path
from .views import (
    DirectMessageAPIView,
    GroupMessageAPIView,
    ChatGroupAPIView,
    GroupManagementAPIView
)

urlpatterns = [
    path('messages/direct/<int:recipient_id>/', DirectMessageAPIView.as_view(), name='direct-messages'),
    path('messages/group/<int:group_id>/', GroupMessageAPIView.as_view(), name='group-messages'),
    path('groups/', ChatGroupAPIView.as_view(), name='chat-groups'),
    path('groups/<int:group_id>/', GroupManagementAPIView.as_view(), name='group-management'),
]