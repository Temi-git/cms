"""
Migration 0028 — Extend Product + add ProductFAQ

Changes to Product:
  - external_product_id: new CharField, unique, nullable
  - is_special: new BooleanField (default False)
  - is_hot: new BooleanField (default False)
  - display_order: new PositiveIntegerField (default 0)
  - image field made blank=True/null=True (was non-nullable)
  - product_url: fix indentation (was already in DB via 0027)

New model: ProductFAQ
"""

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("banners", "0027_product_product_url"),
    ]

    operations = [

        # ── Product: new sync / editorial fields ─────────────────────

        migrations.AddField(
            model_name="product",
            name="external_product_id",
            field=models.CharField(
                blank=True,
                db_index=True,
                help_text="Unique identifier from the external Promallshop product API. Used to match and avoid duplicates during sync.",
                max_length=200,
                null=True,
                unique=True,
                verbose_name="External Product ID",
            ),
        ),

        migrations.AddField(
            model_name="product",
            name="is_special",
            field=models.BooleanField(
                default=False,
                help_text="Mark this product as a Special product (admin-controlled, never set by sync).",
                verbose_name="Is Special",
            ),
        ),

        migrations.AddField(
            model_name="product",
            name="is_hot",
            field=models.BooleanField(
                default=False,
                help_text="Mark this product as a Hot product (admin-controlled, never set by sync).",
                verbose_name="Is Hot",
            ),
        ),

        migrations.AddField(
            model_name="product",
            name="display_order",
            field=models.PositiveIntegerField(
                default=0,
                help_text="Display order in listings. Lower numbers appear first.",
            ),
        ),

        # Make image blank/null so synced products without a local image
        # can still be saved.
        migrations.AlterField(
            model_name="product",
            name="image",
            field=models.ImageField(
                blank=True,
                null=True,
                help_text="Recommended size: 800 x 800 px. Product main image.",
                upload_to="products/",
            ),
        ),

        # ── ProductFAQ ────────────────────────────────────────────────

        migrations.CreateModel(
            name="ProductFAQ",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "question",
                    models.CharField(
                        help_text="The FAQ question.",
                        max_length=500,
                    ),
                ),
                (
                    "answer",
                    models.TextField(
                        help_text="The FAQ answer.",
                    ),
                ),
                (
                    "display_order",
                    models.PositiveIntegerField(
                        default=0,
                        help_text="Lower numbers appear first.",
                    ),
                ),
                (
                    "is_active",
                    models.BooleanField(
                        default=True,
                        help_text="Show this FAQ on the site.",
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "product",
                    models.ForeignKey(
                        help_text="The product this FAQ belongs to.",
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="faqs",
                        to="banners.product",
                    ),
                ),
            ],
            options={
                "verbose_name": "Product FAQ",
                "verbose_name_plural": "Product FAQs",
                "ordering": ["display_order", "created_at"],
            },
        ),
    ]
