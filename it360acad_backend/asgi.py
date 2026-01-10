import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'it360acad_backend.settings')

# Initialize Django ASGI application early to ensure the AppRegistry
# is populated before importing code that may import ORM models.
django_asgi_app = get_asgi_application()

# Import routing and middleware after Django is initialized
import chat.routing
from chat.middleware import JWTAuthMiddlewareStack

# Setup WebSocket routing with JWT authentication
application = ProtocolTypeRouter({
    "http": django_asgi_app,
    "websocket": JWTAuthMiddlewareStack(
        URLRouter(chat.routing.websocket_urlpatterns)
    ),
})