from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group, Permission
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import RefreshToken

from apps.core.models import Profile


User = get_user_model()


class CookieJWTAuthTests(APITestCase):
    password = "Password12345"

    def setUp(self):
        self.user = User.objects.create_user(
            email="auth-user@example.com",
            password=self.password,
            is_active=True,
        )
        Profile.objects.create(
            user=self.user,
            first_name="Auth",
            last_name="User",
        )

    def login(self):
        return self.client.post(
            reverse("login"),
            {
                "email": self.user.email,
                "password": self.password,
            },
            format="json",
        )

    def assert_jwt_cookie(self, response, key, max_age):
        self.assertIn(key, response.cookies)
        cookie = response.cookies[key]
        self.assertEqual(cookie["httponly"], True)
        self.assertEqual(cookie["secure"], settings.SESSION_COOKIE_SECURE)
        self.assertEqual(cookie["samesite"], "Lax")
        self.assertEqual(cookie["path"], "/")
        self.assertEqual(cookie["max-age"], str(max_age))

    def test_login_sets_http_only_access_and_refresh_cookies(self):
        response = self.login()

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json(), {"message": "Login successful"})
        self.assert_jwt_cookie(
            response,
            "access_token",
            int(settings.SIMPLE_JWT["ACCESS_TOKEN_LIFETIME"].total_seconds()),
        )
        self.assert_jwt_cookie(
            response,
            "refresh_token",
            int(settings.SIMPLE_JWT["REFRESH_TOKEN_LIFETIME"].total_seconds()),
        )

    def test_invalid_login_does_not_set_jwt_cookies(self):
        response = self.client.post(
            reverse("login"),
            {
                "email": self.user.email,
                "password": "wrong-password",
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertNotIn("access_token", response.cookies)
        self.assertNotIn("refresh_token", response.cookies)

    def test_session_succeeds_with_access_cookie(self):
        self.login()

        response = self.client.get(reverse("session"))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["active"], True)
        self.assertEqual(response.data["user"]["email"], self.user.email)

    def test_refresh_sets_new_access_cookie(self):
        self.login()

        response = self.client.post(reverse("refresh"))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json(), {"message": "Token refreshed"})
        self.assert_jwt_cookie(
            response,
            "access_token",
            int(settings.SIMPLE_JWT["ACCESS_TOKEN_LIFETIME"].total_seconds()),
        )

    def test_refresh_rotation_sets_new_refresh_cookie(self):
        login_response = self.login()
        original_refresh_token = login_response.cookies["refresh_token"].value

        response = self.client.post(reverse("refresh"))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assert_jwt_cookie(
            response,
            "refresh_token",
            int(settings.SIMPLE_JWT["REFRESH_TOKEN_LIFETIME"].total_seconds()),
        )
        self.assertNotEqual(
            response.cookies["refresh_token"].value,
            original_refresh_token,
        )

    def test_missing_refresh_cookie_returns_unauthorized(self):
        self.client.cookies.clear()

        response = self.client.post(reverse("refresh"))

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data, {"error": "No refresh token"})

    def test_logout_clears_jwt_cookies(self):
        self.login()

        response = self.client.post(reverse("logout"))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, {"detail": "Successfully logged out."})
        self.assertEqual(response.cookies["access_token"]["max-age"], 0)
        self.assertEqual(response.cookies["refresh_token"]["max-age"], 0)
        self.assertEqual(response.cookies["access_token"]["samesite"], "Lax")
        self.assertEqual(response.cookies["refresh_token"]["samesite"], "Lax")

    def test_logged_out_session_fails(self):
        self.login()
        self.client.post(reverse("logout"))

        response = self.client.get(reverse("session"))

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_logout_tolerates_invalid_refresh_cookie(self):
        access_token = RefreshToken.for_user(self.user).access_token
        self.client.cookies["access_token"] = str(access_token)
        self.client.cookies["refresh_token"] = "invalid-refresh-token"

        response = self.client.post(reverse("logout"))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, {"detail": "Successfully logged out."})


