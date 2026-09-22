"""
Migration 0021 — Banner: remove the old `entity` ForeignKey column and
                          fix the M2M related_name to its final value.

By this point migration 0020 has already:
  - created the `entities` ManyToManyField table (related_name="banners_m2m")
  - copied every banner's old entity_id into the M2M table

Now we:
  1. Remove the old `entity` FK (which held related_name="banners").
  2. Alter the M2M field's related_name from "banners_m2m" → "banners"
     so it matches the final model declaration.
"""

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("banners", "0020_banner_entities_m2m"),
    ]

    operations = [
        # 1. Drop the old FK column — data was already migrated in 0020.
        migrations.RemoveField(
            model_name="banner",
            name="entity",
        ),
        # 2. Update related_name on the M2M to match the final model.
        migrations.AlterField(
            model_name="banner",
            name="entities",
            field=models.ManyToManyField(
                to="banners.Entity",
                related_name="banners",
                help_text="Select one or more entities this banner belongs to.",
                verbose_name="Entities",
                blank=True,
            ),
        ),
    ]
