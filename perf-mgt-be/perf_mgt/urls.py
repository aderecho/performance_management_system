from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from django.urls import path, include
from apps.authentication.views import LoginView, LogoutView, RefreshTokenView
# from rest_framework_simplejwt.views import TokenRefreshView
from apps.authentication.views import SessionCheckView

urlpatterns = [
    path('admin/', admin.site.urls),

    path('api/v1/core/', include("apps.core.urls")),
    path('api/v1/pme/', include("apps.pme.urls")),
    path('api/v1/auth/', include("apps.authentication.urls")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
