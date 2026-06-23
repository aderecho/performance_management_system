from django.db import models
from django.conf import settings
from apps.core.models import ( UnitOfMeasure, Unit )
import posixpath
import uuid

User = settings.AUTH_USER_MODEL

"""
FUTURE:
Instead of using Adjacency List, consider using Modified Preorder Tree Traversal (MPTT)
or Closure Table for better performance on deep hierarchies and complex queries.
"""

# FRAMEWORK LAYER (Templates & Schema)
class Template(models.Model):
    """
    Defines a framework/template
    e.g. Strategic Plan, PBB, Performance Indicators
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    short_code = models.CharField(max_length=50, blank=True, null=True)
    description = models.TextField(blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # class Meta:
        # db_table = "templates"

    def __str__(self):
        return self.name

#TEMPLATE NODE TYPE
class TemplateNodeType(models.Model):
    """
    Defines allowed node types within a template
    e.g. Strategic Result Area, Program, Project, Active, Outcome, Output, Initiative
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    template = models.ForeignKey(Template, on_delete=models.CASCADE, related_name="node_types")
    name = models.CharField(max_length=255)
    short_code = models.CharField(max_length=50, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    order = models.PositiveIntegerField(default=0)
    is_parent = models.BooleanField(default=True)

    class Meta:
        # db_table = "template_node_types"
        unique_together = ("template", "name")
        ordering = ["order", "name"]

    def __str__(self):
        return f"{self.template.name} - {self.name}"
    
# REPORTING FREQUENCY 
class ReportingFrequency(models.Model):
    """
    
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    short_code = models.CharField(max_length=50)
    description = models.TextField(null=True, blank=True)
    months_interval = models.PositiveSmallIntegerField()
    # periods_per_year = models.PositiveSmallIntegerField()

    def __str__(self):
        return self.name

# DOCUMENT
class Document(models.Model):
    """
    A document using a template
    e.g. Strategic Plan 2021-2027, Performance Based Bonus 2025
    """

    STATUS_CHOICES = [
        (1, "Active"),
        (2, "Archived"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    template = models.ForeignKey(Template, on_delete=models.CASCADE, related_name="documents")
    reporting_frequency = models.ForeignKey(ReportingFrequency, on_delete=models.SET_NULL, null=True, related_name="documents")
    name = models.CharField(max_length=255)
    short_code = models.CharField(max_length=50, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    start_date = models.DateField(blank=True, null=True) 
    end_date = models.DateField(blank=True, null=True)
    status = models.IntegerField(choices=STATUS_CHOICES, default=1)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # class Meta:
    #     db_table = "documents"

    def __str__(self):
        return f"{self.name} ({self.template.name})"


class Item(models.Model):
    """
    Actual nodes in the framework. Adjacency List model
    e.g. "Improve Student Employability"
    """

    STATUS_CHOICES = [
        (0, "Draft"),
        (1, "Active"),
        (2, "Archive"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    document = models.ForeignKey(Document, on_delete=models.CASCADE, related_name="items")
    template_node_type = models.ForeignKey(TemplateNodeType, on_delete=models.CASCADE, related_name="items")
    parent = models.ForeignKey("self", on_delete=models.CASCADE, related_name="children", null=True, blank=True)
    unit_of_measure = models.ForeignKey(UnitOfMeasure, on_delete=models.CASCADE, related_name="items", blank=True, null=True)
    code = models.CharField(max_length=50)
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    target = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)

    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    status = models.IntegerField(choices=STATUS_CHOICES, default=1)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=["document"]),
            models.Index(fields=["parent"]),
            models.Index(fields=["template_node_type"]),
        ]
        ordering = ["code"]

    def __str__(self):
        return f"{self.name} ({self.template_node_type.name})"
    

class ItemContributor(models.Model):
    """
    Contributor per Item
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    item = models.ForeignKey(Item, on_delete=models.CASCADE, related_name="contributors")
    unit = models.ForeignKey(Unit, on_delete=models.CASCADE, related_name="item_contributions")

    class Meta:
        unique_together = ("item", "unit") 

# Reporting Period and Report Submission
class ReportingPeriod(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    document = models.ForeignKey(Document, on_delete=models.CASCADE, related_name="reporting_periods")
    period_number = models.PositiveIntegerField()
    start_date = models.DateField()
    end_date = models.DateField()
    deadline = models.DateField()
    
    class Meta:
        unique_together = ("document", "period_number")

    def __str__(self):
        return f"{self.document.name} - Period {self.period_number}"


class Initiative(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    item = models.ForeignKey(Item, on_delete=models.CASCADE, related_name="submissions")
    description = models.CharField(max_length=500)
    target_date = models.DateField()
    value = models.DecimalField(max_digits=18, decimal_places=2)
    created_by = models.ForeignKey(User, on_delete=models.PROTECT, related_name="report_submissions")
    unit = models.ForeignKey(Unit, on_delete=models.PROTECT, related_name="initiatives", null=True, blank=True)
    remarks = models.TextField(null=True, blank=True)

    class Meta:
        indexes = [
            models.Index(fields=["item", "description"]),
        ]

    def __str__(self):
        return f"{self.item.name} - Period {self.description}"
    
def initiative_evidence_upload_path(instance, filename):
    upload_dir = settings.PME_EVIDENCE_UPLOAD_TO.strip("/")
    return posixpath.join(upload_dir, filename)


class InitiativeAccomplishment(models.Model):
    STATUS_ACTIVE = 1
    STATUS_REVERTED = 2
    STATUS_CHOICES = [
        (STATUS_ACTIVE, "Active"),
        (STATUS_REVERTED, "Reverted"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    initiative = models.OneToOneField(Initiative, on_delete=models.CASCADE, related_name="accomplishment")
    reporting_period = models.ForeignKey(ReportingPeriod, on_delete=models.CASCADE, related_name="submissions", null=True, blank=True)
    file_path = models.FileField(upload_to=initiative_evidence_upload_path, null=True,  blank=True)
    status = models.PositiveSmallIntegerField(choices=STATUS_CHOICES, default=STATUS_ACTIVE)
    submitted_by = models.ForeignKey(User, on_delete=models.PROTECT, related_name="initiative_accomplishments")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=["initiative", "reporting_period"]),
        ]
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.initiative.description} - Period {self.reporting_period}"


class InitiativeAccomplishmentFile(models.Model):
    STATUS_ACTIVE = 1
    STATUS_REVERTED = 2
    STATUS_CHOICES = [
        (STATUS_ACTIVE, "Active"),
        (STATUS_REVERTED, "Reverted"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    accomplishment = models.ForeignKey(
        InitiativeAccomplishment,
        on_delete=models.CASCADE,
        related_name="files",
        db_column="pia_id",
    )
    file_path = models.FileField(upload_to=initiative_evidence_upload_path)
    status = models.PositiveSmallIntegerField(choices=STATUS_CHOICES, default=STATUS_ACTIVE)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "pme_initiativeaccomplishment_files"
        indexes = [
            models.Index(fields=["accomplishment", "status"]),
        ]
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.accomplishment} - {self.get_status_display()}"
