# django imports
from django.conf import settings
from django.contrib import admin
from django.urls import path, include
from django.conf.urls.static import static


v1_patterns = [
    path('admin/user/', include('apps.user.urls')),
]

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include([path('v1/', include(v1_patterns))])),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
