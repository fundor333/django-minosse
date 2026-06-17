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

| Attribute | Type | Description |
|---|---|---|
| `group_name` | `str` | Name of the Django `Group`. Defaults to the class name. |
| `available_permissions` | `dict[str, bool]` | Permission codenames mapped to `True` (active) or `False` (inactive). |

Only permissions with value `True` are assigned to the group on sync.

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

`RoleRegistry` acts as a central registry for all roles. Use it to collect roles and
sync them all in one call — useful in management commands or app startup hooks.

```python
from minosse.roles import AbstractRole, RoleRegistry

registry = RoleRegistry()

@registry.register
class AdminRole(AbstractRole):
    group_name = "Admins"
    available_permissions = {"can_manage_users": True}

@registry.register
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
groups = registry.sync()
```
