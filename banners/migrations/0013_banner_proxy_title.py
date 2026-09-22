from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('banners', '0012_upcomingevent_location_eventmedia'),
    ]

    operations = [
        migrations.AddField(
            model_name='banner',
            name='proxy_title',
            field=models.CharField(
                blank=True,
                help_text='Optional title override used by proxy/external displays. Leave blank to use the main title.',
                max_length=200,
            ),
        ),
    ]
