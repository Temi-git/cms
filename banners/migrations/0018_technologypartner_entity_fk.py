import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('banners', '0017_technologypartner'),
    ]

    operations = [
        # Drop the old CharField
        migrations.RemoveField(
            model_name='technologypartner',
            name='entity',
        ),
        # Add the FK (no existing rows, so no default needed)
        migrations.AddField(
            model_name='technologypartner',
            name='entity',
            field=models.ForeignKey(
                help_text='Entity this technology partner belongs to.',
                on_delete=django.db.models.deletion.CASCADE,
                related_name='technology_partners',
                to='banners.entity',
            ),
            # preserve_default not needed — no rows exist
        ),
    ]
