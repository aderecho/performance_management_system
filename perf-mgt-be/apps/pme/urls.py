from rest_framework.routers import DefaultRouter
from django.urls import path, include
from .views import (
    TemplateViewSet,
    TemplateNodeTypeViewSet,
    ReportingFrequencyViewSet,
    DocumentViewSet,
    ItemViewSet,
    ReportingPeriodViewSet,
    InitiativeViewSet,
    DashboardEmbedViewSet,
    DashboardSummaryView
)

router = DefaultRouter()
router.register(r"templates", TemplateViewSet, basename="templates")
router.register(r"template-node-types", TemplateNodeTypeViewSet, basename="template-node-types")
router.register(r"reporting-frequencies", ReportingFrequencyViewSet, basename="reporting-frequencies")
router.register(r"documents", DocumentViewSet, basename="documents")
router.register(r"dashboard-embeds", DashboardEmbedViewSet, basename="dashboard-embeds")
router.register(r"items", ItemViewSet, basename="items")
router.register(r"reporting-periods", ReportingPeriodViewSet, basename="reporting-periods")
router.register(r"initiatives", InitiativeViewSet, basename="initiatives")

report_submission_list = InitiativeViewSet.as_view({
    "get": "by_item",
})

urlpatterns = [
    path("", include(router.urls)),
    path("dashboard/summary/", DashboardSummaryView.as_view(), name="dashboard-summary"),
    path("items/<uuid:item_pk>/initiatives/",report_submission_list,name="item-initiatives-list"),
]
