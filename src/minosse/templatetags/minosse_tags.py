from django import template

register = template.Library()


@register.filter
def has_role(user, group_name: str) -> bool:
    """Return True if *user* belongs to the group identified by *group_name*.

    Usage::

        {% load minosse_tags %}
        {% if request.user|has_role:"Editors" %}…{% endif %}
    """
    if not user.is_authenticated:
        return False
    return user.groups.filter(name=group_name).exists()


@register.filter
def has_perm(user, permission_codename: str) -> bool:
    """Return True if *user* has *permission_codename*.

    Accepts the full ``app_label.codename`` form expected by Django.

    Usage::

        {% load minosse_tags %}
        {% if request.user|has_perm:"minosse.can_publish" %}…{% endif %}
    """
    return user.has_perm(permission_codename)
