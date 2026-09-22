"""
Migration 0020 — Banner: ForeignKey → ManyToMany (safe two-step)

Step A (this migration):
  1. Add the new `entities` ManyToManyField table.
  2. Data-migrate every banner's existing `entity_id` FK value into
     the new M2M through-table so NO existing assignments are lost.

The old `entity` FK column is intentionally LEFT in place here so
that the data migration can still read it.  Migration 0021 removes it.
"""

from django.db import migrations, models


def copy_fk_to_m2m(apps, schema_editor):
    """
    For every Banner that has an entity_id set, insert one row into
    the new M2M through-table (banners_banner_entities).
    """
    Banner = apps.get_model("banners", "Banner")
    # apps.get_model returns the historical model; we access entity_id directly.
    db_alias = schema_editor.connection.alias

    through_table = Banner.entities.through

    rows = []
    for banner in Banner.objects.using(db_alias).all():
        # entity_id is still a column at this point (removed in 0021)
        if banner.entity_id is not None:
            rows.append(
                through_table(
                    banner_id=banner.pk,
                    entity_id=banner.entity_id,
                )
            )

    if rows:
        through_table.objects.using(db_alias).bulk_create(rows, ignore_conflicts=True)


def reverse_copy(apps, schema_editor):
    """
    On reverse migration: clear the M2M table (the FK is still there
    so the old state is already correct).
    """
    Banner = apps.get_model("banners", "Banner")
    through_table = Banner.entities.through
    through_table.objects.using(schema_editor.connection.alias).all().delete()


class Migration(migrations.Migration):

    dependencies = [
        ("banners", "0019_upcomingevent_event_type"),
    ]

    operations = [
        # 1. Create the M2M join table.
        # NOTE: related_name is temporarily "banners_m2m" here because the old
        # FK also uses related_name="banners".  Migration 0021 removes the FK,
        # and the final model state has related_name="banners" on the M2M.
        # The model file already declares related_name="banners", which is what
        # Django squashes the state to after both migrations complete.
        migrations.AddField(
            model_name="banner",
            name="entities",
            field=models.ManyToManyField(
                to="banners.Entity",
                related_name="banners_m2m",
                help_text="Select one or more entities this banner belongs to.",
                verbose_name="Entities",
                blank=True,
            ),
        ),
        # 2. Copy existing FK assignments into the new M2M table.
        migrations.RunPython(copy_fk_to_m2m, reverse_copy),
    ]
