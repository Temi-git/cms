from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('banners', '0013_banner_proxy_title'),
    ]

    operations = [
        # Task 1: ThingWeDo.full_description
        migrations.AddField(
            model_name='thingwedo',
            name='full_description',
            field=models.TextField(
                blank=True,
                help_text='Full/expanded description shown when the user clicks the card.',
                verbose_name='Full Description',
            ),
        ),
        # Task 3: Project.more_description
        migrations.AddField(
            model_name='project',
            name='more_description',
            field=models.TextField(
                blank=True,
                help_text='More Description About the Project (e.g., \'Deployed a 15-screen NOC enabling real-time monitoring.\').',
                verbose_name='More Description',
            ),
        ),
    ]
