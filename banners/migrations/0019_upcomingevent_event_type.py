from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('banners', '0018_technologypartner_entity_fk'),
    ]

    operations = [
        migrations.AddField(
            model_name='upcomingevent',
            name='event_type',
            field=models.CharField(
                blank=True,
                default='',
                help_text='Type of event (e.g., Conference, Exhibition, Product Launch, Workshop).',
                max_length=100,
                verbose_name='Event Type',
            ),
        ),
    ]
