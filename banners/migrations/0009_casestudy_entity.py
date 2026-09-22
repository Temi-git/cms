import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('banners', '0008_casestudy_casestudyimage'),
    ]

    operations = [
        migrations.AddField(
            model_name='casestudy',
            name='entity',
            field=models.ForeignKey(
                default=3,  # temporary default so existing rows can be populated
                help_text='Entity this case study belongs to.',
                on_delete=django.db.models.deletion.CASCADE,
                related_name='case_studies',
                to='banners.entity',
            ),
            preserve_default=False,
        ),
    ]
