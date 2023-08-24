from django.contrib import admin
from django.urls import path, include, re_path

from django.conf import settings

from django.views.static import serve
urlpatterns = [
    re_path(r'^media/(?P<path>.*)$', serve,{'document_root': settings.MEDIA_ROOT}),

    re_path(r'^static/(?P<path>.*)$', serve,{'document_root': settings.STATIC_ROOT}),
    path('admin/', admin.site.urls),
    path('', include('tickets.urls')),
]

handler404 = 'tickets.views.error_404'
handler500 = 'tickets.views.error_500'
