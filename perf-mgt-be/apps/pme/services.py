from django.db import transaction
from django.db.models import Exists, OuterRef, Subquery, Prefetch
from django.db.models.functions import Coalesce
from django.utils.timezone import make_aware
from django.utils import timezone
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
    submit_item_ids = set()
    can_submit_all_items = False

    if request and request.user.is_authenticated:
        # Superusers can see all items - skip filtering
        if request.user.is_superuser:
            allowed_item_ids = None
            can_submit_all_items = True

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
                submit_item_ids = set(allowed_item_ids)

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
        accomplishment__status=InitiativeAccomplishment.STATUS_ACTIVE,
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
        node.can_submit_initiative = bool(
            node.target and (
                can_submit_all_items
                or node.id in submit_item_ids
            )
        )

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

# DASHBOARD STATUSES

DASHBOARD_STATUSES = [
    ("on_track", "On Track"),
    ("major_disruption", "Major Disruption"),
    ("completed", "Completed"),
    ("no_update", "No Update"),
]

STATUS_PRIORITY = [
    "major_disruption",
    "no_update",
    "on_track",
    "completed",
]


def status_label(status_key):
    return dict(DASHBOARD_STATUSES).get(status_key, "No Update")


def get_measure_status(item, progress, today):
    if progress >= 100:
        return "completed"

    if progress > 0:
        return "on_track"

    if item.end_date and item.end_date < today:
        return "major_disruption"

    return "no_update"


def get_objective_status(measures):
    if not measures:
        return "no_update"

    statuses = [measure["status"] for measure in measures]

    if all(status == "completed" for status in statuses):
        return "completed"

    for status in STATUS_PRIORITY:
        if status in statuses:
            return status

    return "no_update"


