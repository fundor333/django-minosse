from django.conf import settings
from django.core.management.base import BaseCommand
from django.core.management.base import CommandError
from django.utils.module_loading import import_string
from minosse.roles import RoleRegistry


class Command(BaseCommand):
    help = (
        "Create or update Django groups and permissions for all registered"
        " AbstractRole subclasses."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--registry",
            dest="registry",
            default=None,
            help=(
                "Dotted path to a RoleRegistry instance. "
                "Overrides MINOSSE_ROLE_REGISTRY from settings."
            ),
        )

    def handle(self, *args, **options):
        registry_path = options.get("registry") or getattr(
            settings, "MINOSSE_ROLE_REGISTRY", None
        )
        if not registry_path:
            raise CommandError(
                "No registry configured. Set MINOSSE_ROLE_REGISTRY in "
                "settings or pass --registry <dotted.path>."
            )

        try:
            registry = import_string(registry_path)
        except ImportError as exc:
            raise CommandError(
                f"Could not import registry '{registry_path}': {exc}"
            ) from exc

        if not isinstance(registry, RoleRegistry):
            raise CommandError(
                f"'{registry_path}' must be a RoleRegistry instance, "
                f"got {type(registry).__name__}."
            )

        roles = registry.get_roles()
        if not roles:
            self.stdout.write(
                self.style.WARNING("No roles registered. Nothing to sync.")
            )
            return

        self.stdout.write(f"Syncing {len(roles)} role(s)...")
        for role in roles:
            group = role.get_group()
            perm_count = group.permissions.count()
            self.stdout.write(
                self.style.SUCCESS(
                    f"  OK  {role._get_group_name()!r} "
                    f"({perm_count} permission(s))"
                )
            )

        self.stdout.write(self.style.SUCCESS("Done."))
