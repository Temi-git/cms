import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('banners', '0004_banner_media_type_banner_video_file_banner_video_url_and_more'),
    ]

    operations = [

        # --------------------------------------------------------
        # ThingWeDo
        # --------------------------------------------------------
        migrations.CreateModel(
            name='ThingWeDo',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('is_active', models.BooleanField(default=True, help_text='Designates whether this content is enabled by an administrator.')),
                ('publish_start', models.DateTimeField(blank=True, help_text='Optional start of the publishing window.', null=True)),
                ('publish_end', models.DateTimeField(blank=True, help_text='Optional end of the publishing window.', null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('title', models.CharField(help_text='Title of the service (e.g., \'LFD & Smart Signage\').', max_length=200)),
                ('description', models.TextField(blank=True, help_text='Description of the service.')),
                ('image', models.ImageField(blank=True, help_text='Optional image for this service.', null=True, upload_to='things_we_do/')),
                ('display_order', models.PositiveIntegerField(default=0, help_text='Lower numbers appear first.')),
                ('entity', models.ForeignKey(
                    help_text='Entity this service belongs to.',
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='things_we_do',
                    to='banners.entity',
                )),
            ],
            options={
                'verbose_name': 'Thing We Do',
                'verbose_name_plural': 'Things We Do',
                'ordering': ['display_order', '-created_at'],
                'indexes': [
                    models.Index(fields=['entity', 'is_active', 'display_order'], name='banners_thi_entity__idx'),
                ],
            },
        ),

        # --------------------------------------------------------
        # CybersecuritySolution
        # --------------------------------------------------------
        migrations.CreateModel(
            name='CybersecuritySolution',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('is_active', models.BooleanField(default=True, help_text='Designates whether this content is enabled by an administrator.')),
                ('publish_start', models.DateTimeField(blank=True, help_text='Optional start of the publishing window.', null=True)),
                ('publish_end', models.DateTimeField(blank=True, help_text='Optional end of the publishing window.', null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('title', models.CharField(help_text='Title of the cybersecurity solution (e.g., \'Vulnerability Assessment\').', max_length=200)),
                ('description', models.TextField(blank=True, help_text='Description of the cybersecurity solution.')),
                ('image', models.ImageField(help_text='Solution image.', upload_to='cybersecurity_solutions/')),
                ('display_order', models.PositiveIntegerField(default=0, help_text='Lower numbers appear first.')),
                ('entity', models.ForeignKey(
                    help_text='Entity this cybersecurity solution belongs to.',
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='cybersecurity_solutions',
                    to='banners.entity',
                )),
            ],
            options={
                'verbose_name': 'Cybersecurity Solution',
                'verbose_name_plural': 'Cybersecurity Solutions',
                'ordering': ['display_order', '-created_at'],
                'indexes': [
                    models.Index(fields=['entity', 'is_active', 'display_order'], name='banners_cyb_entity__idx'),
                ],
            },
        ),

        # --------------------------------------------------------
        # Project
        # --------------------------------------------------------
        migrations.CreateModel(
            name='Project',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('is_active', models.BooleanField(default=True, help_text='Designates whether this content is enabled by an administrator.')),
                ('publish_start', models.DateTimeField(blank=True, help_text='Optional start of the publishing window.', null=True)),
                ('publish_end', models.DateTimeField(blank=True, help_text='Optional end of the publishing window.', null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('title', models.CharField(help_text='Project title (e.g., \'Videowall & NOC\').', max_length=200)),
                ('category', models.CharField(blank=True, help_text='Project category or industry (e.g., \'NOC\', \'Cybersecurity\').', max_length=200)),
                ('description', models.TextField(blank=True, help_text='Project description.')),
                ('image', models.ImageField(help_text='Main project image.', upload_to='projects/')),
                ('project_url', models.URLField(blank=True, help_text='Optional URL for the project case study.')),
                ('display_order', models.PositiveIntegerField(default=0, help_text='Lower numbers appear first.')),
                ('entity', models.ForeignKey(
                    help_text='Entity this project belongs to.',
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='projects',
                    to='banners.entity',
                )),
            ],
            options={
                'verbose_name': 'Project',
                'verbose_name_plural': 'Work We Are Proud Of',
                'ordering': ['display_order', '-created_at'],
                'indexes': [
                    models.Index(fields=['entity', 'is_active', 'display_order'], name='banners_pro_entity__proj_idx'),
                ],
            },
        ),

        # --------------------------------------------------------
        # BlogPost
        # --------------------------------------------------------
        migrations.CreateModel(
            name='BlogPost',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('is_active', models.BooleanField(default=True, help_text='Designates whether this content is enabled by an administrator.')),
                ('publish_start', models.DateTimeField(blank=True, help_text='Optional start of the publishing window.', null=True)),
                ('publish_end', models.DateTimeField(blank=True, help_text='Optional end of the publishing window.', null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('title', models.CharField(help_text='Blog post title.', max_length=250)),
                ('slug', models.SlugField(blank=True, help_text='URL-friendly version of the blog title.', max_length=250, unique=True)),
                ('image', models.ImageField(blank=True, help_text='Featured image for the blog post.', null=True, upload_to='blog_posts/')),
                ('excerpt', models.TextField(blank=True, help_text='Short preview text shown on the homepage.')),
                ('content', models.TextField(help_text='Full blog post content.')),
                ('published_at', models.DateTimeField(blank=True, help_text='Date and time the blog post was published.', null=True)),
                ('display_order', models.PositiveIntegerField(default=0, help_text='Optional homepage display order.')),
                ('entity', models.ForeignKey(
                    help_text='Entity this blog post belongs to.',
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='blog_posts',
                    to='banners.entity',
                )),
            ],
            options={
                'verbose_name': 'Blog Post',
                'verbose_name_plural': 'Blog Posts',
                'ordering': ['-published_at', '-created_at'],
                'indexes': [
                    models.Index(fields=['entity', 'is_active', 'published_at'], name='banners_blo_entity__idx'),
                ],
            },
        ),
    ]
