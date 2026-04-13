from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError
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
    ItemContributor,
)
from apps.pme.serializers import (
    TemplateSerializer,
    TemplateNodeTypeSerializer,
    ReportingFrequencySerializer,
    DocumentSerializer,
    ItemFilterSerializer,
    ReportingPeriodSerializer,
    InitiativeSerializer,
    DocumentWithItemsSerializer,
    InitiativeAccomplishmentSerializer,
)
from apps.pme.services import (
    generate_reporting_periods_for_document,
    prefetch_latest_submitted_accomplishment,
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

    @action(detail=True, methods=["post"], url_path="generate-periods")
    def generate_periods(self, request, pk=None):
        document = self.get_object()
        periods_ahead = int(request.data.get("periods_ahead", 12))
        created = generate_reporting_periods_for_document(document, periods_ahead)
        return Response(
            ReportingPeriodSerializer(created, many=True).data,
            status=status.HTTP_201_CREATED,
        )
    
    @action(detail=True, methods=["get"], url_path="items")
    def items(self, request, pk=None):
        document = self.get_object()

        period_id = request.query_params.get("period")
        item_id = request.query_params.get("item")
        show_all = request.query_params.get("show_all")

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
        parent_id = self.request.query_params.get("parent")

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
    queryset = Initiative.objects.select_related(
        "item",
        "created_by",
        "created_at",
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

        # Save initiative
        serializer.save(
            created_by=user,
            unit=unit,
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
        print(initiative)

        # GET
        if request.method == "GET":
            qs = [initiative.accomplishment] if initiative.accomplishment else []
            serializer = InitiativeAccomplishmentSerializer(qs, many=True)
            return Response(serializer.data)

        # POST
        if request.method == "POST":
            if hasattr(initiative, "accomplishment"):
                return Response(
                    {"detail": "Initiative already has an accomplishment."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            serializer = InitiativeAccomplishmentSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save(
                initiative=initiative,
                submitted_by=request.user,
            )
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        # DELETE (REVERT)
        if request.method == "DELETE":
            if not hasattr(initiative, "accomplishment"):
                return Response(
                    {"detail": "No accomplishment to delete."},
                    status=status.HTTP_404_NOT_FOUND,
                )

            initiative.accomplishment.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        # if request.method == "DELETE":
        #     if not initiative.accomplishment:
        #         return Response(
        #             {"detail": "No accomplishment to delete."},
        #             status=status.HTTP_404_NOT_FOUND
        #         )

        #     initiative.accomplishment.delete()
        #     return Response(status=status.HTTP_204_NO_CONTENT)
    