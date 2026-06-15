# Database Engineering Skill

## Purpose
Define database standards for the `perf-mgt-be` Django/PostgreSQL backend, including schema design, Django ORM usage, migrations, seed data, query performance, and database safety.

---

## Current Database Stack

- Database: PostgreSQL
- ORM: Django ORM
- Database Driver: psycopg2-binary
- Migration System: Django migrations
- Seeder System: Django management commands
- Main configuration: `perf-mgt-be/perf_mgt/settings.py`
- Model locations:
  - `perf-mgt-be/apps/authentication/models.py`
  - `perf-mgt-be/apps/core/models.py`
  - `perf-mgt-be/apps/pme/models.py`

---

## Database Configuration

The default database is configured through Django `DATABASES` in `settings.py`:

```python
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.environ.get("POSTGRES_DB", "pm"),
        "USER": os.environ.get("POSTGRES_USER", "itcadmin"),
        "PASSWORD": os.environ.get("POSTGRES_PASSWORD", "ITC1234"),
        "HOST": os.environ.get("POSTGRES_HOST", "127.0.0.1"),
        "PORT": os.environ.get("POSTGRES_PORT", "5432"),
    }
}
```

Rules:

- Keep database configuration environment-driven.
- Do not hard-code new credentials.
- Do not commit `.env` files or secrets.
- Use PostgreSQL-compatible field types and migrations.

---

## Schema And Model Conventions

Domain models generally use UUID primary keys:

```python
id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
```

Use Django model fields and constraints instead of raw SQL schema changes.

Common conventions in this codebase:

- Use `created_at = models.DateTimeField(auto_now_add=True)` for creation timestamps.
- Use `updated_at = models.DateTimeField(auto_now=True)` when update tracking is needed.
- Use `blank=True, null=True` only when both form/API optionality and database nullability are intended.
- Use `DecimalField` for numeric target/accomplishment values.
- Use `DateField` for reporting period and target dates.
- Use `related_name` on relationships for readable reverse access.
- Use `unique=True` or `unique_together` for natural uniqueness rules.

---

## Current Domain Model Map

### Authentication

- `authentication.User`
  - Custom user model.
  - UUID primary key.
  - Unique `email`.
  - Uses email as `USERNAME_FIELD`.

### Core

- `Profile`
  - One-to-one profile for `settings.AUTH_USER_MODEL`.
- `Unit`
  - Organizational unit.
  - Supports parent/child hierarchy with `parent = ForeignKey("self")`.
  - Unique `short_code`.
- `UnitOfMeasure`
  - Shared unit of measure reference data.
  - Unique `short_code`.
- `UserUnit`
  - Links users to units.
  - Uses `is_primary` and `is_active`.
  - Unique per `(user, unit)`.

### PME

- `Template`
  - Framework definition, such as Strategic Plan or PBB.
- `TemplateNodeType`
  - Allowed item/node types for a template.
  - Unique per `(template, name)`.
- `ReportingFrequency`
  - Reporting interval definition.
- `Document`
  - A concrete PME document using a template.
- `Item`
  - Hierarchical PME node using adjacency list through `parent`.
  - Performance measures are items with a `target`.
- `ItemContributor`
  - Links contributing units to items.
  - Unique per `(item, unit)`.
- `ReportingPeriod`
  - Generated reporting period for a document.
  - Unique per `(document, period_number)`.
- `Initiative`
  - Planned initiative/accomplishment value for an item.
- `InitiativeAccomplishment`
  - One-to-one accomplishment marker for an initiative.

---

## Relationship Rules

Use Django relationships directly:

- `ForeignKey` for many-to-one relationships.
- `OneToOneField` for one-to-one relationships.
- Self-referential `ForeignKey("self")` for hierarchies.
- `related_name` for reverse access.

Use `settings.AUTH_USER_MODEL` for user relations:

```python
from django.conf import settings

user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
```

Respect existing `on_delete` behavior:

- `CASCADE` when child data should be removed with the parent.
- `PROTECT` when related records must prevent deletion, such as submitted/created-by user references.
- `SET_NULL` when the relation is optional and historical data can remain without the referenced row.

For PME hierarchy, follow the existing adjacency-list model:

