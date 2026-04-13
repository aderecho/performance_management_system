from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework_simplejwt.views import TokenObtainPairView
from datetime import timedelta
from apps.core.models import (
    UnitOfMeasure,
    Unit,
    UserUnit
)
from apps.core.serializers import (
    UnitOfMeasureSerializer,
    UnitSerializer,
    UserUnitSerializer
)

class UnitOfMeasureViewSet(viewsets.ModelViewSet):
    queryset = UnitOfMeasure.objects.all()
    serializer_class = UnitOfMeasureSerializer


class UnitViewSet(viewsets.ModelViewSet):
    queryset = Unit.objects.all()
    serializer_class = UnitSerializer


class UserUnitViewSet(viewsets.ModelViewSet):
    queryset = UserUnit.objects.all()
    serializer_class = UserUnitSerializer


# class CookieTokenObtainPairView(TokenObtainPairView):
#     def post(self, request, *args, **kwargs):
#         response = super().post(request, *args, **kwargs)
#         if response.status_code == 200:
#             data = response.data

#             access_token = data.get("access")
#             refresh_token = data.get("refresh")

#             # Secure cookie options
#             access_max_age = timedelta(minutes=5)
#             refresh_max_age = timedelta(days=7)

#             # set cookies
#             response.set_cookie(
#                 key="access_token",
#                 value=access_token,
#                 httponly=True,
#                 secure=False,  # change to True if using HTTPS
#                 samesite="Lax",  # or "None" if cross-origin + HTTPS
#                 max_age=access_max_age.total_seconds(),
#                 path="/"
#             )
#             response.set_cookie(
#                 key="refresh_token",
#                 value=refresh_token,
#                 httponly=True,
#                 secure=False,
#                 samesite="Lax",
#                 max_age=refresh_max_age.total_seconds(),
#                 path="/"
#             )

#             # optionally hide tokens from body
#             del response.data["access"]
#             del response.data["refresh"]

#         return response