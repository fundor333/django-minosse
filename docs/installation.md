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

Add `"minosse"` to your `INSTALLED_APPS`, along with the standard `auth` and
`contenttypes` apps (present by default in every Django project):

```python title="settings.py"
INSTALLED_APPS = [
    ...
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "minosse",
    ...
]
```

`"minosse"` is required for two reasons:

- Django discovers template tag libraries (`{% load minosse_tags %}`) only inside
  apps listed in `INSTALLED_APPS`.
- The `sync_roles` management command is registered under the `minosse` app.

!!! note "Database migrations"

    Run `python manage.py migrate` at least once so that the `auth` tables
    (`auth_group`, `auth_permission`, `django_content_type`) exist before calling
    `sync()` or `get_group()`.

## Development setup

If you want to contribute or run the test suite locally, clone the repository and
install the dev dependencies with [uv](https://github.com/astral-sh/uv):

```bash
git clone https://github.com/Fundor333/django-minosse.git
cd django-minosse
make install
```

Run the tests:

```bash
make test
```

Serve the documentation locally at [localhost:8001](http://localhost:8001):

```bash
make docs-serve
```
