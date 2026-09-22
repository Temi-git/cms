from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('banners', '0016_alter_cybersecuritysolution_title'),
    ]

    operations = [
        migrations.CreateModel(
            name='TechnologyPartner',
            fields=[
                ('id', models.BigAutoField(
                    auto_created=True,
                    primary_key=True,
                    serialize=False,
                    verbose_name='ID',
                )),
                ('name', models.CharField(
                    help_text="Partner/vendor name (e.g., 'Fortinet', 'V-Key').",
                    max_length=200,
                )),
                ('entity', models.CharField(
                    default='Proxynet Group',
                    help_text="Entity associated with this partnership (e.g., 'Proxynet Group').",
                    max_length=200,
                )),
                ('description', models.TextField(
                    blank=True,
                    help_text='Short description of the technology partner and their offering.',
                )),
                ('logo', models.ImageField(
                    help_text='Partner/vendor logo image.',
                    upload_to='partners/',
                )),
                ('display_order', models.PositiveIntegerField(
                    default=0,
                    help_text='Lower numbers appear first.',
                )),
                ('is_active', models.BooleanField(
                    default=True,
                    help_text='Uncheck to hide this partner without deleting it.',
                )),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'verbose_name': 'Technology Partner',
                'verbose_name_plural': 'Technology Partners',
                'ordering': ['display_order', 'created_at'],
            },
        ),
    ]
