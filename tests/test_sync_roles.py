from io import StringIO

import pytest
from django.contrib.auth.models import Group
from django.core.management import call_command
from minosse.roles import AbstractRole
from minosse.roles import RoleRegistry


class EditorRole(AbstractRole):
    group_name = "editors"
    available_permissions = {"can_publish": True, "can_draft": True}


class ViewerRole(AbstractRole):
    group_name = "viewers"
    available_permissions = {"can_read": True}


@pytest.fixture(autouse=True)
def reset_registry():
    RoleRegistry()._reset()
    yield
    RoleRegistry()._reset()


class TestRoleRegistry:
    def test_is_singleton(self):
        assert RoleRegistry() is RoleRegistry()

    def test_register_adds_role(self):
        RoleRegistry().register(EditorRole)
        assert EditorRole in RoleRegistry().get_roles()

    def test_register_is_idempotent(self):
        RoleRegistry().register(EditorRole)
        RoleRegistry().register(EditorRole)
        assert RoleRegistry().get_roles().count(EditorRole) == 1

    def test_register_returns_class(self):
        result = RoleRegistry().register(EditorRole)
        assert result is EditorRole

    def test_get_roles_returns_all(self):
        RoleRegistry().register(EditorRole)
        RoleRegistry().register(ViewerRole)
        assert set(RoleRegistry().get_roles()) == {EditorRole, ViewerRole}

    @pytest.mark.django_db
    def test_sync_creates_all_groups(self):
        RoleRegistry().register(EditorRole)
        RoleRegistry().register(ViewerRole)
        groups = RoleRegistry().sync()
        assert {g.name for g in groups} == {"editors", "viewers"}

    def test_register_as_decorator(self):
        @RoleRegistry().register
        class TempRole(AbstractRole):
            available_permissions = {}

        assert TempRole in RoleRegistry().get_roles()

    def test_reset_clears_all_roles(self):
        RoleRegistry().register(EditorRole)
        RoleRegistry()._reset()
        assert RoleRegistry().get_roles() == []


@pytest.mark.django_db
class TestSyncRolesCommand:
    def _run(self):
        out = StringIO()
        call_command("sync_roles", stdout=out)
        return out.getvalue()

    def test_syncs_all_registered_roles(self):
        RoleRegistry().register(EditorRole)
        RoleRegistry().register(ViewerRole)
        output = self._run()
        assert Group.objects.filter(name="editors").exists()
        assert Group.objects.filter(name="viewers").exists()
        assert "Done." in output

    def test_output_shows_permission_count(self):
        RoleRegistry().register(EditorRole)
        RoleRegistry().register(ViewerRole)
        output = self._run()
        assert "'editors'" in output
        assert "'viewers'" in output

    def test_empty_registry_prints_warning(self):
        output = self._run()
        assert "No roles registered" in output

    def test_sync_is_idempotent(self):
        RoleRegistry().register(EditorRole)
        RoleRegistry().register(ViewerRole)
        self._run()
        self._run()
        assert Group.objects.filter(name="editors").count() == 1
