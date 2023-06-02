from django.urls import re_path

from . import consumers

websocket_urlpatterns = [
    re_path(r'ws/tickets_updates/$', consumers.TicketsConsumer.as_asgi()),
    re_path(r'ws/tickets_control/$', consumers.TicketsConsumer.as_asgi()),
]
