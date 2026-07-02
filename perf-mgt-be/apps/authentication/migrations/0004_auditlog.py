import uuid
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("authentication", "0003_add_auth_group_is_deleted"),
    ]

    operations = [
        migrations.CreateModel(
            name="AuditLog",
            fields=[
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("user_email", models.EmailField(blank=True, default="", max_length=254)),
                (
                    "module",
                    models.CharField(
                        choices=[
                            ("auth", "Auth"),
                            ("admin", "Admin"),
                            ("pme", "PME"),
                            ("core", "Core"),
                        ],
                        default="admin",
                        max_length=30,
                    ),
                ),
                ("action", models.CharField(max_length=80)),
                ("target_type", models.CharField(blank=True, default="", max_length=80)),
                ("target_id", models.CharField(blank=True, default="", max_length=80)),
                ("target_label", models.CharField(blank=True, default="", max_length=255)),
                ("summary", models.CharField(max_length=500)),
                ("metadata", models.JSONField(blank=True, default=dict)),
                ("ip_address", models.GenericIPAddressField(blank=True, null=True)),
                ("user_agent", models.CharField(blank=True, default="", max_length=500)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                (
                    "user",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="audit_logs",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "ordering": ["-created_at"],
            },
        ),
        migrations.AddIndex(
            model_name="auditlog",
            index=models.Index(fields=["created_at"], name="authenticat_created_d9c5cc_idx"),
        ),
        migrations.AddIndex(
            model_name="auditlog",
            index=models.Index(fields=["action"], name="authenticat_action_a8c1c2_idx"),
        ),
        migrations.AddIndex(
            model_name="auditlog",
            index=models.Index(fields=["target_type"], name="authenticat_target__4d6f81_idx"),
        ),
        migrations.AddIndex(
            model_name="auditlog",
            index=models.Index(fields=["user"], name="authenticat_user_id_3f696a_idx"),
        ),
        migrations.AddIndex(
            model_name="auditlog",
            index=models.Index(fields=["module"], name="authenticat_module_6d8cdf_idx"),
        ),
    ]
