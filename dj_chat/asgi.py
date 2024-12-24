

import os
import django
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from chat.routing import websocket_urlpatterns
from chat.middleware import JWTAuthMiddleware

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dj_chat.settings')
django.setup()

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    # "websocket": JWTAuthMiddleware(  # Use your custom middleware here
    #     URLRouter(websocket_urlpatterns)
    # ),
})
