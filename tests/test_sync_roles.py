from io import StringIO

import pytest
from django.contrib.auth.models import Group
from django.core.management import call_command
from django.core.management.base import CommandError
from minosse.roles import AbstractRole
from minosse.roles import RoleRegistry


class EditorRole(AbstractRole):
    group_name = "editors"
    available_permissions = {"can_publish": True, "can_draft": True}


class ViewerRole(AbstractRole):
    group_name = "viewers"
    available_permissions = {"can_read": True}


test_registry = RoleRegistry()
test_registry.register(EditorRole)
test_registry.register(ViewerRole)

empty_registry = RoleRegistry()


class TestRoleRegistry:
    def test_register_adds_role(self):
        reg = RoleRegistry()
        reg.register(EditorRole)
        assert EditorRole in reg.get_roles()

    def test_register_is_idempotent(self):
        reg = RoleRegistry()
        reg.register(EditorRole)
        reg.register(EditorRole)
        assert reg.get_roles().count(EditorRole) == 1

    def test_register_returns_class(self):
        reg = RoleRegistry()
        result = reg.register(EditorRole)
        assert result is EditorRole

    def test_get_roles_returns_all(self):
        reg = RoleRegistry()
        reg.register(EditorRole)
        reg.register(ViewerRole)
        assert set(reg.get_roles()) == {EditorRole, ViewerRole}

    @pytest.mark.django_db
    def test_sync_creates_all_groups(self):
        reg = RoleRegistry()
        reg.register(EditorRole)
        reg.register(ViewerRole)
        groups = reg.sync()
        assert {g.name for g in groups} == {"editors", "viewers"}

    def test_register_as_decorator(self):
        reg = RoleRegistry()

        @reg.register
        class TempRole(AbstractRole):
            available_permissions = {}

        assert TempRole in reg.get_roles()


@pytest.mark.django_db
class TestSyncRolesCommand:
    def _run(self, registry_path=None):
        out = StringIO()
        kwargs = {"stdout": out}
        if registry_path:
            kwargs["registry"] = registry_path
        call_command("sync_roles", **kwargs)
        return out.getvalue()

    def test_syncs_all_registered_roles(self, settings):
        settings.MINOSSE_ROLE_REGISTRY = "tests.test_sync_roles.test_registry"
        output = self._run()
        assert Group.objects.filter(name="editors").exists()
        assert Group.objects.filter(name="viewers").exists()
        assert "Done." in output

    def test_output_shows_permission_count(self, settings):
        settings.MINOSSE_ROLE_REGISTRY = "tests.test_sync_roles.test_registry"
        output = self._run()
        assert "'editors'" in output
        assert "'viewers'" in output

    def test_registry_flag_overrides_settings(self, settings):
        settings.MINOSSE_ROLE_REGISTRY = "tests.test_sync_roles.empty_registry"
        self._run(registry_path="tests.test_sync_roles.test_registry")
        assert Group.objects.filter(name="editors").exists()

    def test_empty_registry_prints_warning(self, settings):
        settings.MINOSSE_ROLE_REGISTRY = "tests.test_sync_roles.empty_registry"
        output = self._run()
        assert "No roles registered" in output

    def test_raises_when_no_registry_configured(self, settings):
        if hasattr(settings, "MINOSSE_ROLE_REGISTRY"):
            del settings.MINOSSE_ROLE_REGISTRY
        with pytest.raises(CommandError, match="No registry configured"):
            self._run()

    def test_raises_on_invalid_import_path(self, settings):
        settings.MINOSSE_ROLE_REGISTRY = "nonexistent.module.registry"
        with pytest.raises(CommandError, match="Could not import registry"):
            self._run()

    def test_raises_when_object_is_not_registry(self, settings):
        settings.MINOSSE_ROLE_REGISTRY = "tests.test_sync_roles.EditorRole"
        with pytest.raises(
            CommandError, match="must be a RoleRegistry instance"
        ):
            self._run()

    def test_sync_is_idempotent(self, settings):
        settings.MINOSSE_ROLE_REGISTRY = "tests.test_sync_roles.test_registry"
        self._run()
        self._run()
        assert Group.objects.filter(name="editors").count() == 1
