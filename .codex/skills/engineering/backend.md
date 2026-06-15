# Backend Development Skill

## Purpose
Handle backend work for the `perf-mgt-be` Django API, including API development, authentication, validation, database access, seeders, and server-side business logic.

---

## Current Backend Stack

- Language: Python 3.12+
- Framework: Django 5.2.10
- API Framework: Django REST Framework 3.16.1
- Database: PostgreSQL
- Database Driver: psycopg2-binary
- Authentication: Simple JWT with HttpOnly cookie authentication
- CORS: django-cors-headers
- Import / Export: django-import-export
- Caching Packages: Redis, django-redis
- Data Processing: pandas
- Production Server: Gunicorn
- Dependency File: `requirements.txt`

---

## Repository Layout

Backend root:

```text
perf-mgt-be/
+-- manage.py
+-- requirements.txt
+-- perf_mgt/
|   +-- settings.py
|   +-- urls.py
|   +-- asgi.py
|   +-- wsgi.py
+-- apps/
    +-- authentication/
    +-- core/
    +-- pme/
```

Per-app pattern:

```text
apps/<app_name>/
+-- models.py
+-- serializers.py
+-- views.py
+-- services.py
+-- urls.py
+-- admin.py
+-- tests.py
+-- migrations/
+-- management/commands/
```

---

## Domain Apps

### `apps.authentication`

Responsible for:

- Custom email-based `User`
- Login, logout, refresh token, and session check
- Cookie-based JWT authentication
- User API endpoints
- User dashboard stats

Important conventions:

- Use `AUTH_USER_MODEL = "authentication.User"`.
- Users authenticate by `email`, not username.
- JWT access and refresh tokens are stored in HttpOnly cookies.
- Use `CookieJWTAuthentication` for authenticated API requests.

### `apps.core`

Responsible for shared reference data:

- `Profile`
- `Unit`
- `UnitOfMeasure`
- `UserUnit`

Important conventions:

- `Profile` is linked one-to-one with the user.
- `UserUnit` links users to units.
- `is_primary=True` and `is_active=True` identifies the user's active primary unit.

### `apps.pme`

Responsible for performance management entities:

- `Template`
- `TemplateNodeType`
- `ReportingFrequency`
- `Document`
- `Item`
- `ItemContributor`
- `ReportingPeriod`
- `Initiative`
- `InitiativeAccomplishment`

Important conventions:

- PME hierarchy is represented by `Item.parent`.
- Measurable performance indicators are `Item` records with a `target`.
- Accomplishment/progress logic belongs in `apps.pme.services`.
- Unit authorization should follow `UserUnit` and `ItemContributor`.

---

## API Design Rules

Use Django REST Framework patterns already present in the repo.

Prefer:

- `ModelViewSet` for standard CRUD resources.
- `APIView` for custom endpoints.
- `@action` for resource-specific custom actions.
- App-local `urls.py` files included by `perf_mgt/urls.py`.

Main API prefixes:

```text
/api/v1/auth/
/api/v1/core/
/api/v1/pme/
```

HTTP method conventions:

- `GET` for fetching data
- `POST` for creating data or command-style actions
- `PUT` for full replacement
- `PATCH` for partial update
- `DELETE` for removal or revert actions

Avoid action-style route names such as:

```text
/getUsers
/createDocument
```

Prefer resource-style routes such as:

```text
/users/
/documents/
/documents/<id>/items/
```

---

## Services And Business Logic

Keep business logic out of views when it is more than simple request handling.

Use `services.py` for:

- Dashboard/stat calculations
- PME hierarchy building
- Progress calculations
- Reporting period generation
- Cross-model workflows
- Reusable domain rules

Views should usually:

1. Read request data or query params.
2. Call serializers/services.
3. Return a DRF `Response`.

Example pattern:

```python
class DashboardSummaryView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response(get_dashboard_summary())
```

---

## Serializers And Validation

Use serializers for API input/output shape and validation.

Serializer responsibilities:

