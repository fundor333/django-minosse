from django.contrib.auth.mixins import AccessMixin
from minosse.roles import AbstractRole


class RoleRequiredMixin(AccessMixin):
    required_role_class: AbstractRole = None

    def dispatch(self, request, *args, **kwargs):
        if self.required_role_class is None:
            raise ValueError(
                "required_role_class must be set to a subclass of "
                "AbstractRole."
            )
        if not self.required_role_class.user_has_role(request.user):
            return self.handle_no_permission()
        return super().dispatch(request, *args, **kwargs)


class PermissionRequiredMixin(AccessMixin):
    required_permission_codename: str = None

    def dispatch(self, request, *args, **kwargs):
        if self.required_permission_codename is None:
            raise ValueError(
                "required_permission_codename must be set to a valid "
                "permission codename."
            )
        if not request.user.has_perm(self.required_permission_codename):
            return self.handle_no_permission()
        return super().dispatch(request, *args, **kwargs)
