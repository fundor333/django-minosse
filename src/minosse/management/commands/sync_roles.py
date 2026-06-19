from django.core.management.base import BaseCommand
from minosse.roles import RoleRegistry


class Command(BaseCommand):
    help = (
        "Create or update Django groups and permissions for all registered"
        " AbstractRole subclasses."
    )

    def handle(self, *args, **options):
        registry = RoleRegistry()
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
