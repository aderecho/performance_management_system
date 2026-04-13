from django.db import transaction
from django.db.models import Exists, OuterRef, Subquery, Prefetch
from django.db.models.functions import Coalesce
from django.utils.timezone import make_aware
from django.shortcuts import get_object_or_404
from datetime import datetime
from apps.core.models import UserUnit
from apps.pme.models import (
    Item,
    Document,
    ReportingPeriod,
    Initiative,
    InitiativeAccomplishment,
)
from collections import defaultdict
from datetime import timedelta, date
from dateutil.relativedelta import relativedelta



def daterange(start: date, months: int):
    end = (start + relativedelta(months=months)) - timedelta(days=1)
    return start, end


@transaction.atomic
def generate_reporting_periods_for_document(document: Document, periods_ahead=12):
    if not document.reporting_frequency:
        raise ValueError("Document has no reporting frequency.")

    months = document.reporting_frequency.months_interval
    current_start = document.start_date or date.today()

    last = document.reporting_periods.order_by("-period_number").first()
    start_number = last.period_number + 1 if last else 1

    if last:
        current_start = last.end_date + timedelta(days=1)

    created = []

    for i in range(periods_ahead):
        period_number = start_number + i
        start, end = daterange(current_start, months)
        deadline = end + timedelta(days=15)

        rp, is_created = ReportingPeriod.objects.get_or_create(
            document=document,
            start_date=start,
            end_date=end,
            defaults={"period_number": period_number, "deadline": deadline},
        )

        if is_created:
            created.append(rp)

        current_start = end + timedelta(days=1)

    return created


def build_document_item(
    document,
    reporting_period=None,
    item_id=None,
    request=None,
):

    # Resolve allowed items based on contributor
    allowed_item_ids = None

    if request and request.user.is_authenticated:
        # Superusers can see all items - skip filtering
        if request.user.is_superuser:
            allowed_item_ids = None

        else:
            try:
                user_unit = UserUnit.objects.select_related("unit").get(
                    user=request.user,
                    is_primary=True,
                    is_active=True,
                )

                allowed_item_ids = set(
                    Item.objects.filter(
                        document=document,
                        contributors__unit_id=user_unit.unit_id
                    ).values_list("id", flat=True)
                )

            except UserUnit.DoesNotExist:
                allowed_item_ids = set()
    else:
        allowed_item_ids = set()

    # Include ancestors (preserve hierarchy)
    if allowed_item_ids:
        parent_map = dict(
            Item.objects.filter(document=document)
            .values_list("id", "parent_id")
        )

        all_ids = set(allowed_item_ids)

        for item_id_val in list(allowed_item_ids):
            current = item_id_val
            while parent_map.get(current):
                parent_id = parent_map[current]
                all_ids.add(parent_id)
                current = parent_id

        allowed_item_ids = all_ids

    # Load filtered items
    item_qs = Item.objects.filter(document=document)

    if allowed_item_ids is not None:
        item_qs = item_qs.filter(id__in=allowed_item_ids)

    items = list(
        item_qs
        .select_related("unit_of_measure")
        .order_by("code")
    )

    item_map = {item.id: item for item in items}

    children_map = defaultdict(list)
    for item in items:
        children_map[item.parent_id].append(item)

    # Subtree logic
    selected = None
    selected_path = set()
    subtree_ids = set()

    if item_id:
        selected = get_object_or_404(
            Item,
            pk=item_id,
            document=document
        )

        current = selected
        while current:
            selected_path.add(current.id)
            current = item_map.get(current.parent_id)

        stack = [selected.id]
        while stack:
            current = stack.pop()
            subtree_ids.add(current)
            stack.extend([
                child.id for child in children_map[current]
            ])

    # Load initiatives (NO unit filtering here)
    initiatives = Initiative.objects.filter(
        item__document=document,
        accomplishment__isnull=False
    )

    if subtree_ids:
        initiatives = initiatives.filter(item_id__in=subtree_ids)

    if reporting_period:
        initiatives = initiatives.filter(
            accomplishment__reporting_period=reporting_period,
        ).distinct()

    # Aggregate totals
    direct_totals = defaultdict(float)

    for init in initiatives:
        direct_totals[init.item_id] += float(init.value)

    # Build tree with aggregation
    def attach(node):

        if selected:
            if node.id not in selected_path and node.id not in subtree_ids:
                return None

        node.children_cache = []

        for child in children_map[node.id]:
            attached_child = attach(child)
            if attached_child:
                node.children_cache.append(attached_child)

        total = direct_totals.get(node.id, 0)

        for child in node.children_cache:
            total += getattr(child, "total_accomplishment", 0)

        node.total_accomplishment = total

        if node.target:
            node.percent_achieved = round(
                (total / float(node.target)) * 100,
                2
            )
        else:
            node.percent_achieved = None

        return node

    # Root nodes
    root_nodes = children_map[None]

    result = []
    for node in root_nodes:
        attached = attach(node)
        if attached:
            result.append(attached)

    return result, {}

# Get current status of Initiative Accomplishment
def get_current_status(queryset=None):
    if queryset is None:
        queryset = Initiative.objects.all()

    latest_status = InitiativeAccomplishment.objects.filter(
        initiative=OuterRef("pk")
    ).order_by("-created_at").values("created_at")[:1]

    return queryset.annotate(
        current_status=Subquery(latest_status)
    )


def prefetch_latest_submitted_accomplishment():
    return Prefetch(
        "accomplishment",
        queryset=InitiativeAccomplishment.objects
            .filter(created_at__isnull=False)
            .annotate(
                effective_time=Coalesce(
                    "created_at",
                    make_aware(datetime.min)
                )
            )
            .order_by("-effective_time", "-created_at"),
        to_attr="accomplishment_latest"
    )