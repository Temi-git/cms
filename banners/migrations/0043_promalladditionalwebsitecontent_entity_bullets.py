from django.db import migrations, models
import django.db.models.deletion


def copy_existing_bullet_points(apps, schema_editor):
    # Read the old JSON column using a temporary historical model.
    # The migration's current model state has already repurposed
    # "bullet_points" as a reverse relationship, so it cannot be read
    # directly from the normal historical model.
    Content = apps.get_model("banners", "PromallAdditionalWebsiteContent")
    BulletPoint = apps.get_model(
        "banners",
        "PromallAdditionalWebsiteContentBulletPoint",
    )
    database = schema_editor.connection.alias

    # Build a temporary model mapped to the same database table, with
    # the original JSON column represented as a normal field.
    from django.db import models

    class LegacyContent(models.Model):
        bullet_points = models.JSONField(default=list, blank=True)

        class Meta:
            app_label = "banners"
            db_table = Content._meta.db_table
            managed = False

    for section in Content.objects.using(database).all().iterator():
        legacy = LegacyContent.objects.using(database).get(pk=section.pk)
        points = legacy.bullet_points or []

        if not isinstance(points, list):
            continue

        for position, value in enumerate(points):
            text = str(value).strip()
            if text:
                BulletPoint.objects.using(database).create(
                    content_id=section.pk,
                    text=text[:500],
                    display_order=position,
                )


def restore_bullet_points(apps, schema_editor):
    # Restore the original JSON values if this migration is reversed.
    # This function runs before the reverse operation removes the child
    # table, so read all bullet points back into a temporary JSON column.
    from django.db import models

    Content = apps.get_model("banners", "PromallAdditionalWebsiteContent")
    BulletPoint = apps.get_model(
        "banners",
        "PromallAdditionalWebsiteContentBulletPoint",
    )
    database = schema_editor.connection.alias

    class LegacyContent(models.Model):
        bullet_points = models.JSONField(default=list, blank=True)

        class Meta:
            app_label = "banners"
            db_table = Content._meta.db_table
            managed = False

    for section in Content.objects.using(database).all().iterator():
        points = list(
            BulletPoint.objects.using(database)
            .filter(content_id=section.pk)
            .order_by("display_order", "id")
            .values_list("text", flat=True)
        )
        LegacyContent.objects.using(database).filter(pk=section.pk).update(
            bullet_points=points
        )


class Migration(migrations.Migration):
    dependencies = [
        ("banners", "0042_promalladditionalwebsitecontent"),
    ]

    operations = [
        migrations.AddField(
            model_name="promalladditionalwebsitecontent",
            name="entity",
            field=models.ForeignKey(
                blank=True,
                help_text="Website/entity that owns this content section.",
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="promall_additional_website_content",
                to="banners.entity",
            ),
        ),
        migrations.CreateModel(
            name="PromallAdditionalWebsiteContentBulletPoint",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("text", models.CharField(max_length=500)),
                ("display_order", models.PositiveIntegerField(default=0)),
                (
                    "content",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="bullet_points",
                        to="banners.promalladditionalwebsitecontent",
                    ),
                ),
            ],
            options={
                "verbose_name": "Bullet Point",
                "verbose_name_plural": "Bullet Points",
                "ordering": ["display_order", "id"],
            },
        ),
        migrations.RunPython(
            copy_existing_bullet_points,
            restore_bullet_points,
        ),
        migrations.RemoveField(
            model_name="promalladditionalwebsitecontent",
            name="bullet_points",
        ),
    ]