# DASHBOARD OVERALL SUMMARY
def get_dashboard_summary(search=None, sra=None, status=None, document=None, group=None, template=None):
    today = timezone.localdate()
    group_filter = group or sra

    active_documents_base = Document.objects.filter(status=1).select_related("template").order_by("name")
    active_documents = active_documents_base
    if template:
        active_documents = active_documents.filter(template_id=template)

    item_qs = Item.objects.filter(
        document__status=1,
        status=1,
    )

    if template:
        item_qs = item_qs.filter(document__template_id=template)

    if document:
        item_qs = item_qs.filter(document_id=document)

    items = list(
        item_qs
        .select_related("document", "template_node_type", "parent")
        .order_by("code")
    )

    item_map = {item.id: item for item in items}

    measure_ids = [
        item.id for item in items
        if item.target is not None
    ]

    accomplishment_totals = defaultdict(float)
    initiatives = Initiative.objects.filter(
        item_id__in=measure_ids,
        accomplishment__status=InitiativeAccomplishment.STATUS_ACTIVE,
    ).only("item_id", "value")

    for initiative in initiatives:
        accomplishment_totals[initiative.item_id] += float(initiative.value)

    def format_item_label(item):
        return f"{item.code} {item.name}".strip()

    def ancestor_chain(item):
        chain = []
        current = item_map.get(item.parent_id)

        while current:
            chain.append(current)
            current = item_map.get(current.parent_id)

        return chain

    def nearest_card(item):
        for ancestor in ancestor_chain(item):
            if ancestor.target is None:
                return ancestor

        return item

    def nearest_group(card):
        current = item_map.get(card.parent_id)

        while current:
            if current.target is None:
                return current
            current = item_map.get(current.parent_id)

        return None

    cards_map = {}
    card_measures = defaultdict(list)
    card_groups = {}
    measure_cards = {}
    card_type_counts = defaultdict(lambda: defaultdict(int))

    for measure in [item for item in items if item.target is not None]:
        card = nearest_card(measure)
        measure_cards[measure.id] = card
        card_type_counts[measure.document_id][card.template_node_type_id] += 1

    document_card_types = {
        document_id: max(counts, key=counts.get)
        for document_id, counts in card_type_counts.items()
    }

    for measure in [item for item in items if item.target is not None]:
        card = measure_cards[measure.id]

        if card.template_node_type_id != document_card_types.get(measure.document_id):
            continue

        cards_map[card.id] = card
        card_groups[card.id] = nearest_group(card)
        card_measures[card.id].append(measure)

    objectives_payload = []

    for card in sorted(cards_map.values(), key=lambda item: (item.document.name, item.code)):
        objective_group = card_groups.get(card.id)
        measures_payload = []

        for measure in sorted(card_measures[card.id], key=lambda item: item.code):
            target = float(measure.target or 0)
            total = accomplishment_totals[measure.id]
            progress = round((total / target) * 100, 2) if target > 0 else 0
            progress = min(progress, 100)
            measure_status = get_measure_status(measure, progress, today)

            measures_payload.append({
                "id": str(measure.id),
                "code": measure.code,
                "name": measure.name,
                "node_type": measure.template_node_type.name,
                "progress": round(progress),
                "status": measure_status,
                "status_label": status_label(measure_status),
            })

        objective_progress = (
            round(
                sum(measure["progress"] for measure in measures_payload)
                / len(measures_payload)
            )
            if measures_payload
            else 0
        )
        objective_status = get_objective_status(measures_payload)

        objectives_payload.append({
            "id": str(card.id),
            "document_id": str(card.document_id),
            "code": card.code,
            "name": card.name,
            "node_type": card.template_node_type.name,
            "group": {
                "id": str(objective_group.id) if objective_group else None,
                "code": objective_group.code if objective_group else None,
                "name": objective_group.name if objective_group else None,
                "label": (
                    format_item_label(objective_group)
                    if objective_group
                    else None
                ),
            },
            "measure_count": len(measures_payload),
            "progress": objective_progress,
            "main_status": objective_status,
            "main_status_label": status_label(objective_status),
            "measures": measures_payload,
        })

    for objective in objectives_payload:
        objective["sra"] = objective["group"]

    group_options_map = {}
    for objective in objectives_payload:
        objective_group = objective["group"]
        group_id = objective_group["id"]

        if group_id and group_id not in group_options_map:
            group_options_map[group_id] = {
                "value": group_id,
                "label": objective_group["label"],
            }

    group_options = sorted(
        group_options_map.values(),
        key=lambda option: option["label"],
    )
    all_card_node_types = {
        objective["node_type"]
        for objective in objectives_payload
    }
    all_measure_node_types = {
        measure["node_type"]
        for objective in objectives_payload
        for measure in objective["measures"]
    }
    all_group_node_types = {
        card_groups[card.id].template_node_type.name
        for card in cards_map.values()
        if card_groups.get(card.id)
    }

    if search:
        needle = search.lower()
        objectives_payload = [
            objective for objective in objectives_payload
            if needle in f"{objective['code']} {objective['name']}".lower()
            or any(
                needle in f"{measure['code']} {measure['name']}".lower()
                for measure in objective["measures"]
            )
        ]

    if group_filter:
        objectives_payload = [
            objective for objective in objectives_payload
            if objective["group"]["id"] == group_filter
        ]

    if status:
        objectives_payload = [
            objective for objective in objectives_payload
            if objective["main_status"] == status
        ]

    all_measures = [
        measure
        for objective in objectives_payload
        for measure in objective["measures"]
    ]

    status_counts = {
        key: 0
        for key, label in DASHBOARD_STATUSES
    }

    for measure in all_measures:
        status_counts[measure["status"]] += 1

    overall_progress = (
        round(
            sum(measure["progress"] for measure in all_measures)
            / len(all_measures),
            2,
        )
        if all_measures
        else 0
    )

    selected_document = document is not None

    def flexible_label(names, fallback):
        if selected_document and len(names) == 1:
            return next(iter(names))

        return fallback

    group_filter_label = flexible_label(all_group_node_types, "Group")
    card_label = flexible_label(all_card_node_types, "Documents")
    measure_label = flexible_label(all_measure_node_types, "Measure")

    template_options_map = {
        active_document.template_id: {
            "value": str(active_document.template_id),
            "label": active_document.template.name,
        }
        for active_document in active_documents_base
    }

    template_options = sorted(
        template_options_map.values(),
        key=lambda option: option["label"],
    )

    return {
        "measures": len(all_measures),
        "objectives": len(objectives_payload),
        "performance_measures": len(all_measures),
        "overall_progress": overall_progress,
        "status_counts": status_counts,
        **status_counts,
        "document_options": [
            {
                "value": str(active_document.id),
                "label": active_document.name,
                "template": str(active_document.template_id),
                "template_label": active_document.template.name,
            }
            for active_document in active_documents
        ],
        "template_options": template_options,
        "group_options": group_options,
        "group_filter_label": group_filter_label,
        "card_label": card_label,
        "measure_label": measure_label,
        "sra_options": group_options,
        "status_options": [
            {"value": key, "label": label}
            for key, label in DASHBOARD_STATUSES
        ],
        "objectives_list": objectives_payload,
    }
