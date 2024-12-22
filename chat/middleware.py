from channels.db import database_sync_to_async
from django.contrib.auth.models import AnonymousUser
from rest_framework_simplejwt.tokens import UntypedToken
from rest_framework.exceptions import AuthenticationFailed
from django.contrib.auth import get_user_model
import jwt
from django.conf import settings

User = get_user_model()

class JWTAuthMiddleware:
    """
    Custom middleware for JWT authentication in Django Channels.
    """
    def __init__(self, inner):
        self.inner = inner

    async def __call__(self, scope, receive, send):
        # Add user to the scope
        scope['user'] = await self.authenticate(scope)
        return await self.inner(scope, receive, send)

    @database_sync_to_async
    def authenticate(self, scope):
        """
        Authenticate the user based on the JWT token provided in the query string.
        """
        headers = dict(scope.get("headers", []))
        raw_token = None

        # Extract the token from headers or query string
        if b'authorization' in headers:
            auth_header = headers[b'authorization'].decode('utf8')
            prefix, raw_token = auth_header.split()
            if prefix.lower() != "bearer":
                return AnonymousUser()
        elif 'token' in scope.get('query_string', b'').decode():
            query_string = scope['query_string'].decode()
            raw_token = query_string.split('token=')[-1]

        if not raw_token:
            return AnonymousUser()

        try:
            # Validate token and fetch user
            UntypedToken(raw_token)  # Verifies the token signature
            decoded_data = jwt.decode(raw_token, settings.SECRET_KEY, algorithms=["HS256"])
            user_id = decoded_data.get("user_id")
            return User.objects.get(id=user_id)
        except (AuthenticationFailed, jwt.ExpiredSignatureError, jwt.DecodeError, User.DoesNotExist):
            return AnonymousUser()
