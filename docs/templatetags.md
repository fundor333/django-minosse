---
icon: lucide/tag
---

# Template tags

django-minosse provides a template tag library for checking roles and permissions
directly in Django templates.

Load it at the top of your template:

```html+django
{% load minosse_tags %}
```

!!! warning "INSTALLED_APPS required"

    `"minosse"` must be present in `INSTALLED_APPS` for Django to find the
    `minosse_tags` library. See [Installation](installation.md) for the full setup.

---

## `is`

Filter that returns `True` if the user belongs to the group identified by the given
name, `False` otherwise. Unauthenticated users always return `False`.

```html+django
{% load minosse_tags %}

{% if request.user|is:"Editors" %}
  <a href="{% url 'editor_dashboard' %}">Editor panel</a>
{% endif %}
```

### Parameters

| Argument | Type | Description |
|---|---|---|
| `group_name` | `str` | The `group_name` defined on the role class (e.g. `"Editors"`). |

!!! tip "Matching your role class"

    Pass the same string you set as `group_name` on your `AbstractRole` subclass:

    ```python
    class EditorRole(AbstractRole):
        group_name = "Editors"   # ← use this value in the filter
    ```

---

## `can`

Filter that returns `True` if the user has the given permission codename.
Accepts Django's full `app_label.codename` format.

```html+django
{% load minosse_tags %}

{% if request.user|can:"auth.can_publish" %}
  <button type="submit">Publish</button>
{% endif %}
```

### Parameters

| Argument | Type | Description |
|---|---|---|
| `permission_codename` | `str` | Full permission string in `app_label.codename` form. |

!!! note "Permission format"

    django-minosse links all permissions to the built-in `auth.user` content type,
    so the app label is always `auth`:

    ```html+django
    {% if request.user|can:"auth.can_delete_content" %}…{% endif %}
    ```

---

## Full example

```html+django
{% load minosse_tags %}

<nav>
  <a href="/">Home</a>

  {% if request.user|is:"Editors" %}
    <a href="{% url 'editor_dashboard' %}">Dashboard</a>
  {% endif %}

  {% if request.user|can:"auth.can_publish" %}
    <a href="{% url 'publish' %}">Publish</a>
  {% endif %}
</nav>
```
