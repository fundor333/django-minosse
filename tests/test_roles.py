import pytest
from django.contrib.auth.models import Group
from django.contrib.auth.models import Permission
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from minosse.roles import AbstractRole


class SampleRole(AbstractRole):
    available_permissions = {
        "can_view": True,
        "can_edit": False,
        "not a_permission": "True",
        "info": "This is just an informational entry, not a permission",
    }


class NamedRole(AbstractRole):
    group_name = "custom_group"
    available_permissions = {"can_manage": True}


class TestGetPermissionsList:
    def test_returns_permission_keys(self):
        assert set(SampleRole.get_permissions_list()) == {
            "can_view",
        }

    def test_empty_when_no_permissions_defined(self):
        class EmptyRole(AbstractRole):
            available_permissions = {}

        assert list(EmptyRole.get_permissions_list()) == []

    def test_uses_class_available_permissions(self):
        assert "can_manage" in NamedRole.get_permissions_list()


class TestGetGroupName:
    def test_returns_class_name_by_default(self):
        assert SampleRole._get_group_name() == "SampleRole"

    def test_returns_custom_group_name(self):
        assert NamedRole._get_group_name() == "custom_group"


@pytest.mark.django_db
class TestGetPermission:
    def test_returns_permission_objects_for_true_permissions(self):
        perms = SampleRole._get_permission()
        assert {p.codename for p in perms} == {"can_view"}

    def test_excludes_false_and_non_bool_values(self):
        perms = SampleRole._get_permission()
        codenames = {p.codename for p in perms}
        assert "can_edit" not in codenames
        assert "info" not in codenames

    def test_returns_empty_list_when_all_permissions_are_false(self):
        class AllFalseRole(AbstractRole):
            available_permissions = {"can_view": False, "can_edit": False}

        assert AllFalseRole._get_permission() == []

    def test_all_permissions_flag_true_yields_same_result(self):
        # _get_permission iterates get_permissions_list() which always filters
        # to True-only, so all_permissions_flag=True has no effect currently
        default = {p.codename for p in SampleRole._get_permission()}
        with_flag = {
            p.codename
            for p in SampleRole._get_permission(all_permissions_flag=True)
        }
        assert default == with_flag


@pytest.mark.django_db
class TestGetGroup:
    def test_creates_group_on_first_call(self):
        SampleRole.get_group()
        assert Group.objects.filter(name="SampleRole").exists()

    def test_creates_group_with_permissions(self):
        SampleRole.get_group()
        group = Group.objects.get(name="SampleRole")
        codenames = set(group.permissions.values_list("codename", flat=True))
        assert codenames == {"can_view"}

    def test_false_permissions_excluded_from_group(self):
        SampleRole.get_group()
        group = Group.objects.get(name="SampleRole")
        codenames = set(group.permissions.values_list("codename", flat=True))
        assert "can_edit" not in codenames
        assert "info" not in codenames

    def test_idempotent_when_called_multiple_times(self):
        SampleRole.get_group()
        SampleRole.get_group()
        assert Group.objects.filter(name="SampleRole").count() == 1

    def test_removes_extra_permissions_from_group(self):
        group = SampleRole.get_group()
        ct, _ = ContentType.objects.get_or_create(
            app_label="auth", model="user"
        )
        extra, _ = Permission.objects.get_or_create(
            codename="extra_perm",
            content_type=ct,
            defaults={"name": "Extra Permission"},
        )
        group.permissions.add(extra)
        assert group.permissions.filter(codename="extra_perm").exists()

        SampleRole.get_group()
        group.refresh_from_db()
        codenames = set(group.permissions.values_list("codename", flat=True))
        assert codenames == {"can_view"}

    def test_returns_group_object(self):
        group = SampleRole.get_group()
        assert group is not None
        assert group.name == "SampleRole"

    def test_creates_group_implicitly(self):
        class FreshRole(AbstractRole):
            available_permissions = {}

        group = FreshRole.get_group()
        assert group is not None
        assert group.name == "FreshRole"

    def test_returns_named_group(self):
        group = NamedRole.get_group()
        assert group is not None
        assert group.name == "custom_group"


@pytest.mark.django_db
class TestAddRemoveUserFromRole:
    def test_add_user_to_role(self):
        user = User.objects.create_user(username="user1", password="pass")
        SampleRole.add_user_to_role(user)
        assert SampleRole.get_group() in user.groups.all()

    def test_remove_user_from_role(self):
        user = User.objects.create_user(username="user2", password="pass")
        SampleRole.add_user_to_role(user)
        assert SampleRole.get_group() in user.groups.all()
        SampleRole.remove_user_from_role(user)
        assert SampleRole.get_group() not in user.groups.all()

    def test_add_user_creates_group_if_needed(self):
        class OrphanRole(AbstractRole):
            available_permissions = {}

        user = User.objects.create_user(username="user3", password="pass")
        OrphanRole.add_user_to_role(user)
        assert user.groups.filter(name="OrphanRole").exists()
