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
    def get_group_name(cls):
        name = getattr(cls, "group_name", cls.__name__)
        group = Group.objects.filter(name=name).first()
        if not group:
            group, _ = Group.objects.get_or_create(name=name)
            available_permissions = getattr(cls, "available_permissions", {})
            content_type, _ = ContentType.objects.get_or_create(
                app_label="minosse",
                model="role",
            )
            permissions = []
            for perm in cls.get_permissions_list():
                permission, _ = Permission.objects.get_or_create(
                    codename=perm,
                    content_type=content_type,
                    defaults={"name": available_permissions.get(perm, perm)},
                )
                permissions.append(permission)
            group.permissions.set(permissions)
        return name

    @classmethod
    def get_group(cls):
        group_name = cls.get_group_name()
        group = Group.objects.filter(name=group_name).first()
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
