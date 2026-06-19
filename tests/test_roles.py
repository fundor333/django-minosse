import pytest
from django.contrib.auth.models import AnonymousUser
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
    
class SampleRoleWithOtherName(SampleRole):
    group_name = "AnotherGroup"

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
    def test_returns_snake_case_by_default(self):
        assert SampleRole._get_group_name() == "sample_role"
        assert SampleRoleWithOtherName._get_group_name() == "AnotherGroup"

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
        default = {p.codename for p in SampleRole._get_permission()}
        with_flag = {
            p.codename
            for p in SampleRole._get_permission(all_permissions_flag=True)
        }
        assert default == with_flag

    def test_permission_name_follows_module_model_action_format(self):
        perms = {p.codename: p for p in SampleRole._get_permission()}
        expected = (
            f"{SampleRole.__module__} | {SampleRole.__name__} | can_view"
        )
        assert perms["can_view"].name == expected

    def test_permission_content_type_app_label_uses_class_module(self):
        for perm in SampleRole._get_permission():
            assert perm.content_type.app_label == SampleRole.__module__

    def test_permission_content_type_model_uses_class_name(self):
        for perm in SampleRole._get_permission():
            assert perm.content_type.model == SampleRole.__name__

    def test_app_label_and_model_name_override(self):
        class OverrideRole(AbstractRole):
            app_label = "myapp"
            model_name = "MyModel"
            available_permissions = {"can_do": True}

        perms = OverrideRole._get_permission()
        assert len(perms) == 1
        assert perms[0].content_type.app_label == "myapp"
        assert perms[0].content_type.model == "MyModel"
        assert perms[0].name == "myapp | MyModel | can_do"


@pytest.mark.django_db
class TestGetGroup:
    def test_creates_group_on_first_call(self):
        SampleRole.get_group()
        assert Group.objects.filter(name="sample_role").exists()

    def test_creates_group_with_permissions(self):
        SampleRole.get_group()
        group = Group.objects.get(name="sample_role")
        codenames = set(group.permissions.values_list("codename", flat=True))
        assert codenames == {"can_view"}

    def test_false_permissions_excluded_from_group(self):
        SampleRole.get_group()
        group = Group.objects.get(name="sample_role")
        codenames = set(group.permissions.values_list("codename", flat=True))
        assert "can_edit" not in codenames
        assert "info" not in codenames

    def test_idempotent_when_called_multiple_times(self):
        SampleRole.get_group()
        SampleRole.get_group()
        assert Group.objects.filter(name="sample_role").count() == 1

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
        assert group.name == "sample_role"

    def test_creates_group_implicitly(self):
        class FreshRole(AbstractRole):
            available_permissions = {}

        group = FreshRole.get_group()
        assert group is not None
        assert group.name == "fresh_role"

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
        assert user.groups.filter(name="orphan_role").exists()


@pytest.mark.django_db
class TestUserHasRole:
    def test_returns_true_for_user_with_role(self):
        user = User.objects.create_user(username="member", password="pass")
        SampleRole.add_user_to_role(user)
        assert SampleRole.user_has_role(user) is True

    def test_returns_false_for_user_without_role(self):
        user = User.objects.create_user(username="outsider", password="pass")
        assert SampleRole.user_has_role(user) is False

    def test_returns_false_for_anonymous_user(self):
        assert SampleRole.user_has_role(AnonymousUser()) is False

    def test_role_check_is_group_specific(self):
        user = User.objects.create_user(username="manager", password="pass")
        NamedRole.add_user_to_role(user)
        assert NamedRole.user_has_role(user) is True
        assert SampleRole.user_has_role(user) is False

    def test_returns_false_after_remove(self):
        user = User.objects.create_user(username="ex_member", password="pass")
        SampleRole.add_user_to_role(user)
        SampleRole.remove_user_from_role(user)
        assert SampleRole.user_has_role(user) is False
