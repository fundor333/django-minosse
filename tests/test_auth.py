import pytest
from django.contrib.auth.models import AnonymousUser
from django.contrib.auth.models import User
from django.core.exceptions import PermissionDenied
from django.http import HttpResponse
from django.test import RequestFactory
from django.views import View
from minosse.decorator import permission_required
from minosse.decorator import role_required
from minosse.mixin import PermissionRequiredMixin
from minosse.mixin import RoleRequiredMixin
from minosse.roles import AbstractRole


class AdminRole(AbstractRole):
    app_label = "minosse"
    available_permissions = {"can_admin": True}


class EditorRole(AbstractRole):
    app_label = "minosse"
    available_permissions = {"can_edit_content": True}


def simple_view(request):
    return HttpResponse("ok")


class SimpleView(View):
    def get(self, request, *args, **kwargs):
        return HttpResponse("ok")


@pytest.mark.django_db
class TestRoleRequiredDecorator:
    def setup_method(self):
        self.factory = RequestFactory()
        self.view = role_required(AdminRole)(simple_view)

    def test_allows_user_with_role(self):
        user = User.objects.create_user(username="admin", password="pass")
        AdminRole.add_user_to_role(user)
        request = self.factory.get("/")
        request.user = user
        assert self.view(request).status_code == 200

    def test_raises_permission_denied_for_authenticated_without_role(self):
        user = User.objects.create_user(username="other", password="pass")
        request = self.factory.get("/")
        request.user = user
        with pytest.raises(PermissionDenied):
            self.view(request)

    def test_raises_permission_denied_for_anonymous(self):
        request = self.factory.get("/")
        request.user = AnonymousUser()
        with pytest.raises(PermissionDenied):
            self.view(request)

    def test_preserves_view_function_name(self):
        assert role_required(AdminRole)(simple_view).__name__ == "simple_view"


@pytest.mark.django_db
class TestPermissionRequiredDecorator:
    def setup_method(self):
        self.factory = RequestFactory()
        self.view = permission_required("minosse.can_edit_content")(
            simple_view
        )

    def test_allows_user_with_permission(self):
        user = User.objects.create_user(username="editor", password="pass")
        EditorRole.add_user_to_role(user)
        user = User.objects.get(pk=user.pk)  # clear Django's permission cache
        request = self.factory.get("/")
        request.user = user
        assert self.view(request).status_code == 200

    def test_raises_permission_denied_without_permission(self):
        user = User.objects.create_user(username="viewer", password="pass")
        request = self.factory.get("/")
        request.user = user
        with pytest.raises(PermissionDenied):
            self.view(request)

    def test_raises_permission_denied_for_anonymous(self):
        request = self.factory.get("/")
        request.user = AnonymousUser()
        with pytest.raises(PermissionDenied):
            self.view(request)

    def test_preserves_view_function_name(self):
        assert (
            permission_required("any.perm")(simple_view).__name__
            == "simple_view"
        )


@pytest.mark.django_db
class TestRoleRequiredMixin:
    def setup_method(self):
        self.factory = RequestFactory()

    def _make_view(self, role_class):
        class TestView(RoleRequiredMixin, SimpleView):
            required_role_class = role_class

        return TestView.as_view()

    def test_allows_user_with_role(self):
        user = User.objects.create_user(username="admin2", password="pass")
        AdminRole.add_user_to_role(user)
        request = self.factory.get("/")
        request.user = user
        assert self._make_view(AdminRole)(request).status_code == 200

    def test_raises_permission_denied_for_authenticated_without_role(self):
        user = User.objects.create_user(username="norole", password="pass")
        request = self.factory.get("/")
        request.user = user
        with pytest.raises(PermissionDenied):
            self._make_view(AdminRole)(request)

    def test_redirects_anonymous_user(self):
        request = self.factory.get("/protected/")
        request.user = AnonymousUser()
        response = self._make_view(AdminRole)(request)
        assert response.status_code == 302

    def test_raises_value_error_when_role_class_not_set(self):
        class MisconfiguredView(RoleRequiredMixin, SimpleView):
            pass

        request = self.factory.get("/")
        request.user = AnonymousUser()
        with pytest.raises(ValueError):
            MisconfiguredView.as_view()(request)


@pytest.mark.django_db
class TestPermissionRequiredMixin:
    def setup_method(self):
        self.factory = RequestFactory()

    def _make_view(self, perm):
        class TestView(PermissionRequiredMixin, SimpleView):
            required_permission_codename = perm

        return TestView.as_view()

    def test_allows_user_with_permission(self):
        user = User.objects.create_user(username="editor2", password="pass")
        EditorRole.add_user_to_role(user)
        user = User.objects.get(pk=user.pk)  # clear Django's permission cache
        request = self.factory.get("/")
        request.user = user
        assert (
            self._make_view("minosse.can_edit_content")(request).status_code
            == 200
        )

    def test_raises_permission_denied_for_authenticated_without_permission(
        self,
    ):
        user = User.objects.create_user(username="noperm", password="pass")
        request = self.factory.get("/")
        request.user = user
        with pytest.raises(PermissionDenied):
            self._make_view("minosse.can_edit_content")(request)

    def test_redirects_anonymous_user(self):
        request = self.factory.get("/protected/")
        request.user = AnonymousUser()
        response = self._make_view("minosse.can_edit_content")(request)
        assert response.status_code == 302

    def test_raises_value_error_when_codename_not_set(self):
        class MisconfiguredView(PermissionRequiredMixin, SimpleView):
            pass

        request = self.factory.get("/")
        request.user = AnonymousUser()
        with pytest.raises(ValueError):
            MisconfiguredView.as_view()(request)
