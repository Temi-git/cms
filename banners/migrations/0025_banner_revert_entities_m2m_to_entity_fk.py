"""
Migration 0025 — Revert Banner from ManyToMany back to ForeignKey.

Undoes migrations 0020–0023:
  1. Re-add the `entity` ForeignKey column (nullable temporarily so
     existing rows can be populated before enforcing NOT NULL).
  2. Copy each banner's first associated entity from the M2M
     through-table back into entity_id.
  3. Remove the `entities` ManyToManyField (drops the join table).
  4. Restore the original index on [entity, is_active, display_order].
  5. Remove the index added in 0022 on [is_active, display_order].
"""

import django.db.models.deletion
from django.db import migrations, models


def copy_m2m_to_fk(apps, schema_editor):
    """
    For each banner, pick the first entity from the M2M through-table
    and write it into the new entity_id column.
    """
    Banner = apps.get_model("banners", "Banner")
    db_alias = schema_editor.connection.alias

    through = Banner.entities.through  # banners_banner_entities
    for banner in Banner.objects.using(db_alias).all():
        row = (
            through.objects.using(db_alias)
            .filter(banner_id=banner.pk)
            .order_by("id")
            .first()
        )
        if row:
            banner.entity_id = row.entity_id
            banner.save(update_fields=["entity_id"])


def reverse_copy(apps, schema_editor):
    """Reverse: populate M2M from FK (no-op if M2M table has data)."""
    Banner = apps.get_model("banners", "Banner")
    db_alias = schema_editor.connection.alias
    through = Banner.entities.through
    for banner in Banner.objects.using(db_alias).all():
        if banner.entity_id:
            through.objects.using(db_alias).get_or_create(
                banner_id=banner.pk,
                entity_id=banner.entity_id,
            )


class Migration(migrations.Migration):

    dependencies = [
        ("banners", "0023_remove_banner_banners_ban_entity__73670f_idx"),
    ]

    operations = [
        # Step 1: Add entity FK column, nullable first so existing rows
        # don't violate NOT NULL during the migration.
        migrations.AddField(
            model_name="banner",
            name="entity",
            field=models.ForeignKey(
                null=True,
                blank=True,
                help_text="Entity this banner belongs to.",
                on_delete=django.db.models.deletion.CASCADE,
                related_name="banners_fk_temp",
                to="banners.entity",
            ),
        ),

        # Step 2: Populate entity_id from the M2M table.
        migrations.RunPython(copy_m2m_to_fk, reverse_copy),

        # Step 3: Remove the M2M field (drops banners_banner_entities table).
        migrations.RemoveField(
            model_name="banner",
            name="entities",
        ),

        # Step 4: Make entity non-nullable now that all rows have a value.
        migrations.AlterField(
            model_name="banner",
            name="entity",
            field=models.ForeignKey(
                null=False,
                blank=False,
                help_text="Entity this banner belongs to.",
                on_delete=django.db.models.deletion.CASCADE,
                related_name="banners",
                to="banners.entity",
            ),
        ),

        # Step 5: Restore the original composite index.
        migrations.AddIndex(
            model_name="banner",
            index=models.Index(
                fields=["entity", "is_active", "display_order"],
                name="banners_ban_entity__73670f_idx",
            ),
        ),

        # Step 6: Remove the index introduced in migration 0022.
        migrations.RemoveIndex(
            model_name="banner",
            name="banners_ban_is_acti_66e158_idx",
        ),
    ]
