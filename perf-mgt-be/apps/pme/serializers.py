from rest_framework import serializers
from apps.pme.models import (
    Template,
    TemplateNodeType,
    Document,
    Item,
    ReportingPeriod,
    Initiative,
    InitiativeAccomplishment,
    InitiativeAccomplishmentFile,
    ReportingFrequency,
    ItemContributor,
)
from apps.pme.services import (
    build_document_item,
)
from apps.core.models import Unit
from apps.core.serializers import UnitOfMeasureSerializer
from django.contrib.auth import get_user_model

User = get_user_model()

# TEMPLATE
class TemplateSerializer(serializers.ModelSerializer):
    documents = serializers.SerializerMethodField()

    class Meta:
        model = Template
        fields = "__all__"

    def get_documents(self, obj):
        from apps.pme.serializers import DocumentSerializer
        return DocumentSerializer(
            obj.documents.all(),
            many=True,
            context=self.context,
        ).data

class TemplateNodeTypeSerializer(serializers.ModelSerializer):
    template_name = serializers.CharField(
        source="template.name",
        read_only=True
    )

    class Meta:
        model = TemplateNodeType
        fields = [
            "id",
            "template",
            "template_name",
            "name",
            "short_code",
            "description",
            "order",
            "is_parent",
        ]

# ITEM
class ItemContributorSerializer(serializers.ModelSerializer):
    unit_name = serializers.CharField(source="unit.name", read_only=True)

    class Meta:
        model = ItemContributor
        fields = ["id", "unit", "unit_name"]


class ItemSerializer(serializers.ModelSerializer):
    parent_name = serializers.CharField(source="parent.name", read_only=True)
    template_node_type_name = serializers.CharField(
        source="template_node_type.name", read_only=True
    )
    unit_of_measure = UnitOfMeasureSerializer(read_only=True)
    contributors = ItemContributorSerializer(many=True, read_only=True)

    class Meta:
        model = Item
        fields = "__all__"

class ItemFilterSerializer(serializers.ModelSerializer):
    class Meta:
        model = Item
        fields = ["id", "code", "name"]

class ItemHierarchySerializer(serializers.ModelSerializer):
    children = serializers.SerializerMethodField()
    template_node_type_name = serializers.CharField(
        source="template_node_type.name", read_only=True
    )
    unit_of_measure = UnitOfMeasureSerializer(read_only=True)
    contributors = ItemContributorSerializer(many=True, read_only=True)

    class Meta:
        model = Item
        fields = [
            "id",
            "code",
            "name",
            "description",
            "target",
            "status",
            "template_node_type_name",
            "unit_of_measure",
            "contributors",
            "children",
        ]

    def get_children(self, obj):
        return ItemHierarchySerializer(
            getattr(obj, "children_cache", []),
            many=True,
            context=self.context,
        ).data

# DOCUMENT
class DocumentSerializer(serializers.ModelSerializer):
    template_name = serializers.CharField(source="template.name", read_only=True)

    class Meta:
        model = Document
        fields = "__all__"


class ReportingPeriodSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReportingPeriod
        fields = "__all__"


class ReportingFrequencySerializer(serializers.ModelSerializer):
    class Meta:
        model = ReportingFrequency
        fields = "__all__"

# INITIATIVES
class UnitInlineSerializer(serializers.ModelSerializer):
    class Meta:
        model = Unit
        fields = ["id", "name", "short_code"]


class UserWithUnitSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()
    unit = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ["id", "unit"]

    def get_full_name(self, obj):
        return f"{obj.first_name} {obj.last_name}".strip()

    def get_unit(self, obj):
        user_unit = (
            obj.user_units
            .filter(is_primary=True, is_active=True)
            .select_related("unit")
            .first()
        )
        return UnitInlineSerializer(user_unit.unit).data if user_unit else None
    

class InitiativeAccomplishmentFileSerializer(serializers.ModelSerializer):
    file_url = serializers.SerializerMethodField()
    file_name = serializers.SerializerMethodField()
    status_label = serializers.CharField(source="get_status_display", read_only=True)

    class Meta:
        model = InitiativeAccomplishmentFile
        fields = [
            "id",
            "file_url",
            "file_name",
            "status",
            "status_label",
            "created_at",
            "updated_at",
        ]

    def get_file_url(self, obj):
        if not obj.file_path:
            return None

        request = self.context.get("request")
        if request:
            return request.build_absolute_uri(obj.file_path.url)

        return obj.file_path.url

    def get_file_name(self, obj):
        if not obj.file_path:
            return None

        return obj.file_path.name.split("/")[-1]


