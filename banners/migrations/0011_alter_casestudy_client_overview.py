# Generated to reconcile AlterField after 0010 rename
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('banners', '0010_casestudy_rename_fields_technology_result_roi'),
    ]

    operations = [
        migrations.AlterField(
            model_name='casestudy',
            name='client_overview',
            field=models.TextField(
                blank=True,
                help_text='Background information about the client.',
                verbose_name='Client Overview',
            ),
        ),
    ]
