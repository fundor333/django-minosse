from django import template

register = template.Library()


@register.filter(name="can")
def has_role_template_tag(user, group_name: str) -> bool:
    """Return True if *user* belongs to the group identified by *group_name*.

    Usage::

        {% load minosse_tags %}
        {% if request.user|can:"Editors" %}…{% endif %}
    """
    if not user.is_authenticated:
        return False
    return user.groups.filter(name=group_name).exists()


@register.filter(name="is")
def has_perm(user, permission_codename: str) -> bool:
    """Return True if *user* has *permission_codename*.

    All minosse permissions are stored under the ``auth`` app label (they are
    linked to the User content type), so pass ``auth.<codename>``.

    Usage::

        {% load minosse_tags %}
        {% if request.user|is:"auth.can_publish" %}…{% endif %}
    """
    return user.has_perm(permission_codename)
