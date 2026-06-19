import pytest
from django.contrib.auth.models import AnonymousUser
from django.contrib.auth.models import User
from django.template import Context
from django.template import Template
from minosse.roles import AbstractRole


class EditorRole(AbstractRole):
    app_label = "minosse"
    group_name = "Editors"
    available_permissions = {"can_publish": True}


def render(template_str: str, context: dict) -> str:
    return Template(template_str).render(Context(context))


@pytest.mark.django_db
class TestHasRoleFilter:
    def test_returns_true_for_user_with_role(self):
        user = User.objects.create_user(username="editor", password="pass")
        EditorRole.add_user_to_role(user)
        result = render(
            "{% load minosse_tags %}"
            "{% if user|has_role:'Editors' %}yes{% endif %}",
            {"user": user},
        )
        assert result == "yes"

    def test_returns_empty_for_user_without_role(self):
        user = User.objects.create_user(username="viewer", password="pass")
        result = render(
            "{% load minosse_tags %}"
            "{% if user|has_role:'Editors' %}yes{% endif %}",
            {"user": user},
        )
        assert result == ""

    def test_returns_empty_for_anonymous_user(self):
        result = render(
            "{% load minosse_tags %}"
            "{% if user|has_role:'Editors' %}yes{% endif %}",
            {"user": AnonymousUser()},
        )
        assert result == ""

    def test_returns_empty_for_unknown_group(self):
        user = User.objects.create_user(username="nobody", password="pass")
        result = render(
            "{% load minosse_tags %}"
            "{% if user|has_role:'NonExistent' %}yes{% endif %}",
            {"user": user},
        )
        assert result == ""


@pytest.mark.django_db
class TestHasPermFilter:
    def test_returns_true_for_user_with_permission(self):
        user = User.objects.create_user(username="publisher", password="pass")
        EditorRole.add_user_to_role(user)
        user = User.objects.get(pk=user.pk)  # clear Django's permission cache
        result = render(
            "{% load minosse_tags %}"
            "{% if user|has_perm:'minosse.can_publish' %}yes{% endif %}",
            {"user": user},
        )
        assert result == "yes"

    def test_returns_empty_for_user_without_permission(self):
        user = User.objects.create_user(username="noperm", password="pass")
        result = render(
            "{% load minosse_tags %}"
            "{% if user|has_perm:'minosse.can_publish' %}yes{% endif %}",
            {"user": user},
        )
        assert result == ""

    def test_returns_empty_for_anonymous_user(self):
        result = render(
            "{% load minosse_tags %}"
            "{% if user|has_perm:'minosse.can_publish' %}yes{% endif %}",
            {"user": AnonymousUser()},
        )
        assert result == ""
