from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('banners', '0014_thingwedo_full_description_project_more_description'),
    ]

    operations = [
        migrations.AddField(
            model_name='cybersecuritysolution',
            name='product_name',
            field=models.CharField(
                blank=True,
                help_text="Product or vendor name (e.g., 'V-Key'). Displayed below the category title.",
                max_length=200,
                verbose_name='Product Name',
            ),
        ),
        migrations.AddField(
            model_name='cybersecuritysolution',
            name='product_logo',
            field=models.ImageField(
                blank=True,
                help_text='PRODUCT/VENDOR LOGO — the small logo displayed below the product description (e.g., V-Key logo). Different from the main image above.',
                null=True,
                upload_to='cybersecurity_solutions/logos/',
                verbose_name='Product/Vendor Logo',
            ),
        ),
        # Update help_text on existing image field to make its purpose clear in the DB record
        migrations.AlterField(
            model_name='cybersecuritysolution',
            name='image',
            field=models.ImageField(
                help_text='MAIN PRODUCT IMAGE — the large image shown in the solution card/slide.',
                upload_to='cybersecurity_solutions/',
            ),
        ),
    ]
