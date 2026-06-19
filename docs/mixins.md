---
icon: lucide/puzzle
---

# Mixins

django-minosse provides two mixins for protecting class-based views.
Both extend Django's `AccessMixin`, so the standard `login_url` and `raise_exception`
attributes are honoured.

---

## `RoleRequiredMixin`

Restricts a class-based view to users that belong to a specific role.

```python
from django.views import View
from minosse.mixin import RoleRequiredMixin
from .roles import EditorRole

class EditorDashboardView(RoleRequiredMixin, View):
    required_role_class = EditorRole

    def get(self, request):
        ...
```

### Attributes

| Attribute | Type | Description |
|---|---|---|
| `required_role_class` | `AbstractRole` subclass | **Required.** The role the user must have. |

!!! warning

    If `required_role_class` is not set, `dispatch()` raises `ValueError`.

### Behaviour

`dispatch()` calls `required_role_class.user_has_role(request.user)`. When access is
denied, `handle_no_permission()` is called — which either redirects to `login_url` or
raises `PermissionDenied` depending on `raise_exception`.

---

## `PermissionRequiredMixin`

Restricts a class-based view to users that have a specific permission codename.

```python
from django.views import View
from minosse.mixin import PermissionRequiredMixin

class PublishView(PermissionRequiredMixin, View):
    required_permission_codename = "auth.can_publish"

    def post(self, request):
        ...
```

### Attributes

| Attribute | Type | Description |
|---|---|---|
| `required_permission_codename` | `str` | **Required.** Full permission string in `app_label.codename` form (e.g. `"auth.can_publish"`). |

!!! warning

    If `required_permission_codename` is not set, `dispatch()` raises `ValueError`.

!!! note "Permission app label"

    django-minosse links all permissions to the `auth.user` content type, so the
    app label is always `auth`. Use `"auth.<codename>"`.

### Behaviour

`dispatch()` calls `request.user.has_perm(required_permission_codename)`. When access is
denied, `handle_no_permission()` is called.
