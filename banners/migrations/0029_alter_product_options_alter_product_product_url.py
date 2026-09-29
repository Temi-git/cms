from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("banners", "0028_product_sync_fields_productfaq"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="product",
            options={
                "ordering": ["display_order", "name"],
                "verbose_name": "Product",
                "verbose_name_plural": "Products",
            },
        ),
        migrations.AlterField(
            model_name="product",
            name="product_url",
            field=models.URLField(
                blank=True,
                help_text="URL of this product on the Promallshop website. Used by the BUY NOW button on Today's Deal.",
            ),
        ),
    ]
