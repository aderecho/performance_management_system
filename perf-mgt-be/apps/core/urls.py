from django.urls import path
from apps.core.views import (
    UnitOfMeasureViewSet,
    UserUnitViewSet,
    UnitViewSet
)

urlpatterns = [
    path('uoms/', UnitOfMeasureViewSet.as_view({'get': 'list'}), name='uoms-list'),
    path('units/', UnitViewSet.as_view({'get': 'list'}), name='units-list'),
    path('user-units/', UserUnitViewSet.as_view({'get': 'list'}), name='user-units-list'),
]