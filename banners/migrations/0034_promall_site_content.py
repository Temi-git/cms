# Generated manually for Promallshop site-content additions:
#   - AffiliateBanner: add placement field, make affiliate_url optional,
#     add unique constraint (entity, placement) when placement is non-blank.
#   - PromallBanner, PromallAnnouncement, PromallEventType, PromallEvent: new models.
#
# Migration is safe for existing data:
#   - placement defaults to '' so every existing AffiliateBanner row keeps a blank placement.
#   - The UniqueConstraint only applies when placement != '' so no existing row violates it.
#   - affiliate_url is made blank=True (DB column already nullable-equivalent for VARCHAR);
#     no data loss.

import django.db.models.deletion
import django.db.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('banners', '0033_promallproduct_slug_unique'),
    ]

    operations = [
        # ----------------------------------------------------------------
        # 1. AffiliateBanner â€” add placement field
        # ----------------------------------------------------------------
        migrations.AddField(
            model_name='affiliatebanner',
            name='placement',
            field=models.CharField(
                blank=True,
                choices=[
                    ('top',              'Top â€” full-width strip above all content (Recommended size: TBC)'),
                    ('program',          'Program â€” linked promotional block in the main body (Recommended size: TBC)'),
                    ('below_categories', 'Below Categories â€” banner displayed beneath the category grid (Recommended size: TBC)'),
                    ('flash_side',       'Flash Side â€” sidebar banner beside the flash-sale section (Recommended size: TBC)'),
                    ('below_flash',      'Below Flash â€” banner displayed directly below the flash-sale strip (Recommended size: TBC)'),
                ],
                db_index=True,
                default='',
                help_text=(
                    "Where this banner appears on the page. "
                    "Only the 'Program' placement uses an affiliate_url link â€” all others are static images. "
                    "One banner per entity per placement is enforced (existing rows have no placement)."
                ),
                max_length=30,
            ),
        ),

        # ----------------------------------------------------------------
        # 2. AffiliateBanner â€” make affiliate_url optional
        # ----------------------------------------------------------------
        migrations.AlterField(
            model_name='affiliatebanner',
            name='affiliate_url',
            field=models.URLField(
                blank=True,
                help_text=(
                    "External affiliate or target URL. "
                    "Required only for the 'Program' placement â€” leave blank for static-image placements."
                ),
            ),
        ),

        # ----------------------------------------------------------------
        # 3. AffiliateBanner â€” add unique constraint per entity+placement
        # ----------------------------------------------------------------

        # ----------------------------------------------------------------
        # 4. PromallBanner
        # ----------------------------------------------------------------
        migrations.CreateModel(
            name='PromallBanner',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(help_text='Banner headline text displayed over the image.', max_length=300)),
                ('description', models.TextField(blank=True, help_text='Optional supporting text shown beneath the title.')),
                ('button_text', models.CharField(
                    blank=True,
                    help_text='Call-to-action button label, e.g. "Shop Now". Leave blank to hide the button.',
                    max_length=100,
                )),
                ('button_link', models.URLField(blank=True, help_text='URL the button links to. Leave blank if no button is shown.')),
                ('image', models.ImageField(
                    help_text='Main banner image. Recommended size: TBC.',
                    upload_to='promall/banners/',
                )),
                ('display_order', models.PositiveIntegerField(default=0, help_text='Lower numbers appear first in the slider.')),
                ('is_active', models.BooleanField(default=True, help_text='Uncheck to hide this banner without deleting it.')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('entity', models.ForeignKey(
                    help_text='Must be the Promallshop entity.',
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='promall_banners',
                    to='banners.entity',
                )),
            ],
            options={
                'verbose_name': 'Promall Banner',
                'verbose_name_plural': 'Promall Banners',
                'ordering': ['display_order', '-created_at'],
            },
        ),

        # ----------------------------------------------------------------
        # 5. PromallAnnouncement
        # ----------------------------------------------------------------
        migrations.CreateModel(
            name='PromallAnnouncement',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('text', models.CharField(
                    help_text='Announcement text shown in the top bar, e.g. "Bonanza 15% off all items this week!".',
                    max_length=500,
                )),
                ('link', models.URLField(blank=True, help_text='Optional URL the announcement links to. Leave blank for a non-clickable bar.')),
                ('is_active', models.BooleanField(default=True, help_text='Uncheck to hide this announcement without deleting it.')),
                ('display_order', models.PositiveIntegerField(
                    default=0,
                    help_text='Lower numbers appear first. The first active announcement is displayed.',
                )),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('entity', models.ForeignKey(
                    help_text='Must be the Promallshop entity.',
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='promall_announcements',
                    to='banners.entity',
                )),
            ],
            options={
                'verbose_name': 'Promall Announcement',
                'verbose_name_plural': 'Promall Announcements',
                'ordering': ['display_order', '-created_at'],
            },
        ),

        # ----------------------------------------------------------------
        # 6. PromallEventType
        # ----------------------------------------------------------------
        migrations.CreateModel(
            name='PromallEventType',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(
                    help_text='Event type label shown in filters, e.g. "Webinars", "Product Launches".',
                    max_length=200,
                )),
                ('slug', models.SlugField(
                    db_index=True,
                    help_text='URL-friendly identifier used in ?type=<slug> filter. Auto-generate from name.',
                    max_length=200,
                )),
                ('display_order', models.PositiveIntegerField(default=0, help_text='Lower numbers appear first in filter lists.')),
                ('is_active', models.BooleanField(default=True, help_text='Uncheck to hide this event type from the filter list.')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('entity', models.ForeignKey(
                    help_text='Must be the Promallshop entity.',
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='promall_event_types',
                    to='banners.entity',
                )),
            ],
            options={
                'verbose_name': 'Promall Event Type',
                'verbose_name_plural': 'Promall Event Types',
                'ordering': ['display_order', 'name'],
                'unique_together': {('entity', 'slug')},
            },
        ),

        # ----------------------------------------------------------------
        # 7. PromallEvent
        # ----------------------------------------------------------------
        migrations.CreateModel(
            name='PromallEvent',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(help_text='Event name/title.', max_length=300)),
                ('description', models.TextField(blank=True, help_text='Full description of the event.')),
                ('event_datetime', models.DateTimeField(help_text='Scheduled date and time of the event.')),
                ('location', models.CharField(
                    blank=True,
                    help_text='Venue or location (e.g. "Lagos, Nigeria" or "Online via Zoom").',
                    max_length=300,
                )),
                ('image', models.ImageField(
                    blank=True,
                    help_text='Event cover image. Recommended size: TBC.',
                    null=True,
                    upload_to='promall/events/',
                )),
                ('registration_link', models.URLField(blank=True, help_text='Optional registration or RSVP URL.')),
                ('is_active', models.BooleanField(default=True, help_text='Uncheck to hide this event without deleting it.')),
                ('display_order', models.PositiveIntegerField(default=0, help_text='Lower numbers appear first.')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('entity', models.ForeignKey(
                    help_text='Must be the Promallshop entity.',
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='promall_events',
                    to='banners.entity',
                )),
                ('event_type', models.ForeignKey(
                    blank=True,
                    help_text='Category/type of this event (e.g. Webinars). Leave blank for uncategorised events.',
                    null=True,
                    on_delete=django.db.models.deletion.SET_NULL,
                    related_name='events',
                    to='banners.promalleventtype',
                )),
            ],
            options={
                'verbose_name': 'Promall Event',
                'verbose_name_plural': 'Promall Events',
                'ordering': ['event_datetime', 'display_order'],
            },
        ),
    ]
