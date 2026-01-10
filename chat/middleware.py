"""
Custom JWT authentication middleware for WebSocket connections
"""
from urllib.parse import parse_qs
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser
from channels.db import database_sync_to_async
from channels.middleware import BaseMiddleware
from rest_framework_simplejwt.tokens import AccessToken
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError

User = get_user_model()


@database_sync_to_async
def get_user_from_token(token_string):
    """Get user from JWT token"""
    try:
        access_token = AccessToken(token_string)
        user_id = access_token['user_id']
        user = User.objects.get(id=user_id)
        return user
    except (TokenError, InvalidToken, User.DoesNotExist):
        return AnonymousUser()


class JWTAuthMiddleware(BaseMiddleware):
    """
    Custom middleware to authenticate WebSocket connections using JWT tokens.
    
    Supports authentication via:
    1. Query parameter: ?token=<jwt_token>
    2. Subprotocol: (not implemented, but can be added)
    """

    async def __call__(self, scope, receive, send):
        # Extract token from query string
        query_string = scope.get('query_string', b'').decode()
        query_params = parse_qs(query_string)
        token = None

        # Try to get token from query params
        if 'token' in query_params:
            token = query_params['token'][0]
        elif 'access_token' in query_params:
            token = query_params['access_token'][0]

        # Authenticate user
        if token:
            scope['user'] = await get_user_from_token(token)
        else:
            scope['user'] = AnonymousUser()

        return await super().__call__(scope, receive, send)


def JWTAuthMiddlewareStack(inner):
    """Stack JWT auth middleware"""
    return JWTAuthMiddleware(inner)

