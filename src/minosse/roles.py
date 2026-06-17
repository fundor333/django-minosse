from typing import Any

from django.contrib.auth.models import Group
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType

registered_roles = {}


class AbstractRole:

    @classmethod
    def get_permissions_list(cls):
        available_permissions: dict[str, bool] = getattr(
            cls, "available_permissions", {}
        )
        available_permissions = {
            k: v for k, v in available_permissions.items() if v is True
        }
        return available_permissions.keys()

    @classmethod
    def _get_group_name(cls) -> str:
        name: Any | str = getattr(cls, "group_name", cls.__name__)
        return name

    @classmethod
    def _get_permission(
        cls, all_permissions_flag: bool = False
    ) -> list[Permission]:
        available_permissions = getattr(cls, "available_permissions", {})
        if all_permissions_flag is False:
            available_permissions = {
                k: v for k, v in available_permissions.items() if v is True
            }

        permissions = []
        for perm in cls.get_permissions_list():
            content_type, _ = ContentType.objects.get_or_create(
                app_label="minosse",
                model="role",
            )
            permission, _ = Permission.objects.get_or_create(
                codename=perm,
                content_type=content_type,
                defaults={"name": available_permissions.get(perm, perm)},
            )
            permissions.append(permission)
        return permissions

    @classmethod
    def _set_group_permissions(cls, group: Group):
        group.permissions.clear()
        group.permissions.add(*cls._get_permission())

    @classmethod
    def get_group(cls) -> Group:
        group_name = cls._get_group_name()
        group, _ = Group.objects.get_or_create(name=group_name)
        cls._set_group_permissions(group)
        return group

    @classmethod
    def add_user_to_role(cls, user):
        group = cls.get_group()
        if group:
            user.groups.add(group)

    @classmethod
    def remove_user_from_role(cls, user):
        group = cls.get_group()
        if group:
            user.groups.remove(group)

    @classmethod
    def user_has_role(cls, user):
        if not user.is_authenticated:
            return False
        group_name = getattr(cls, "group_name", cls.__name__)
        return user.groups.filter(name=group_name).exists()

    class Meta:
        abstract = True
