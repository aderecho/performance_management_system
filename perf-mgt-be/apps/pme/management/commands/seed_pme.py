from datetime import date
from decimal import Decimal

from django.core.management.base import BaseCommand

from apps.core.models import Unit, UnitOfMeasure
from apps.pme.models import (
    Document,
    Item,
    ItemContributor,
    ReportingFrequency,
    Template,
    TemplateNodeType,
)
from apps.pme.services import generate_reporting_periods_for_document


class Command(BaseCommand):
    help = "Seed PME reference and sample data"

    def handle(self, *args, **options):
        template, _ = Template.objects.get_or_create(
            short_code="SP",
            defaults={
                "name": "Strategic Plan",
                "description": "Strategic planning framework",
            },
        )

        sra_type, _ = TemplateNodeType.objects.get_or_create(
            template=template,
            name="Strategic Result Area",
            defaults={
                "short_code": "SRA",
                "description": "Top-level strategic result area",
                "order": 1,
                "is_parent": True,
            },
        )

        objective_type, _ = TemplateNodeType.objects.get_or_create(
            template=template,
            name="Objective",
            defaults={
                "short_code": "OBJ",
                "description": "Strategic objective",
                "order": 2,
                "is_parent": True,
            },
        )

        indicator_type, _ = TemplateNodeType.objects.get_or_create(
            template=template,
            name="Performance Indicator",
            defaults={
                "short_code": "PI",
                "description": "Measurable performance indicator",
                "order": 3,
                "is_parent": False,
            },
        )

        quarterly, _ = ReportingFrequency.objects.get_or_create(
            short_code="QTR",
            defaults={
                "name": "Quarterly",
                "description": "Every 3 months",
                "months_interval": 3,
            },
        )

        document, _ = Document.objects.get_or_create(
            short_code="SP-2026",
            defaults={
                "template": template,
                "reporting_frequency": quarterly,
                "name": "Strategic Plan 2026",
                "description": "Sample strategic plan document",
                "start_date": date(2026, 1, 1),
                "end_date": date(2026, 12, 31),
                "status": 1,
            },
        )

        percentage = UnitOfMeasure.objects.get(short_code="%")
        up_cebu = Unit.objects.get(short_code="UP-Cebu")

        sra, _ = Item.objects.get_or_create(
            document=document,
            code="SRA-1",
            defaults={
                "template_node_type": sra_type,
                "parent": None,
                "unit_of_measure": None,
                "name": "Academic Excellence",
                "description": "Strengthen academic excellence",
                "target": None,
                "start_date": date(2026, 1, 1),
                "end_date": date(2026, 12, 31),
                "status": 1,
            },
        )

        objective, _ = Item.objects.get_or_create(
            document=document,
            code="OBJ-1",
            defaults={
                "template_node_type": objective_type,
                "parent": sra,
                "unit_of_measure": None,
                "name": "Improve student success",
                "description": "Improve student learning and completion outcomes",
                "target": None,
                "start_date": date(2026, 1, 1),
                "end_date": date(2026, 12, 31),
                "status": 1,
            },
        )

        indicator, _ = Item.objects.get_or_create(
            document=document,
            code="PI-1",
            defaults={
                "template_node_type": indicator_type,
                "parent": objective,
                "unit_of_measure": percentage,
                "name": "Student satisfaction rate",
                "description": "Percentage of students satisfied with academic services",
                "target": Decimal("90.00"),
                "start_date": date(2026, 1, 1),
                "end_date": date(2026, 12, 31),
                "status": 1,
            },
        )

        ItemContributor.objects.get_or_create(
            item=indicator,
            unit=up_cebu,
        )

        generate_reporting_periods_for_document(document, periods_ahead=4)

        self.stdout.write(self.style.SUCCESS("PME data seeded successfully."))
