---
icon: lucide/users
---

# Roles

## AbstractRole

`AbstractRole` is the base class for all roles in django-minosse.
Subclass it to define a role and its permission set.

```python
from minosse.roles import AbstractRole

class ModeratorRole(AbstractRole):
    group_name = "Moderators"
    available_permissions = {
        "can_ban_users": True,
        "can_delete_posts": True,
        "can_edit_posts": False,
    }
```

### Class attributes

| Attribute | Type | Default | Description |
|---|---|---|---|
| `group_name` | `str` | snake_case of the class name | Name of the Django `Group`. |
| `available_permissions` | `dict[str, bool]` | `{}` | Permission codenames mapped to `True` (active) or `False` (inactive). |
| `app_label` | `str` | class `__module__` | Affects the human-readable permission name shown in Django admin. Does **not** change the lookup key. |
| `model_name` | `str` | class `__name__` | Affects the human-readable permission name shown in Django admin. Does **not** change the lookup key. |

Only permissions with value `True` are assigned to the group on sync.

!!! note "Permission lookup key"

    All permissions created by django-minosse are linked to the `auth.user` content
    type (Django's built-in User model). This means `app_label` in the lookup string
    is always `auth`, regardless of the `app_label` class attribute.

    Use `"auth.<codename>"` wherever Django expects a permission string:

    ```python
    user.has_perm("auth.can_publish")

    @permission_required("auth.can_publish")
    def my_view(request): ...
    ```

    The `app_label` and `model_name` class attributes only affect the human-readable
    `name` field of the Django `Permission` object (visible in the admin).

### Class methods

#### `get_group() -> Group`

Creates (or retrieves) the Django `Group` for this role and syncs its permissions.
Replaces all existing permissions on the group with the currently active ones.

```python
group = ModeratorRole.get_group()
```

#### `add_user_to_role(user)`

Adds a user to the role's group.

```python
ModeratorRole.add_user_to_role(request.user)
```

#### `remove_user_from_role(user)`

Removes a user from the role's group.

```python
ModeratorRole.remove_user_from_role(request.user)
```

#### `user_has_role(user) -> bool`

Returns `True` if the user belongs to the role's group, `False` otherwise.
Unauthenticated users always return `False`.

```python
if ModeratorRole.user_has_role(request.user):
    ...
```

#### `get_permissions_list() -> KeysView`

Returns the codenames of all active permissions (those with value `True`).

---

## RoleRegistry

`RoleRegistry` is a **singleton** that acts as the central registry for all roles.
Every call to `RoleRegistry()` returns the same instance, so roles registered anywhere
in the project are always visible to the management command and to `sync()`.

```python
from minosse.roles import AbstractRole, RoleRegistry

@RoleRegistry().register
class AdminRole(AbstractRole):
    group_name = "Admins"
    available_permissions = {"can_manage_users": True}

@RoleRegistry().register
class ViewerRole(AbstractRole):
    group_name = "Viewers"
    available_permissions = {"can_view_reports": True}
```

### Methods

#### `register(role_class) -> type`

Decorator/method that registers a role class. Returns the class unchanged so it can be
used as a decorator.

#### `get_roles() -> list[type]`

Returns a copy of the list of registered role classes.

#### `sync() -> list[Group]`

Calls `get_group()` on every registered role and returns the resulting `Group` instances.

```python
RoleRegistry().sync()
```

#### `_reset() -> None`

Clears all registered roles. Intended for **test isolation only** — do not call this in
production code.
