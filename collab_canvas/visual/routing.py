from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.security.websocket import AllowedHostsOriginValidator
from django.urls import path
# from django.conf.urls import url

from .consumers import VisualCellEditConsumer


application = ProtocolTypeRouter({
    # Empty for now (http->django views is added by default)

    # Use ALLOWED_HOSTS config for the whole project.
    # Use OriginValidator if it's helpful to differentiate.
    # https://channels.readthedocs.io/en/latest/topics/security.html
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
    # 'websocket': URLRouter(
    #     [
    #         url("test_canvas/channels", VisualCellEditConsumer),
    #     ]
    # )
})
