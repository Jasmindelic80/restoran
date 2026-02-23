from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
import os


class Command(BaseCommand):
    help = "Create superuser if not exists"

    def handle(self, *args, **kwargs):
        username = os.getenv("ADMIN_USERNAME")
        email = os.getenv("ADMIN_EMAIL")
        password = os.getenv("ADMIN_PASSWORD")

        if not username or not password:
            self.stdout.write("Admin credentials not provided.")
            return

        User = get_user_model()

        if not User.objects.filter(username=username).exists():
            User.objects.create_superuser(
                username=username,
                email=email,
                password=password,
            )
            self.stdout.write(self.style.SUCCESS("Superuser created."))
        else:
            self.stdout.write("Superuser already exists.")