from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('banners', '0015_cybersecuritysolution_product_name_product_logo'),
    ]

    operations = [
        migrations.AlterField(
            model_name='cybersecuritysolution',
            name='title',
            field=models.CharField(
                help_text="Solution/category title (e.g., 'Identity & Authentication').",
                max_length=200,
            ),
        ),
    ]
