import os

from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model


class Command(BaseCommand):
    help = "Create a Django superuser from environment variables"

    def handle(self, *args, **options):
        User = get_user_model()

        username = os.getenv("DJANGO_ADMIN_USERNAME")
        email = os.getenv("DJANGO_ADMIN_EMAIL", "")
        password = os.getenv("DJANGO_ADMIN_PASSWORD")

        if not username or not password:
            self.stdout.write(
                self.style.ERROR(
                    "DJANGO_ADMIN_USERNAME and DJANGO_ADMIN_PASSWORD must be set."
                )
            )
            return

        user, created = User.objects.get_or_create(
            username=username,
            defaults={
                "email": email,
                "is_staff": True,
                "is_superuser": True,
            },
        )

        if created:
            user.set_password(password)
            user.save()
            self.stdout.write(
                self.style.SUCCESS(
                    f"Superuser '{username}' created successfully."
                )
            )
        else:
            if not user.is_staff or not user.is_superuser:
                user.is_staff = True
                user.is_superuser = True
                user.save(update_fields=["is_staff", "is_superuser"])

            self.stdout.write(
                self.style.SUCCESS(
                    f"Superuser '{username}' already exists."
                )
            )