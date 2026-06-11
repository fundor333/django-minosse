import pytest
from django.contrib.auth.models import Group
from django.contrib.auth.models import User
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


@pytest.mark.django_db
class TestGetGroupName:
    def test_returns_class_name_by_default(self):
        assert SampleRole.get_group_name() == "SampleRole"

    def test_returns_custom_group_name(self):
        assert NamedRole.get_group_name() == "custom_group"

    def test_creates_group_in_database(self):
        SampleRole.get_group_name()
        assert Group.objects.filter(name="SampleRole").exists()

    def test_creates_group_with_permissions(self):
        SampleRole.get_group_name()
        group = Group.objects.get(name="SampleRole")
        codenames = set(group.permissions.values_list("codename", flat=True))
        assert codenames == {"can_view"}

    def test_false_permissions_excluded_from_group(self):
        SampleRole.get_group_name()
        group = Group.objects.get(name="SampleRole")
        codenames = set(group.permissions.values_list("codename", flat=True))
        assert "can_edit" not in codenames
        assert "info" not in codenames

    def test_idempotent_when_group_already_exists(self):
        SampleRole.get_group_name()
        SampleRole.get_group_name()
        assert Group.objects.filter(name="SampleRole").count() == 1


@pytest.mark.django_db
class TestGetGroup:
    def test_returns_group_after_creation(self):
        SampleRole.get_group_name()
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
        NamedRole.get_group_name()
        group = NamedRole.get_group()
        assert group is not None
        assert group.name == "custom_group"


@pytest.mark.django_db
class TestAddRemoveUserFromRole:
    def test_add_user_to_role(self):
        user = User.objects.create_user(username="user1", password="pass")
        SampleRole.get_group_name()
        SampleRole.add_user_to_role(user)
        assert SampleRole.get_group() in user.groups.all()

    def test_remove_user_from_role(self):
        user = User.objects.create_user(username="user2", password="pass")
        SampleRole.get_group_name()
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
