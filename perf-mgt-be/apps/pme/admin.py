from django.contrib import admin
from .models import (
    Template,
    TemplateNodeType,
    ReportingFrequency,
    Document,
    Item,
    ReportingPeriod,
    Initiative,
    ItemContributor,
    InitiativeAccomplishment,
    InitiativeAccomplishmentFile,
)
from import_export import resources, fields
from import_export.widgets import ForeignKeyWidget
from import_export.admin import ImportExportModelAdmin


# DOCUMENT IMPORT-EXPORT RESOURCE
class DocumentResource(resources.ModelResource):
    template = fields.Field(
        column_name='template',
        attribute='template',
        widget=ForeignKeyWidget(Template, 'name')
    )

    reporting_frequency = fields.Field(
        column_name='reporting_frequency',
        attribute='reporting_frequency',
        widget=ForeignKeyWidget(ReportingFrequency, 'name')
    )

    class Meta:
        model = Document
        import_id_fields = ('name',)
        fields = ('name', 'template', 'reporting_frequency', 'status')


# ITEM IMPORT-EXPORT RESOURCE
class ItemResource(resources.ModelResource):
    document = fields.Field(
        column_name='document',
        attribute='document',
        widget=ForeignKeyWidget(Document, 'name')
    )

    template_node_type = fields.Field(
        column_name='template_node_type',
        attribute='template_node_type',
        widget=ForeignKeyWidget(TemplateNodeType, 'name')
    )

    class Meta:
        model = Item
        import_id_fields = ('code',)
        fields = ('name', 'document', 'template_node_type', 'code', 'status')


# REPORTING PERIOD IMPORT-EXPORT RESOURCE
class ReportingPeriodResource(resources.ModelResource):
    document = fields.Field(
        column_name='document',
        attribute='document',
        widget=ForeignKeyWidget(Document, 'name')
    )

    class Meta:
        model = ReportingPeriod
        import_id_fields = ('document', 'period_number')
        fields = (
            'document',
            'period_number',
            'start_date',
            'end_date',
            'deadline',
        )


# ITEM CONTRIBUTOR INLINE
class ItemContributorInline(admin.TabularInline):
    model = ItemContributor
    extra = 1
    autocomplete_fields = ("unit",)
    show_change_link = True


# INITIATIVE ACCOMPLISHMENT INLINE
class InitiativeAccomplishmentInline(admin.TabularInline):
    model = InitiativeAccomplishment
    extra = 0
    autocomplete_fields = (
        "reporting_period",
        "submitted_by",
    )
    readonly_fields = ("created_at",)
    show_change_link = True


class InitiativeAccomplishmentFileInline(admin.TabularInline):
    model = InitiativeAccomplishmentFile
    extra = 0
    readonly_fields = ("created_at", "updated_at")


# TEMPLATE ADMIN
@admin.register(Template)
class TemplateAdmin(admin.ModelAdmin):
    list_display = ("name", "short_code", "description")
    search_fields = ("name", "short_code")
    ordering = ("name",)


@admin.register(TemplateNodeType)
class TemplateNodeTypeAdmin(admin.ModelAdmin):
    list_display = ("name", "template_name", "order", "is_parent")
    search_fields = ("name", "template__name")
    ordering = ("template__name", "order")

    @admin.display(description="Template")
    def template_name(self, obj):
        return obj.template.name


# REPORTING FREQUENCY ADMIN
@admin.register(ReportingFrequency)
class ReportingFrequencyAdmin(admin.ModelAdmin):
    list_display = ("name", "short_code", "months_interval")
    list_filter = ("months_interval",)
    search_fields = ("name", "short_code")
    ordering = ("name",)


# DOCUMENT ADMIN
@admin.register(Document)
class DocumentAdmin(ImportExportModelAdmin):
    resource_class = DocumentResource

    list_display = (
        "name",
        "template_name",
        "reporting_frequency_name",
        "status",
    )
    search_fields = ("name", "template__name")
    list_filter = ("status", "reporting_frequency")
    ordering = ("name",)

    @admin.display(description="Template")
    def template_name(self, obj):
        return obj.template.name

    @admin.display(description="Reporting Frequency")
    def reporting_frequency_name(self, obj):
        return obj.reporting_frequency.name if obj.reporting_frequency else "—"


# ITEM ADMIN
@admin.register(Item)
class ItemAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "document_name",
        "template_node_type_name",
        "code",
        "status",
    )
    search_fields = (
        "name",
        "document__name",
        "template_node_type__name",
        "code",
    )
    list_filter = ("status", "document")
    ordering = ("document__name", "code")
    inlines = [ItemContributorInline]

    @admin.display(description="Document")
    def document_name(self, obj):
        return obj.document.name

    @admin.display(description="Node Type")
    def template_node_type_name(self, obj):
        return obj.template_node_type.name


# REPORTING PERIOD ADMIN
@admin.register(ReportingPeriod)
class ReportingPeriodAdmin(ImportExportModelAdmin):
    resource_class = ReportingPeriodResource
    
    ordering = ("document", "period_number")
    list_display = (
        "document",
        "period_number",
        "start_date",
        "end_date",
        "deadline",
    )
    list_filter = ("document",)
    search_fields = ("document__name",)


# INITIATIVE (PLANNING) ADMIN
@admin.register(Initiative)
class InitiativeAdmin(admin.ModelAdmin):
    list_display = (
        "description",
        "item",
        "unit_name",
        "target_date",
        "value",
        "created_by",
    )

    list_filter = (
        "item__document",
        "unit",
        "target_date",
    )

    search_fields = (
        "description",
        "item__name",
        "item__code",
        "created_by__username",
        "created_by__email",
    )

    autocomplete_fields = (
        "item",
        "created_by",
        "unit",
    )

    inlines = [InitiativeAccomplishmentInline]

    ordering = ("item__name", "target_date")

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related(
            "item",
            "unit",
            "created_by",
        )

    @admin.display(description="Unit")
    def unit_name(self, obj):
        return obj.unit.name if obj.unit else "—"


# INITIATIVE ACCOMPLISHMENT ADMIN (OPTIONAL SEPARATE VIEW)
@admin.register(InitiativeAccomplishment)
class InitiativeAccomplishmentAdmin(admin.ModelAdmin):
    list_display = (
        "initiative",
        "reporting_period",
        "status",
        "submitted_by",
    )

    list_filter = (
        "status",
        "reporting_period",
        "initiative__unit",
    )

    search_fields = (
        "initiative__description",
        "submitted_by__username",
        "submitted_by__email",
    )

    autocomplete_fields = (
        "initiative",
        "reporting_period",
        "submitted_by",
    )

    inlines = [InitiativeAccomplishmentFileInline]

    ordering = ("-created_at",)

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related(
            "initiative",
            "reporting_period",
            "submitted_by",
        )
