import os

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError

from apps.accounts.models import Profile


class Command(BaseCommand):
    """Create the single administrator/owner account from env vars. No public signup exists."""

    help = "Create the default (and only) LecturerHub user from DEFAULT_ADMIN_* env vars."

    def handle(self, *args, **options) -> None:
        username = os.environ.get("DEFAULT_ADMIN_USERNAME")
        email = os.environ.get("DEFAULT_ADMIN_EMAIL", "")
        password = os.environ.get("DEFAULT_ADMIN_PASSWORD")

        if not username or not password:
            raise CommandError(
                "DEFAULT_ADMIN_USERNAME and DEFAULT_ADMIN_PASSWORD must be set (see .env.example)."
            )

        User = get_user_model()
        user, created = User.objects.get_or_create(
            username=username, defaults={"email": email, "is_staff": True, "is_superuser": True}
        )
        user.set_password(password)
        user.is_staff = True
        user.is_superuser = True
        user.email = email
        user.save()

        Profile.objects.get_or_create(user=user, defaults={"full_name": username, "email": email})

        action = "Created" if created else "Updated"
        self.stdout.write(self.style.SUCCESS(f"{action} default user '{username}'."))
