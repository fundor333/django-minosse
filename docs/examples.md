---
icon: lucide/book-open
---

# Examples

## Defining and syncing roles

```python title="myapp/roles.py"
from minosse.roles import AbstractRole, RoleRegistry

@RoleRegistry().register
class AdminRole(AbstractRole):
    group_name = "Admins"
    available_permissions = {
        "can_manage_users": True,
        "can_view_reports": True,
        "can_delete_content": True,
    }

@RoleRegistry().register
class EditorRole(AbstractRole):
    group_name = "Editors"
    available_permissions = {
        "can_publish": True,
        "can_edit": True,
        "can_delete_content": False,
    }

@RoleRegistry().register
class ViewerRole(AbstractRole):
    group_name = "Viewers"
    available_permissions = {
        "can_view_reports": True,
    }
```

`RoleRegistry` is a singleton — every call to `RoleRegistry()` returns the same instance,
so roles registered across different modules are all visible in one place.

Sync all roles (e.g. from a management command or `AppConfig.ready()`):

```python
from minosse.roles import RoleRegistry

RoleRegistry().sync()
```

---

## Assigning and checking roles

```python
from myapp.roles import EditorRole

# Assign a role
EditorRole.add_user_to_role(user)

# Remove a role
EditorRole.remove_user_from_role(user)

# Check membership
if EditorRole.user_has_role(user):
    print("User is an editor")
```

---

## Protecting function-based views

```python title="myapp/views.py"
from django.contrib.auth.decorators import login_required
from minosse.decorator import role_required, permission_required
from .roles import EditorRole

@login_required
@role_required(EditorRole)
def editor_dashboard(request):
    return render(request, "editor/dashboard.html")

@login_required
@permission_required("can_publish")
def publish_article(request, pk):
    ...
```

---

## Protecting class-based views

```python title="myapp/views.py"
from django.views.generic import TemplateView, View
from minosse.mixin import RoleRequiredMixin, PermissionRequiredMixin
from .roles import AdminRole

class AdminDashboardView(RoleRequiredMixin, TemplateView):
    required_role_class = AdminRole
    template_name = "admin/dashboard.html"

class DeleteContentView(PermissionRequiredMixin, View):
    required_permission_codename = "can_delete_content"

    def post(self, request, pk):
        ...
```

---

## Syncing roles via the built-in management command

django-minosse ships a `sync_roles` command that syncs all roles registered in the
singleton to the database. Make sure your role modules are imported before the command
runs (e.g. import them in `AppConfig.ready()`).

```bash
python manage.py sync_roles
```
