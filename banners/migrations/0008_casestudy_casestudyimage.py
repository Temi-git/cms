import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('banners', '0007_recognition_teamcertificate'),
    ]

    operations = [

        # --------------------------------------------------------
        # CaseStudy
        # --------------------------------------------------------
        migrations.CreateModel(
            name='CaseStudy',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                # PublishableMixin fields
                ('is_active', models.BooleanField(default=True, help_text='Designates whether this content is enabled by an administrator.')),
                ('publish_start', models.DateTimeField(blank=True, help_text='Optional start of the publishing window.', null=True)),
                ('publish_end', models.DateTimeField(blank=True, help_text='Optional end of the publishing window.', null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                # CaseStudy-specific fields
                ('title', models.CharField(help_text="Case study title (e.g., 'Access Bank Videowall — Ikota Branch').", max_length=250)),
                ('slug', models.SlugField(blank=True, help_text='URL-friendly identifier. Auto-generated from title if left blank.', max_length=250, unique=True)),
                ('client', models.CharField(help_text="Client / organisation name (e.g., 'Access Bank').", max_length=200)),
                ('solution', models.CharField(help_text="Solution delivered (e.g., 'Videowall & Digital Signage').", max_length=200)),
                ('industry', models.CharField(help_text="Client industry (e.g., 'Financial Services').", max_length=200)),
                ('country', models.CharField(help_text="Country where the project was delivered (e.g., 'Nigeria').", max_length=100)),
                ('short_description', models.TextField(blank=True, help_text='Brief summary shown on the listing card.')),
                ('featured_image', models.ImageField(blank=True, help_text='Main hero image for the case study.', null=True, upload_to='case_studies/featured/')),
                ('client_background', models.TextField(blank=True, help_text='Background information about the client.')),
                ('challenge', models.TextField(blank=True, help_text='The challenge or problem the client faced.')),
                ('solution_details', models.TextField(blank=True, help_text='Detailed description of the solution delivered.')),
                ('implementation', models.TextField(blank=True, help_text='How the solution was implemented.')),
                ('results', models.TextField(blank=True, help_text='Outcomes and measurable results achieved.')),
                ('display_order', models.PositiveIntegerField(default=0, help_text='Lower numbers appear first in the listing.')),
            ],
            options={
                'verbose_name': 'Case Study',
                'verbose_name_plural': 'Case Studies',
                'ordering': ['display_order', '-created_at'],
                'indexes': [
                    models.Index(
                        fields=['is_active', 'display_order'],
                        name='banners_cs_active__order_idx',
                    ),
                ],
            },
        ),

        # --------------------------------------------------------
        # CaseStudyImage
        # --------------------------------------------------------
        migrations.CreateModel(
            name='CaseStudyImage',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('image', models.ImageField(help_text='Gallery image for this case study.', upload_to='case_studies/gallery/')),
                ('caption', models.CharField(blank=True, help_text='Optional caption displayed beneath the image.', max_length=250)),
                ('display_order', models.PositiveIntegerField(default=0, help_text='Lower numbers appear first.')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('case_study', models.ForeignKey(
                    help_text='The case study this image belongs to.',
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='images',
                    to='banners.casestudy',
                )),
            ],
            options={
                'verbose_name': 'Case Study Image',
                'verbose_name_plural': 'Case Study Images',
                'ordering': ['display_order', 'created_at'],
            },
        ),
    ]
