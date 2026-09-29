"""
Management command: sync_products

Usage:
    python manage.py sync_products
    python manage.py sync_products --url https://custom-endpoint/products/
"""

from django.core.management.base import BaseCommand

from banners.services import sync_external_products


class Command(BaseCommand):
    help = "Synchronise products from the external Promallshop product API."

    def add_arguments(self, parser):
        parser.add_argument(
            "--url",
            type=str,
            default=None,
            help="Override the external API URL (uses PROMALLSHOP_PRODUCTS_URL from settings by default).",
        )

    def handle(self, *args, **options):
        self.stdout.write("Starting external product sync…")

        results = sync_external_products(url=options.get("url"))

        self.stdout.write(
            self.style.SUCCESS(
                f"Sync complete — "
                f"created: {results['created']}, "
                f"updated: {results['updated']}, "
                f"skipped: {results['skipped']}, "
                f"errors: {len(results['errors'])}"
            )
        )

        if results["errors"]:
            self.stdout.write(self.style.WARNING("Errors encountered:"))
            for err in results["errors"]:
                self.stdout.write(f"  • {err}")