- Validate request payloads.
- Define read-only fields.
- Expose related display fields.
- Hide internal-only fields.
- Format nested API output where needed.

Use:

```python
serializers.ValidationError
```

for request validation errors.

Prefer explicit serializer fields for API contracts when the response shape matters. Use `fields = "__all__"` only for simple internal/reference resources.

---

## Authentication And Permissions

Default authentication comes from:

```python
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "apps.authentication.authentication.CookieJWTAuthentication",
    ),
    "DEFAULT_PERMISSION_CLASSES": (
        "rest_framework.permissions.IsAuthenticated",
    ),
}
```

Rules:

- Use `IsAuthenticated` for protected endpoints.
- Use `AllowAny` only for login, logout, refresh, or public endpoints.
- Use `IsAuthenticatedOrReadOnly` only when anonymous reads are intentional.
- Do not expose JWT tokens in logs.
- Do not store tokens in local storage on the frontend.
- Keep JWT cookies HttpOnly.
- Keep CORS and CSRF settings aligned with `settings.py`.

---

## Database And Query Rules

Use Django ORM by default.

Prefer:

- UUID primary keys for domain models.
- `select_related()` for foreign keys and one-to-one relations.
- `prefetch_related()` for reverse and many-related relations.
- `transaction.atomic()` for multi-write workflows.
- Model indexes for frequent filters.
- `get_object_or_404()` for object lookup in views/services where appropriate.

Avoid:

- Raw SQL unless clearly necessary.
- N+1 query patterns.
- Repeating expensive aggregation logic in views.
- Querying inside loops when aggregation or prefetching can solve it.

---

## Seeding And Migrations

Seed commands live under:

```text
apps/<app>/management/commands/
```

Current seed flow:

```bash
python manage.py seed
```

which calls app-specific seeders such as:

```bash
python manage.py seed_core
python manage.py seed_users
python manage.py seed_pme
```

Rules:

- Use migrations for schema changes.
- Keep seeders idempotent with `get_or_create()` or equivalent safeguards.
- Do not hard-delete important seeded reference data without explicit instruction.
- When adding model fields, create migrations and update seed data if needed.

---

## Error Handling Rules

Use DRF-native errors where possible.

Prefer:

```python
raise ValidationError("Message")
```

or:

```python
return Response(
    {"detail": "Message"},
    status=status.HTTP_400_BAD_REQUEST,
)
```

Keep response formats consistent with existing DRF conventions.

Do not expose:

- stack traces
- database credentials
- tokens
- internal secrets

---

## Testing And Verification

For backend changes, prefer running:

```bash
python manage.py test
```

For migration changes, also run:

```bash
python manage.py makemigrations --check
python manage.py migrate
```

Important flows to test:

- Login/logout/session refresh
- User/profile/unit relationships
- PME document hierarchy
- Initiative creation authorization
- Accomplishment submission/revert
- Dashboard/progress calculations

---

## Refactoring Rules

When refactoring:

- Preserve existing API response shapes unless intentionally changing them.
- Keep views thin.
- Move reusable rules into `services.py`.
- Keep serializers focused on API contracts.
- Do not mix frontend-specific naming into backend models.
- Prefer small, scoped changes.
- Update tests or seed data when behavior changes.

---

## AI Agent Instructions

Before coding:

1. Inspect existing app patterns first.
2. Reuse existing serializers, services, and viewset patterns.
3. Check `settings.py`, app `urls.py`, and related models before adding endpoints.
4. Decide whether logic belongs in a serializer, service, view, or model.
5. Preserve authentication and permission behavior.

Before finishing:

1. Run relevant backend tests.
2. Check migrations when models changed.
3. Review query performance for N+1 issues.
4. Confirm response shape matches frontend expectations.
5. Check for accidental secrets, tokens, or debug prints.

Never:

- Add a second authentication pattern without explicit need.
- Put complex business calculations directly in views.
- Bypass serializers for request validation.
- Introduce raw SQL casually.
- Commit `.env` files or secrets.
- Silently change public API response shapes.
