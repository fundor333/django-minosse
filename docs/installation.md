---
icon: lucide/package
---

# Installation

## Requirements

- Python 3.12+
- Django 5.0+

## Install

Install django-minosse with pip or uv:

=== "pip"

    ```bash
    pip install django-minosse
    ```

=== "uv"

    ```bash
    uv add django-minosse
    ```

## Django setup

No additional `INSTALLED_APPS` entry is required. django-minosse uses Django's built-in
`auth` models (`Group`, `Permission`, `ContentType`) which are already included in every
Django project.

Make sure `django.contrib.auth` and `django.contrib.contenttypes` are in your
`INSTALLED_APPS` (they are by default):

```python title="settings.py"
INSTALLED_APPS = [
    ...
    "django.contrib.auth",
    "django.contrib.contenttypes",
    ...
]
```

!!! note "Database migrations"

    Run `python manage.py migrate` at least once so that the `auth` tables
    (`auth_group`, `auth_permission`, `django_content_type`) exist before calling
    `sync()` or `get_group()`.
