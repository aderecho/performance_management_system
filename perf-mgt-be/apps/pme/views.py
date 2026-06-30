from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.parsers import FormParser, JSONParser, MultiPartParser
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError
from rest_framework.views import APIView
from django.db import transaction
from django.shortcuts import get_object_or_404
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated
from apps.core.models import UserUnit
from apps.pme.models import (
    Template,
    TemplateNodeType,
    ReportingFrequency,
    Document,
    Item,
    ReportingPeriod,
    Initiative,
    InitiativeAccomplishment,
    InitiativeAccomplishmentFile,
    ItemContributor,
)
from apps.pme.serializers import (
    TemplateSerializer,
    TemplateNodeTypeSerializer,
    ReportingFrequencySerializer,
    DocumentSerializer,
    GeneratePeriodsRequestSerializer,
    DocumentItemsQuerySerializer,
    ItemFilterSerializer,
    ItemListQuerySerializer,
    ReportingPeriodSerializer,
    InitiativeSerializer,
    DocumentWithItemsSerializer,
    InitiativeAccomplishmentSerializer,
    DashboardSummaryQuerySerializer,
)
from apps.pme.services import (
    generate_reporting_periods_for_document,
    prefetch_latest_submitted_accomplishment,
    get_dashboard_summary
)
from apps.authentication.models import AuditLog
from apps.authentication.services import AuditLogService


def changed_fields_from_serializer(serializer):
    return sorted(serializer.validated_data.keys())


def record_pme_audit(request, action, target, summary, metadata=None):
    AuditLogService.record(
        request=request,
        module=AuditLog.MODULE_PME,
        action=action,
        target_type=target.__class__.__name__.lower(),
        target_id=getattr(target, "id", ""),
        target_label=str(target),
        summary=summary,
        metadata=metadata or {},
    )


class TemplateViewSet(viewsets.ModelViewSet):
    queryset = Template.objects.all()
    serializer_class = TemplateSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]


class TemplateNodeTypeViewSet(viewsets.ModelViewSet):
    queryset = TemplateNodeType.objects.all()
    serializer_class = TemplateNodeTypeSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]


class ReportingFrequencyViewSet(viewsets.ModelViewSet):
    queryset = ReportingFrequency.objects.all()
    serializer_class = ReportingFrequencySerializer
    permission_classes = [IsAuthenticatedOrReadOnly]


class DocumentViewSet(viewsets.ModelViewSet):
    queryset = Document.objects.select_related("template", "reporting_frequency")
    serializer_class = DocumentSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    def perform_create(self, serializer):
        document = serializer.save()
        record_pme_audit(
            self.request,
            "document.create",
            document,
            f"Created document {document.name}.",
            metadata={"fields": changed_fields_from_serializer(serializer)},
        )

    def perform_update(self, serializer):
        document = serializer.save()
        record_pme_audit(
            self.request,
            "document.update",
            document,
            f"Updated document {document.name}.",
            metadata={
                "fields": changed_fields_from_serializer(serializer),
                "status": document.get_status_display(),
            },
        )

    def perform_destroy(self, instance):
        metadata = {"status": instance.get_status_display()}
        target_id = instance.id
        target_label = instance.name
        instance.delete()
        AuditLogService.record(
            request=self.request,
            module=AuditLog.MODULE_PME,
            action="document.delete",
            target_type="document",
            target_id=target_id,
            target_label=target_label,
            summary=f"Deleted document {target_label}.",
            metadata=metadata,
        )

    @action(detail=True, methods=["post"], url_path="generate-periods")
    def generate_periods(self, request, pk=None):
        document = self.get_object()
        request_serializer = GeneratePeriodsRequestSerializer(data=request.data)
        request_serializer.is_valid(raise_exception=True)
        periods_ahead = request_serializer.validated_data["periods_ahead"]

        created = generate_reporting_periods_for_document(document, periods_ahead)
        return Response(
            ReportingPeriodSerializer(created, many=True).data,
            status=status.HTTP_201_CREATED,
        )
    
    @action(detail=True, methods=["get"], url_path="items")
    def items(self, request, pk=None):
        document = self.get_object()

        query_serializer = DocumentItemsQuerySerializer(data=request.query_params)
        query_serializer.is_valid(raise_exception=True)
        params = query_serializer.validated_data

        period_id = params.get("period")
        item_id = params.get("item")
        show_all = params.get("show_all", False)

        reporting_period = None
        if period_id:
            reporting_period = get_object_or_404(
                ReportingPeriod,
                pk=period_id
            )

        serializer = DocumentWithItemsSerializer(
            document,
            context= {
                "reporting_period": reporting_period,
                "item_id": item_id,
                "show_all": show_all,
                "request": request,
            },
        )

        return Response(serializer.data)