class InitiativeAccomplishmentSerializer(serializers.ModelSerializer):
    reporting_period = serializers.PrimaryKeyRelatedField(
        queryset=ReportingPeriod.objects.all()
    )

    reporting_period_detail = ReportingPeriodSerializer(
        source="reporting_period",
        read_only=True
    )
    file_url = serializers.SerializerMethodField()
    file_name = serializers.SerializerMethodField()
    status_label = serializers.CharField(source="get_status_display", read_only=True)
    evidence_history = serializers.SerializerMethodField()

    class Meta:
        model = InitiativeAccomplishment
        fields = [
            "id",
            "initiative",
            "reporting_period",
            "reporting_period_detail",
            "file_path",
            "file_url",
            "file_name",
            "status",
            "status_label",
            "evidence_history",
            "submitted_by",
            "created_at",
            "updated_at",
        ]
        read_only_fields = (
            "initiative",
            "submitted_by",
            "created_at",
            "updated_at",
            "file_url",
            "file_name",
            "status",
            "status_label",
            "evidence_history",
        )
        extra_kwargs = {
            "file_path": {
                "write_only": True,
                "required": False,
                "allow_null": True,
            },
        }

    def get_file_url(self, obj):
        file_record = self.get_active_file(obj)
        if file_record:
            return InitiativeAccomplishmentFileSerializer(
                file_record,
                context=self.context,
            ).data["file_url"]

        if obj.status != InitiativeAccomplishment.STATUS_ACTIVE or not obj.file_path:
            return None

        request = self.context.get("request")
        if request:
            return request.build_absolute_uri(obj.file_path.url)

        return obj.file_path.url

    def get_file_name(self, obj):
        file_record = self.get_active_file(obj)
        if file_record:
            return file_record.file_path.name.split("/")[-1]

        if obj.status != InitiativeAccomplishment.STATUS_ACTIVE or not obj.file_path:
            return None

        return obj.file_path.name.split("/")[-1]

    def get_evidence_history(self, obj):
        return InitiativeAccomplishmentFileSerializer(
            obj.files.all(),
            many=True,
            context=self.context,
        ).data

    def get_active_file(self, obj):
        return (
            obj.files
            .filter(status=InitiativeAccomplishmentFile.STATUS_ACTIVE)
            .order_by("-created_at")
            .first()
        )
    # reporting_period = ReportingPeriodSerializer(read_only=True)

    # class Meta:
    #     model = InitiativeAccomplishment
    #     fields = "__all__"
    #     read_only_fields = ("initiative", "submitted_by", "created_at", "updated_at")


class InitiativeSerializer(serializers.ModelSerializer):
    item_name = serializers.CharField(source="item.name", read_only=True)
    document_id = serializers.UUIDField(source="item.document_id", read_only=True)
    unit = UnitInlineSerializer(read_only=True)
    created_by = serializers.SerializerMethodField()
    accomplishment = serializers.SerializerMethodField()
    is_accomplished = serializers.SerializerMethodField()

    class Meta:
        model = Initiative
        fields = [
            "id",
            "item",
            "item_name",
            "document_id",
            "description",
            "target_date",
            "value",
            "created_by",
            "unit",
            "accomplishment",
            "is_accomplished",
        ]
        read_only_fields = (
            "item_name",
            "document_id",
            "created_by",
            "unit",
            "accomplishment",
        )    

    def get_accomplishment(self, obj):
        try:
            return InitiativeAccomplishmentSerializer(
                obj.accomplishment,
                context=self.context,
            ).data
        except InitiativeAccomplishment.DoesNotExist:
            return None

    def get_is_accomplished(self, obj):
        try:
            return obj.accomplishment.status == InitiativeAccomplishment.STATUS_ACTIVE
        except InitiativeAccomplishment.DoesNotExist:
            return False

    def get_created_by(self, obj):
        user = obj.created_by
        if not user:
            return None

        return {
            "id": user.id,
            # "first_name": user.first_name,
            # "last_name": user.last_name,
        }

    def validate_value(self, value):
        if value <= 0:
            raise serializers.ValidationError(
                "Accomplishment value must be greater than zero."
            )
        return value

    def validate_description(self, value):
        if len(value) > 500:
            raise serializers.ValidationError(
                "Description must not exceed 500 characters."
            )
        return value

    def validate(self, attrs):
        item = attrs.get('item')
        target_date = attrs.get('target_date')

        if not item:
            raise serializers.ValidationError({
                'item': 'Indicator is required.'
            })

        if not target_date:
            raise serializers.ValidationError({
                'target_date': 'Target date is required.'
            })

        return attrs
    

class InitiativeInlineSerializer(serializers.ModelSerializer):
    unit = UnitInlineSerializer(read_only=True)

    class Meta:
        model = Initiative
        fields = [
            "id",
            "description",
            "value",
            "unit",
        ]
    
    def get_unit(self, obj):
        unit = obj.unit
        if not unit:
            return None

        return {
            "id": unit.id,
            "name": unit.name,
            "short_code": unit.short_code,
            'asd': 'asd'
        }


class DocumentItemSerializer(serializers.ModelSerializer):
    children = serializers.SerializerMethodField()
    # submissions = serializers.SerializerMethodField()
    total_accomplishment = serializers.FloatField(read_only=True)
    percent_achieved = serializers.FloatField(read_only=True)

    class Meta:
        model = Item
        fields = [
            "id",
            "code",
            "name",
            "target",
            "total_accomplishment",
            "percent_achieved",
            # "submissions",
            "children",
        ]

    def get_children(self, obj):
        return DocumentItemSerializer(
            getattr(obj, "children_cache", []),
            many=True,
            context=self.context,
        ).data

    
class DocumentWithItemsSerializer(serializers.Serializer):
    id = serializers.UUIDField()
    name = serializers.CharField()
    template_name = serializers.CharField(source="template.name")
    items = serializers.SerializerMethodField()

    def get_items(self, document):
        reporting_period = self.context.get("reporting_period")
        item_id = self.context.get("item_id")
        show_all = self.context.get("show_all")
        request = self.context.get("request")

        items, submissions_map = build_document_item(
            document,
            reporting_period=reporting_period,
            item_id=item_id,
            # show_all=show_all,
            request=request,
        )

        return DocumentItemSerializer(
            items,
            many=True,
            context={"submissions_map": submissions_map},
        ).data
