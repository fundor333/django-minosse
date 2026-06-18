---
icon: lucide/shield
---

# django-minosse

**django-minosse** is a lightweight library for role-based access control (RBAC) in Django projects.
It lets you define roles as Python classes, sync them to Django's built-in `Group` model, and protect
views with decorators or mixins — all without a dedicated database table for roles.

## Features

- Define roles as Python classes with declarative permission sets
- Sync roles and permissions to Django's `Group` / `Permission` models
- Protect function-based views with the `@role_required` and `@permission_required` decorators
- Protect class-based views with `RoleRequiredMixin` and `PermissionRequiredMixin`
- Check roles and permissions in templates with the `has_role` and `has_perm` filters
- Register roles centrally via `RoleRegistry` for bulk sync (e.g. from a management command)

## Quick example

```python
from minosse.roles import AbstractRole, RoleRegistry

registry = RoleRegistry()

@registry.register
class EditorRole(AbstractRole):
    group_name = "Editors"
    available_permissions = {
        "can_publish": True,
        "can_edit": True,
        "can_delete": False,
    }

# Sync all registered roles to the database
registry.sync()
```

```python
from minosse.decorator import role_required
from .roles import EditorRole

@role_required(EditorRole)
def editor_dashboard(request):
    ...
```