class ItemViewSet(viewsets.ModelViewSet):
    # queryset = Item.objects.select_related(
    #     "document", "template_node_type", "unit_of_measure"
    # )
    # serializer_class = ItemSerializer
    serializer_class = ItemFilterSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """
        Filters items by:
        - document (required for hierarchy scope)
        - parent (optional, for cascading levels)
        """

        qs = Item.objects.select_related(
            "document",
            "template_node_type",
            "unit_of_measure",
        )

        document_id = self.request.query_params.get("document")
        query_serializer = ItemListQuerySerializer(data=self.request.query_params)
        query_serializer.is_valid(raise_exception=True)
        params = query_serializer.validated_data

        document_id = params.get("document")
        parent_id = params.get("parent")

        # Restrict to specific document
        if document_id:
            qs = qs.filter(document_id=document_id)

        # If parent provided → return children
        if parent_id:
            qs = qs.filter(parent_id=parent_id)
        else:
            # Otherwise return top-level nodes
            qs = qs.filter(parent__isnull=True)

        return qs.order_by("code")

    def perform_create(self, serializer):
        item = serializer.save()
        record_pme_audit(
            self.request,
            "item.create",
            item,
            f"Created item {item.name}.",
            metadata={"fields": changed_fields_from_serializer(serializer)},
        )

    def perform_update(self, serializer):
        item = serializer.save()
        record_pme_audit(
            self.request,
            "item.update",
            item,
            f"Updated item {item.name}.",
            metadata={
                "fields": changed_fields_from_serializer(serializer),
                "status": item.get_status_display(),
            },
        )

    def perform_destroy(self, instance):
        target_id = instance.id
        target_label = instance.name
        metadata = {
            "document": instance.document.name,
            "status": instance.get_status_display(),
        }
        instance.delete()
        AuditLogService.record(
            request=self.request,
            module=AuditLog.MODULE_PME,
            action="item.delete",
            target_type="item",
            target_id=target_id,
            target_label=target_label,
            summary=f"Deleted item {target_label}.",
            metadata=metadata,
        )

    


class ReportingPeriodViewSet(viewsets.ModelViewSet):
    queryset = ReportingPeriod.objects.select_related("document")
    serializer_class = ReportingPeriodSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    @action(detail=True, methods=["get"])
    def initiative(self, request, pk=None):
        rp = self.get_object()
        qs = rp.submissions.select_related("item", "created_by")
        return Response(InitiativeSerializer(qs, many=True).data)


