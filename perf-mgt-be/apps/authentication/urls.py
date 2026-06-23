from django.urls import path
from .views import (
    LoginView,
    LogoutView,
    RefreshTokenView,
    SessionCheckView,
    UserViewSet,
    UserDashboardStatsView,
)

urlpatterns = [
    path('login/', LoginView.as_view(), name='login'),
    path("logout/", LogoutView.as_view(), name="logout"),
    path('refresh/', RefreshTokenView.as_view(), name='refresh'),
    path('session/', SessionCheckView.as_view(), name='session'),
    path('users/', UserViewSet.as_view({'get': 'list'}), name='user-list'),
    path('users/create/', UserViewSet.as_view({'post': 'create'}), name='user-create'),
    path('users/<uuid:pk>/', UserViewSet.as_view({ 'get': 'retrieve', 'put': 'update', 'patch': 'partial_update'}), name='user-detail',),
    path('users/stats/', UserDashboardStatsView.as_view(), name='user-dashboard-stats'),
]
