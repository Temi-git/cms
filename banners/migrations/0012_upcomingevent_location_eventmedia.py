"""
Migration 0012 — Extend UpcomingEvent + add EventMedia

Operations:
  1. AddField  upcomingevent.location  (CharField blank=True)
  2. CreateModel  EventMedia
"""

import django.core.validators
import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('banners', '0011_alter_casestudy_client_overview'),
    ]

    operations = [

        # ── Step 1: location field on UpcomingEvent ──────────────────────
        migrations.AddField(
            model_name='upcomingevent',
            name='location',
            field=models.CharField(
                blank=True,
                help_text="Venue or location of the event (e.g., 'Lagos Business School, Lekki').",
                max_length=300,
            ),
        ),

        # ── Step 2: EventMedia table ─────────────────────────────────────
        migrations.CreateModel(
            name='EventMedia',
            fields=[
                ('id', models.BigAutoField(
                    auto_created=True,
                    primary_key=True,
                    serialize=False,
                    verbose_name='ID',
                )),
                ('media_type', models.CharField(
                    choices=[('image', 'Image'), ('video', 'Video')],
                    default='image',
                    help_text='Select Image or Video.',
                    max_length=10,
                )),
                ('image', models.ImageField(
                    blank=True,
                    help_text='Upload an event photo (JPEG/PNG recommended).',
                    null=True,
                    upload_to='events/gallery/',
                )),
                ('video_file', models.FileField(
                    blank=True,
                    help_text='Upload an event video (MP4/WebM recommended, max ~50 MB).',
                    null=True,
                    upload_to='events/videos/',
                    validators=[
                        django.core.validators.FileExtensionValidator(
                            allowed_extensions=['mp4', 'webm', 'mov', 'avi'],
                        )
                    ],
                )),
                ('caption', models.CharField(
                    blank=True,
                    help_text='Optional caption displayed beneath the media item.',
                    max_length=250,
                )),
                ('display_order', models.PositiveIntegerField(
                    default=0,
                    help_text='Lower numbers appear first in the gallery.',
                )),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('event', models.ForeignKey(
                    help_text='The event this media item belongs to.',
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='media',
                    to='banners.upcomingevent',
                )),
            ],
            options={
                'verbose_name': 'Event Media',
                'verbose_name_plural': 'Event Media',
                'ordering': ['display_order', 'created_at'],
                'indexes': [
                    models.Index(
                        fields=['event', 'media_type', 'display_order'],
                        name='banners_em_event__idx',
                    ),
                ],
            },
        ),
    ]
