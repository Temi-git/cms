"""
Migration 0023 — State-only removal of banners_ban_entity__73670f_idx.

Root cause:
    Migration 0021 called RemoveField(banner.entity). On SQLite, dropping
    a column rebuilds the table, which implicitly dropped the named index
    banners_ban_entity__73670f_idx from the physical database.

    Migration 0022 originally included RemoveIndex for that index but the
    operation was removed after it failed with "no such index".  That left
    Django's internal migration state still tracking the index as existing.

    Every subsequent makemigrations run re-generates this removal because
    the state says the index exists but the current model definition has no
    such index.

Fix:
    SeparateDatabaseAndState records the RemoveIndex in the migration state
    (so Django stops trying to regenerate it) while executing NOTHING against
    the database (so there is no "no such index" error at runtime).
"""

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("banners", "0022_remove_banner_banners_ban_entity__73670f_idx_and_more"),
    ]

    operations = [
        # Update the migration state to record that banners_ban_entity__73670f_idx
        # has been removed.  The index was already physically gone (dropped
        # implicitly by SQLite when migration 0021 removed the entity FK column),
        # so database_operations is intentionally empty.
        migrations.SeparateDatabaseAndState(
            state_operations=[
                migrations.RemoveIndex(
                    model_name="banner",
                    name="banners_ban_entity__73670f_idx",
                ),
            ],
            database_operations=[],
        ),
    ]
