# Generated manually — adds unique constraint to PromallProduct.slug.
# Addresses review finding #2: two products with the same name would silently
# share a slug, breaking any future slug-based route.

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('banners', '0032_add_promall_catalog'),
    ]

    operations = [
        migrations.AlterField(
            model_name='promallproduct',
            name='slug',
            field=models.SlugField(
                max_length=500,
                unique=True,
                help_text='URL-friendly product identifier. Must be unique across all products.',
            ),
        ),
    ]