class RolePermissionCookieAuthTests(APITestCase):
    password = "Password12345"

    def create_user(self, email, permissions=None, is_superuser=False):
        user = User.objects.create_user(
            email=email,
            password=self.password,
            is_active=True,
            is_staff=is_superuser,
            is_superuser=is_superuser,
        )
        Profile.objects.create(
            user=user,
            first_name="Role",
            last_name="Tester",
        )
        if permissions:
            user.user_permissions.set(permissions)
        return user

    def login_as(self, user):
        self.client.cookies.clear()
        response = self.client.post(
            reverse("login"),
            {
                "email": user.email,
                "password": self.password,
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access_token", response.cookies)
        return response

    def get_permission(self, codename, app_label="auth"):
        return Permission.objects.get(
            content_type__app_label=app_label,
            codename=codename,
        )

    def test_unauthenticated_role_list_returns_unauthorized(self):
        response = self.client.get(reverse("role-list"))

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_authenticated_user_without_role_view_permission_gets_forbidden(self):
        user = self.create_user("no-role-view@example.com")
        self.login_as(user)

        response = self.client.get(reverse("role-list"))

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_user_with_role_view_permission_can_list_roles(self):
        user = self.create_user(
            "role-view@example.com",
            permissions=[self.get_permission("view_group")],
        )
        Group.objects.create(name="Reviewer")
        self.login_as(user)

        response = self.client.get(reverse("role-list"))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data), 1)

    def test_user_with_role_add_permission_can_create_role(self):
        user = self.create_user(
            "role-add@example.com",
            permissions=[self.get_permission("add_group")],
        )
        self.login_as(user)

        response = self.client.post(
            reverse("role-list"),
            {"name": "Role Creator"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Group.objects.filter(name="Role Creator").exists())

    def test_user_without_role_change_permission_cannot_update_role(self):
        user = self.create_user(
            "role-view-only@example.com",
            permissions=[self.get_permission("view_group")],
        )
        role = Group.objects.create(name="Existing Role")
        self.login_as(user)

        response = self.client.put(
            reverse("role-detail", kwargs={"pk": role.pk}),
            {"name": "Changed Role"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        role.refresh_from_db()
        self.assertEqual(role.name, "Existing Role")

    def test_user_with_role_delete_permission_can_toggle_role_status(self):
        user = self.create_user(
            "role-delete@example.com",
            permissions=[self.get_permission("delete_group")],
        )
        role = Group.objects.create(name="Status Role")
        self.login_as(user)

        response = self.client.patch(
            reverse("role-detail", kwargs={"pk": role.pk}),
            {"is_deleted": True},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["is_deleted"], True)

    def test_user_with_only_role_change_permission_cannot_toggle_role_status(self):
        user = self.create_user(
            "role-change-only@example.com",
            permissions=[self.get_permission("change_group")],
        )
        role = Group.objects.create(name="Status Denied Role")
        self.login_as(user)

        response = self.client.patch(
            reverse("role-detail", kwargs={"pk": role.pk}),
            {"is_deleted": True},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_unauthenticated_permission_list_returns_unauthorized(self):
        response = self.client.get(reverse("permission-list"))

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_user_with_permission_view_permission_can_list_permissions(self):
        user = self.create_user(
            "permission-view@example.com",
            permissions=[self.get_permission("view_permission")],
        )
        self.login_as(user)

        response = self.client.get(reverse("permission-list"))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data), 1)

    def test_user_with_role_change_permission_can_list_permissions_for_role_form(self):
        user = self.create_user(
            "role-permission-editor@example.com",
            permissions=[self.get_permission("change_group")],
        )
        self.login_as(user)

        response = self.client.get(reverse("permission-list"))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data), 1)

    def test_user_with_only_role_view_permission_cannot_list_permission_catalog(self):
        user = self.create_user(
            "role-view-permission-denied@example.com",
            permissions=[self.get_permission("view_group")],
        )
        self.login_as(user)

        response = self.client.get(reverse("permission-list"))

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_denied_permission_removes_role_grant_from_session_and_api_access(self):
        permission = self.get_permission("view_permission")
        role = Group.objects.create(name="Permission Viewer")
        role.permissions.set([permission])
        user = self.create_user("permission-denied@example.com")
        user.groups.set([role])
        user.denied_permissions.set([permission])
        self.login_as(user)

        session_response = self.client.get(reverse("session"))
        permission_response = self.client.get(reverse("permission-list"))

        self.assertEqual(session_response.status_code, status.HTTP_200_OK)
        self.assertNotIn(
            "auth.view_permission",
            session_response.data["user"]["permissions"],
        )
        self.assertEqual(permission_response.status_code, status.HTTP_403_FORBIDDEN)

    def test_direct_permission_still_grants_permission_without_deny(self):
        user = self.create_user(
            "permission-direct@example.com",
            permissions=[self.get_permission("view_permission")],
        )
        self.login_as(user)

        session_response = self.client.get(reverse("session"))
        permission_response = self.client.get(reverse("permission-list"))

        self.assertEqual(session_response.status_code, status.HTTP_200_OK)
        self.assertIn(
            "auth.view_permission",
            session_response.data["user"]["permissions"],
        )
        self.assertEqual(permission_response.status_code, status.HTTP_200_OK)

    def test_denied_permission_overrides_direct_permission(self):
        permission = self.get_permission("view_permission")
        user = self.create_user(
            "permission-direct-denied@example.com",
            permissions=[permission],
        )
        user.denied_permissions.set([permission])
        self.login_as(user)

        session_response = self.client.get(reverse("session"))
        permission_response = self.client.get(reverse("permission-list"))

        self.assertEqual(session_response.status_code, status.HTTP_200_OK)
        self.assertNotIn(
            "auth.view_permission",
            session_response.data["user"]["permissions"],
        )
        self.assertEqual(permission_response.status_code, status.HTTP_403_FORBIDDEN)

    def test_user_payload_exposes_role_direct_and_denied_permission_ids(self):
        actor = self.create_user(
            "user-list-actor@example.com",
            permissions=[self.get_permission("view_user", app_label="authentication")],
        )
        role_permission = self.get_permission("view_permission")
        direct_permission = self.get_permission("add_permission")
        denied_permission = self.get_permission("delete_permission")
        role = Group.objects.create(name="Payload Role")
        role.permissions.set([role_permission])
        target = self.create_user(
            "permission-payload@example.com",
            permissions=[direct_permission],
        )
        target.groups.set([role])
        target.denied_permissions.set([denied_permission])
        self.login_as(actor)

        response = self.client.get(reverse("user-list"))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        row = next(item for item in response.data if item["id"] == str(target.id))
        self.assertIn(role_permission.id, row["role_permission_ids"])
        self.assertEqual(row["direct_permission_ids"], [direct_permission.id])
        self.assertEqual(row["denied_permission_ids"], [denied_permission.id])
        self.assertIn("auth.view_permission", row["effective_permissions"])
        self.assertIn("auth.add_permission", row["effective_permissions"])
        self.assertNotIn("auth.delete_permission", row["effective_permissions"])

    def test_superuser_can_access_role_and_permission_endpoints(self):
        user = self.create_user(
            "superuser@example.com",
            is_superuser=True,
        )
        self.login_as(user)

        role_response = self.client.get(reverse("role-list"))
        permission_response = self.client.get(reverse("permission-list"))

        self.assertEqual(role_response.status_code, status.HTTP_200_OK)
        self.assertEqual(permission_response.status_code, status.HTTP_200_OK)

    def test_user_with_user_delete_permission_can_toggle_user_status(self):
        actor = self.create_user(
            "user-delete@example.com",
            permissions=[self.get_permission("delete_user", app_label="authentication")],
        )
        target = self.create_user("status-target@example.com")
        self.login_as(actor)

        response = self.client.patch(
            reverse("user-detail", kwargs={"pk": target.pk}),
            {"is_active": False},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        target.refresh_from_db()
        self.assertFalse(target.is_active)

    def test_user_with_only_user_change_permission_cannot_toggle_user_status(self):
        actor = self.create_user(
            "user-change-only@example.com",
            permissions=[self.get_permission("change_user", app_label="authentication")],
        )
        target = self.create_user("status-denied@example.com")
        self.login_as(actor)

        response = self.client.patch(
            reverse("user-detail", kwargs={"pk": target.pk}),
            {"is_active": False},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        target.refresh_from_db()
        self.assertTrue(target.is_active)

    def test_user_with_user_change_permission_can_update_user_details(self):
        actor = self.create_user(
            "user-change@example.com",
            permissions=[self.get_permission("change_user", app_label="authentication")],
        )
        target = self.create_user("change-target@example.com")
        self.login_as(actor)

        response = self.client.patch(
            reverse("user-detail", kwargs={"pk": target.pk}),
            {"email": "changed-target@example.com"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        target.refresh_from_db()
        self.assertEqual(target.email, "changed-target@example.com")
