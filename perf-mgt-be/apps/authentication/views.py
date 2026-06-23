
from rest_framework import status
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, AllowAny, IsAdminUser
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework import viewsets, status

from django.contrib.auth import get_user_model
from django.contrib.auth import authenticate
from django.http import JsonResponse

from .authentication import CookieJWTAuthentication

from .serializers import UserSerializer, UserCreateSerializer, UserUpdateSerializer
from .services import UserDashboardService

User = get_user_model()

class LoginView(APIView):
    permission_classes = [AllowAny]
    authentication_classes = []

    def post(self, request):
        email = request.data.get("email")
        password = request.data.get("password")

        user = authenticate(request, email=email, password=password)

        if user is None:
            return Response({"error": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED)

        refresh = RefreshToken.for_user(user)
        access_token = str(refresh.access_token)
        refresh_token = str(refresh)

        response = JsonResponse({"message": "Login successful"})

        # Set secure cookies
        response.set_cookie(
            key="access_token",
            value=access_token,
            httponly=True,
            secure=False,  # Set to True in production (HTTPS)
            samesite="Lax", #Lax
            max_age=60 * 30,  # 30 minutes
        )
        response.set_cookie(
            key="refresh_token",
            value=refresh_token,
            httponly=True,
            secure=False,  # Set to True in production (HTTPS)
            samesite="Lax", #Lax
            max_age=60 * 60 * 24 * 7,  # 7 days
        )

        return response
    

class LogoutView(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]

    def post(self, request):
        """
        Blacklist refresh token
        Clear JWT cookies
        """

        refresh_token = request.COOKIES.get("refresh_token")

        if refresh_token:
            try:
                token = RefreshToken(refresh_token)
                token.blacklist()
            except Exception:
                # Token may already be invalid/expired
                pass

        response = Response(
            {"detail": "Successfully logged out."},
            status=status.HTTP_200_OK
        )

        # Clear cookies
        response.delete_cookie("access_token")
        response.delete_cookie("refresh_token")

        return response


class SessionCheckView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [CookieJWTAuthentication]

    def get(self, request):
        print('cookies', request.COOKIES)
        print('user', request.user)
        user = request.user
        if user and user.is_authenticated:
            return Response({
                "active": True,
                "user": {
                    "id": user.id,
                    "email": user.email,
                    "first_name": user.profile.first_name,
                    "last_name": user.profile.last_name,
                    "is_superadmin": user.is_superuser,
                    "roles": list(user.groups.values_list("name", flat=True)),
                    "permissions": list(user.get_all_permissions()),
                }
            }, status=status.HTTP_200_OK)
        else:
            return Response({
                "active": False
            }, status=status.HTTP_401_UNAUTHORIZED)
        

class RefreshTokenView(APIView):
    permission_classes = [AllowAny]
    authentication_classes = []

    def post(self, request):
        from rest_framework_simplejwt.tokens import RefreshToken
        refresh_token = request.COOKIES.get('refresh_token')
        if not refresh_token:
            return Response({"error": "No refresh token"}, status=status.HTTP_401_UNAUTHORIZED)

        try:
            refresh = RefreshToken(refresh_token)
            access_token = str(refresh.access_token)
        except Exception:
            return Response(
                {"error": "Invalid refresh token"},
                status=status.HTTP_401_UNAUTHORIZED
            )

        response = JsonResponse({"message": "Token refreshed"})
        response.set_cookie(
            key="access_token",
            value=access_token,
            httponly=True,
            secure=False, # True in production
            samesite="Lax",
            max_age=60 * 30,  # 30 minutes
        )
        return response
    

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all().prefetch_related(
        "user_units__unit",
        "profile"
    )

    permission_classes = [IsAdminUser]

    def get_serializer_class(self):
        if self.action == "create":
            return UserCreateSerializer
        if self.action in ["update", "partial_update"]:
            return UserUpdateSerializer
        return UserSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        params = self.request.query_params

        primary_unit = params.get("primary_unit")
        is_active = params.get("is_active")
        is_superuser = params.get("is_superuser")

        if primary_unit:
            queryset = queryset.filter(
                user_units__unit_id=primary_unit,
                user_units__is_primary=True,
                user_units__is_active=True,
            )

        if is_active in ["true", "false"]:
            queryset = queryset.filter(is_active=is_active == "true")

        if is_superuser in ["true", "false"]:
            queryset = queryset.filter(is_superuser=is_superuser == "true")

        return queryset.distinct().order_by("-created_at")

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = serializer.save()

        return Response(
            UserSerializer(user).data,
            status=status.HTTP_201_CREATED
        )

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop("partial", False)
        instance = self.get_object()
        serializer = self.get_serializer(
            instance,
            data=request.data,
            partial=partial,
        )
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        return Response(UserSerializer(user).data, status=status.HTTP_200_OK)



class UserDashboardStatsView(APIView):

    def get(self, request):
        data = UserDashboardService.get_stats()
        return Response(data)