```python
parent = models.ForeignKey(
    "self",
    on_delete=models.CASCADE,
    related_name="children",
    null=True,
    blank=True,
)
```

Do not introduce MPTT, closure tables, or a second hierarchy model unless explicitly planned.

---

## Migration Rules

Use Django migrations for every schema change.

Commands:

```bash
python manage.py makemigrations
python manage.py migrate
```

Verification command:

```bash
python manage.py makemigrations --check
```

Rules:

- Do not manually edit historical migrations unless explicitly requested.
- Keep each migration focused on a clear schema change.
- Review generated migrations before applying them.
- Include data migrations only when the schema change requires data backfill or transformation.
- Do not drop tables, remove relations, rename fields, or change primary key types without explicit approval.
- Keep migrations compatible with PostgreSQL.

---

## Seeder Rules

Seed commands live under:

```text
apps/<app>/management/commands/
```

Current seed flow:

```bash
python manage.py seed
```

App-level seed commands include:

```bash
python manage.py seed_core
python manage.py seed_users
python manage.py seed_pme
```

Rules:

- Keep seeders idempotent with `get_or_create()` or equivalent safeguards.
- Use seeders for reference data, local development data, and repeatable demos.
- Do not seed sensitive production credentials.
- Update seeders when required reference models or fields change.
- Avoid destructive seed behavior unless explicitly requested.

---

## Indexing And Query Performance

Prefer Django ORM optimization patterns:

- Use `select_related()` for foreign keys and one-to-one relationships.
- Use `prefetch_related()` for reverse relationships and many-related records.
- Use `models.Index` for common filters and sort patterns.
- Use aggregation when computing totals across many records.
- Use `.values()` or `.values_list()` when only primitive fields are needed.

Current PME index examples:

- `Item` indexes `document`, `parent`, and `template_node_type`.
- `Initiative` indexes `item` and `description`.
- `InitiativeAccomplishment` indexes `initiative` and `reporting_period`.

Avoid:

- Querying inside loops when prefetching or aggregation can solve it.
- Loading entire model rows when only ids or a few fields are needed.
- Large unfiltered list endpoints.
- Repeating expensive aggregate logic in views.

---

## Transactions And Consistency

Use `transaction.atomic()` for multi-write workflows or generated data that must stay consistent.

Good candidates:

- Generating reporting periods.
- Creating related records across models.
- Data migrations.
- Bulk updates with dependent changes.

Rules:

- Roll back the full workflow on failure.
- Keep transaction scopes as small as practical.
- Avoid long-running external calls inside database transactions.

---

## Security And Configuration

Rules:

- Never commit database credentials, `.env` files, dumps, or secrets.
- Keep database connection values in environment variables.
- Use Django ORM parameterization instead of raw string-built SQL.
- Validate inputs through serializers/forms before database writes.
- Do not expose database errors directly to users.
- Avoid logging sensitive data, tokens, or credentials.

Raw SQL is allowed only when Django ORM cannot reasonably express the operation. When raw SQL is needed, parameterize it and document why it exists.

---

## Verification Commands

Run from `perf-mgt-be/`.

For schema changes:

```bash
python manage.py makemigrations --check
python manage.py migrate
```

For backend behavior:

```bash
python manage.py test
```

For seed verification:

```bash
python manage.py seed
```

When only documentation changes, no database command is required.

---

## AI Agent Instructions

Before database changes:

1. Inspect existing models and migrations.
2. Confirm the affected app and domain boundary.
3. Check existing relationships, constraints, and `on_delete` behavior.
4. Decide whether the change needs a schema migration, data migration, or seed update.
5. Consider API and frontend response impact before changing model fields.

Before finishing database work:

1. Review generated migrations.
2. Run migration checks.
3. Run relevant backend tests.
4. Verify indexes and query patterns for changed workflows.
5. Confirm seed commands still work if reference data changed.

Never:

- Replace Django ORM conventions with Laravel/MySQL conventions.
- Drop critical tables or columns without explicit approval.
- Change UUID primary key strategy without explicit approval.
- Duplicate existing relational structures.
- Add raw SQL casually.
- Commit credentials, dumps, or local database artifacts.
