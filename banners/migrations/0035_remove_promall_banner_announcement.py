from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("banners", "0034_promall_site_content"),
    ]

    operations = [
        migrations.DeleteModel(name="PromallAnnouncement"),
    ]
