# django-minosse

**Role-based access control for Django, without the extra database tables.**

django-minosse lets you define roles as Python classes, sync them to Django's built-in
`Group` model, and protect views with decorators or mixins — all on top of the
`django.contrib.auth` machinery you already have.

---

## Requirements

- Python 3.12+
- Django 5.0+

## Installation

```bash
pip install django-minosse
```

or with [uv](https://github.com/astral-sh/uv):

```bash
uv add django-minosse
```

Add `"minosse"` to `INSTALLED_APPS`, alongside the standard `auth` and `contenttypes`
apps that are already present in every Django project:

```python
INSTALLED_APPS = [
    ...
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "minosse",
    ...
]
```

Run `python manage.py migrate` at least once so the auth tables exist before calling
`sync()` or `get_group()`.

## Quick start

### 1. Define roles

```python
# myapp/roles.py
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

@registry.register
class ViewerRole(AbstractRole):
    group_name = "Viewers"
    available_permissions = {
        "can_view_reports": True,
    }
```

### 2. Sync roles to the database

```python
from myapp.roles import registry

registry.sync()   # call from a management command or AppConfig.ready()
```

### 3. Protect views

**Function-based views:**

```python
from django.contrib.auth.decorators import login_required
from minosse.decorator import role_required, permission_required
from .roles import EditorRole

@login_required
@role_required(EditorRole)
def editor_dashboard(request):
    ...

@login_required
@permission_required("auth.can_publish")
def publish_article(request, pk):
    ...
```

**Class-based views:**

```python
from django.views.generic import TemplateView
from minosse.mixin import RoleRequiredMixin, PermissionRequiredMixin
from .roles import EditorRole

class EditorDashboardView(RoleRequiredMixin, TemplateView):
    required_role_class = EditorRole
    template_name = "editor/dashboard.html"

class PublishView(PermissionRequiredMixin, TemplateView):
    required_permission_codename = "auth.can_publish"
    template_name = "editor/publish.html"
```

### 4. Manage role membership

```python
# Assign / remove
EditorRole.add_user_to_role(user)
EditorRole.remove_user_from_role(user)

# Check
if EditorRole.user_has_role(user):
    ...
```

## Features

- Define roles as Python classes with declarative permission sets
- Sync roles and permissions to Django's `Group` / `Permission` models
- Protect function-based views with `@role_required` and `@permission_required`
- Protect class-based views with `RoleRequiredMixin` and `PermissionRequiredMixin`
- Check roles and permissions in templates with `|can` and `|is` filters
- Register roles centrally via `RoleRegistry` for bulk sync

## Documentation

Full documentation is available in the `docs/` directory and can be served locally:

```bash
make docs-serve
```

## License

MIT
