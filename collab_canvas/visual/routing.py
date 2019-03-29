from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.security.websocket import AllowedHostsOriginValidator
from django.urls import path

from .consumers import VisualCellEditConsumer


application = ProtocolTypeRouter({
    # Empty for now (http->django views is added by default)
    'websocket': AllowedHostsOriginValidator(
        AuthMiddlewareStack(
            URLRouter(
                [
                    path("canvas/cell/<uuid:cell_id>/edit/changes",
                         VisualCellEditConsumer),
                ]
            )
        )
    )
})
