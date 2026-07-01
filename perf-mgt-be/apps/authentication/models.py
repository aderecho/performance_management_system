import uuid
from django.db import models
from django.contrib.auth.models import BaseUserManager, AbstractBaseUser, PermissionsMixin, Permission

# class User(AbstractUser):
#     id = models.UUIDField(
#         primary_key=True,
#         default=uuid.uuid4,
#         editable=False
#     )

class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("Email is required")

        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        return self.create_user(email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    email = models.EmailField(unique=True)
    denied_permissions = models.ManyToManyField(
        Permission,
        blank=True,
        related_name="denied_user_set",
        verbose_name="denied permissions",
    )

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = UserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    def __str__(self):
        return self.email


class AuditLog(models.Model):
    MODULE_AUTH = "auth"
    MODULE_ADMIN = "admin"
    MODULE_PME = "pme"
    MODULE_CORE = "core"
    MODULE_CHOICES = [
        (MODULE_AUTH, "Auth"),
        (MODULE_ADMIN, "Admin"),
        (MODULE_PME, "PME"),
        (MODULE_CORE, "Core"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="audit_logs",
    )
    user_email = models.EmailField(blank=True, default="")
    module = models.CharField(max_length=30, choices=MODULE_CHOICES, default=MODULE_ADMIN)
    action = models.CharField(max_length=80)
    target_type = models.CharField(max_length=80, blank=True, default="")
    target_id = models.CharField(max_length=80, blank=True, default="")
    target_label = models.CharField(max_length=255, blank=True, default="")
    summary = models.CharField(max_length=500)
    metadata = models.JSONField(default=dict, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.CharField(max_length=500, blank=True, default="")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["created_at"]),
            models.Index(fields=["action"]),
            models.Index(fields=["target_type"]),
            models.Index(fields=["user"]),
            models.Index(fields=["module"]),
        ]

    def __str__(self):
        return f"{self.user_email or 'System'} {self.action} {self.target_label}".strip()
