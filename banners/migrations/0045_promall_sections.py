import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("banners", "0044_promallwebsitefaq"),
    ]

    operations = [
        migrations.CreateModel(
            name="PromallSection1",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("title", models.CharField(max_length=300)),
                ("subtitle", models.CharField(blank=True, max_length=500)),
                ("description", models.TextField(blank=True)),
                ("link", models.URLField(blank=True, help_text="Optional destination URL for Section 1.")),
                ("is_active", models.BooleanField(default=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("entity", models.OneToOneField(help_text="Website that owns Section 1.", on_delete=django.db.models.deletion.CASCADE, related_name="promall_section1", to="banners.entity")),
            ],
            options={
                "verbose_name": "Promall Section 1",
                "verbose_name_plural": "Promall Section 1",
            },
        ),
        migrations.CreateModel(
            name="PromallSection2",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("title", models.CharField(max_length=300)),
                ("subtitle", models.CharField(blank=True, max_length=500)),
                ("description", models.TextField(blank=True)),
                ("is_active", models.BooleanField(default=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("entity", models.OneToOneField(help_text="Website that owns Section 2.", on_delete=django.db.models.deletion.CASCADE, related_name="promall_section2", to="banners.entity")),
            ],
            options={
                "verbose_name": "Promall Section 2",
                "verbose_name_plural": "Promall Section 2",
            },
        ),
        migrations.CreateModel(
            name="PromallSubsection",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("title", models.CharField(max_length=300)),
                ("description", models.TextField(help_text="Enter the full subsection content. Long descriptions are supported.")),
                ("display_order", models.PositiveIntegerField(default=0, help_text="Lower numbers appear first.")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("section", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="subsections", to="banners.promallsection2")),
            ],
            options={
                "verbose_name": "Promall Subsection",
                "verbose_name_plural": "Promall Subsections",
                "ordering": ["display_order", "id"],
            },
        ),
        migrations.DeleteModel(
            name="PromallAdditionalWebsiteContentBulletPoint",
        ),
        migrations.DeleteModel(
            name="PromallAdditionalWebsiteContent",
        ),
    ]
