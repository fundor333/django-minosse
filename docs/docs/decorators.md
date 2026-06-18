---
icon: lucide/lock
---

# Decorators

django-minosse provides two decorators for protecting function-based views.
Both raise `django.core.exceptions.PermissionDenied` (HTTP 403) when access is denied.

---

## `@role_required`

Restricts a view to users that belong to a specific role.

```python
from minosse.decorator import role_required
from .roles import EditorRole

@role_required(EditorRole)
def editor_dashboard(request):
    ...
```

### Parameters

| Parameter | Type | Description |
|---|---|---|
| `role_class` | `AbstractRole` subclass | The role that the user must have. |

### Behaviour

Internally calls `role_class.user_has_role(request.user)`. Unauthenticated users are
denied because `user_has_role` returns `False` for unauthenticated users.

!!! tip "Combining with `@login_required`"

    If you want to redirect unauthenticated users to the login page rather than
    returning a 403, chain `@login_required` above `@role_required`:

    ```python
    from django.contrib.auth.decorators import login_required

    @login_required
    @role_required(EditorRole)
    def editor_dashboard(request):
        ...
    ```

---

## `@permission_required`

Restricts a view to users that have a specific permission codename.

```python
from minosse.decorator import permission_required

@permission_required("can_publish")
def publish_article(request):
    ...
```

### Parameters

| Parameter | Type | Description |
|---|---|---|
| `permission_codename` | `str` | Django permission codename (e.g. `"can_publish"`). |

### Behaviour

Internally calls `request.user.has_perm(permission_codename)`.