class InitiativeViewSet(viewsets.ModelViewSet):
    serializer_class = InitiativeSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    parser_classes = [MultiPartParser, FormParser, JSONParser]
    queryset = Initiative.objects.select_related(
        "item",
        "created_by",
        "unit",
        "accomplishment"
    )
    # .prefetch_related(
        # "accomplishments" # Reverse FK / Many-to-Many Relations
    # )

    # Override create to set created_by and unit
    def perform_create(self, serializer):
        user = self.request.user
        item = serializer.validated_data["item"]

        try:
            user_unit = UserUnit.objects.select_related("unit").get(
                user=user,
                is_primary=True,
                is_active=True,
            )
        except UserUnit.DoesNotExist:
            raise ValidationError(
                "You do not have an active primary unit assigned."
            )
        unit = user_unit.unit

        # Contributor check
        if not ItemContributor.objects.filter(
            item=item,
            unit=unit,
        ).exists():
            raise ValidationError(
                "Your unit is not authorized to submit initiatives for this item."
            )

        initiative = serializer.save(
            created_by=user,
            unit=unit,
        )
        record_pme_audit(
            self.request,
            "initiative.create",
            initiative,
            f"Created initiative {initiative.description}.",
            metadata={
                "item": item.name,
                "unit": unit.short_code or unit.name,
                "fields": changed_fields_from_serializer(serializer),
            },
        )

    def perform_update(self, serializer):
        initiative = serializer.save()
        record_pme_audit(
            self.request,
            "initiative.update",
            initiative,
            f"Updated initiative {initiative.description}.",
            metadata={
                "item": initiative.item.name,
                "fields": changed_fields_from_serializer(serializer),
            },
        )

    def perform_destroy(self, instance):
        target_id = instance.id
        target_label = instance.description
        metadata = {
            "item": instance.item.name,
            "unit": instance.unit.short_code if instance.unit else "",
        }
        instance.delete()
        AuditLogService.record(
            request=self.request,
            module=AuditLog.MODULE_PME,
            action="initiative.delete",
            target_type="initiative",
            target_id=target_id,
            target_label=target_label,
            summary=f"Deleted initiative {target_label}.",
            metadata=metadata,
        )

    @action(detail=False, methods=["get"], url_path="by-item/(?P<item_pk>[^/.]+)")
    def by_item(self, request, item_pk=None):
        qs = self.get_queryset().filter(item_id=item_pk)
        page = self.paginate_queryset(qs)
        if page is not None:
            return self.get_paginated_response(
                self.get_serializer(page, many=True).data
            )
        return Response(self.get_serializer(qs, many=True).data)
    
    def get_queryset(self):
        base_qs = (
            Initiative.objects
            .select_related(
                "item",
                "unit",
                "created_by",
                "accomplishment"
                )
            .prefetch_related(
                "accomplishment__files",
                prefetch_latest_submitted_accomplishment()
            )
        )

        return base_qs
    
    # Accomplishments endpoint
    # @action(detail=True, methods=["get", "post", "delete"], url_path="accomplishments")
    # def accomplishments(self, request, pk=None):
    #     initiative = self.get_object()

    #     if request.method == "GET":
    #         qs = initiative.accomplishment and [initiative.accomplishment] or []
    #         serializer = InitiativeAccomplishmentSerializer(qs, many=True)
    #         return Response(serializer.data)

    #     serializer = InitiativeAccomplishmentSerializer(data=request.data)
    #     serializer.is_valid(raise_exception=True)

    #     serializer.save(
    #         initiative=initiative,
    #         submitted_by=request.user,
    #     )

    #     return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    # Accomplishments endpoint
    @action(detail=True, methods=["get", "post", "delete"], url_path="accomplishments")
    def accomplishments(self, request, pk=None):
        initiative = self.get_object()

        # GET
        if request.method == "GET":
            try:
                qs = [initiative.accomplishment]
            except InitiativeAccomplishment.DoesNotExist:
                qs = []

            serializer = InitiativeAccomplishmentSerializer(
                qs,
                many=True,
                context={"request": request},
            )
            return Response(serializer.data)

        # POST
        if request.method == "POST":
            try:
                accomplishment = initiative.accomplishment
            except InitiativeAccomplishment.DoesNotExist:
                accomplishment = None

            if accomplishment and accomplishment.status == InitiativeAccomplishment.STATUS_ACTIVE:
                return Response(
                    {"detail": "Initiative already has an accomplishment."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            serializer = InitiativeAccomplishmentSerializer(
                data=request.data,
                context={"request": request},
            )
            serializer.is_valid(raise_exception=True)

            with transaction.atomic():
                file_upload = serializer.validated_data.pop("file_path", None)
                is_update = accomplishment is not None
                file_name = getattr(file_upload, "name", "") if file_upload else ""

                if accomplishment:
                    accomplishment.reporting_period = serializer.validated_data["reporting_period"]
                    accomplishment.status = InitiativeAccomplishment.STATUS_ACTIVE
                    accomplishment.submitted_by = request.user
                    accomplishment.save(
                        update_fields=[
                            "reporting_period",
                            "status",
                            "submitted_by",
                            "updated_at",
                        ]
                    )
                else:
                    accomplishment = serializer.save(
                        initiative=initiative,
                        submitted_by=request.user,
                        status=InitiativeAccomplishment.STATUS_ACTIVE,
                    )

                accomplishment.files.filter(
                    status=InitiativeAccomplishmentFile.STATUS_ACTIVE
                ).update(status=InitiativeAccomplishmentFile.STATUS_REVERTED)

                if file_upload:
                    evidence_file = InitiativeAccomplishmentFile.objects.create(
                        accomplishment=accomplishment,
                        file_path=file_upload,
                        status=InitiativeAccomplishmentFile.STATUS_ACTIVE,
                    )
                    accomplishment.file_path = evidence_file.file_path.name
                    accomplishment.save(update_fields=["file_path", "updated_at"])
                else:
                    accomplishment.file_path = None
                    accomplishment.save(update_fields=["file_path", "updated_at"])

                action = "accomplishment.update" if is_update else "accomplishment.submit"
                period = accomplishment.reporting_period
                metadata = {
                    "initiative": initiative.description,
                    "item": initiative.item.name,
                    "reporting_period": str(period) if period else "",
                    "evidence_uploaded": bool(file_upload),
                }
                if file_name:
                    metadata["file_name"] = file_name

                record_pme_audit(
                    request,
                    action,
                    accomplishment,
                    f"{'Updated' if is_update else 'Submitted'} accomplishment for {initiative.description}.",
                    metadata=metadata,
                )

                if file_upload:
                    AuditLogService.record(
                        request=request,
                        module=AuditLog.MODULE_PME,
                        action="evidence.upload",
                        target_type="initiativeaccomplishment",
                        target_id=accomplishment.id,
                        target_label=initiative.description,
                        summary=f"Uploaded evidence for {initiative.description}.",
                        metadata={"file_name": file_name},
                    )

            response_serializer = InitiativeAccomplishmentSerializer(
                accomplishment,
                context={"request": request},
            )
            return Response(response_serializer.data, status=status.HTTP_201_CREATED)

        # DELETE (REVERT)
        if request.method == "DELETE":
            try:
                accomplishment = initiative.accomplishment
            except InitiativeAccomplishment.DoesNotExist:
                return Response(
                    {"detail": "No accomplishment to delete."},
                    status=status.HTTP_404_NOT_FOUND,
                )

            if accomplishment.status != InitiativeAccomplishment.STATUS_ACTIVE:
                return Response(
                    {"detail": "No active accomplishment to revert."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            with transaction.atomic():
                accomplishment.status = InitiativeAccomplishment.STATUS_REVERTED
                accomplishment.save(update_fields=["status", "updated_at"])
                accomplishment.files.filter(
                    status=InitiativeAccomplishmentFile.STATUS_ACTIVE
                ).update(status=InitiativeAccomplishmentFile.STATUS_REVERTED)

                record_pme_audit(
                    request,
                    "accomplishment.revert",
                    accomplishment,
                    f"Reverted accomplishment for {initiative.description}.",
                    metadata={
                        "initiative": initiative.description,
                        "item": initiative.item.name,
                        "status": accomplishment.get_status_display(),
                    },
                )
                AuditLogService.record(
                    request=request,
                    module=AuditLog.MODULE_PME,
                    action="evidence.revert",
                    target_type="initiativeaccomplishment",
                    target_id=accomplishment.id,
                    target_label=initiative.description,
                    summary=f"Reverted active evidence for {initiative.description}.",
                )

            serializer = InitiativeAccomplishmentSerializer(
                accomplishment,
                context={"request": request},
            )
            return Response(serializer.data, status=status.HTTP_200_OK)
        # if request.method == "DELETE":
        #     if not initiative.accomplishment:
        #         return Response(
        #             {"detail": "No accomplishment to delete."},
        #             status=status.HTTP_404_NOT_FOUND
        #         )

        #     initiative.accomplishment.delete()
        #     return Response(status=status.HTTP_204_NO_CONTENT)
# Dashboard Summary View
class DashboardSummaryView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        query_serializer = DashboardSummaryQuerySerializer(data=request.query_params)
        query_serializer.is_valid(raise_exception=True)
        params = query_serializer.validated_data

        return Response(get_dashboard_summary(
            search=params.get("search"),
            group=params.get("group"),
            sra=params.get("sra"),
            status=params.get("status"),
            template=params.get("template"),
            document=params.get("document"),
        ))
    
