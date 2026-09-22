import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('banners', '0006_rename_banners_blo_entity__idx_banners_blo_entity__34f1fd_idx_and_more'),
    ]

    operations = [

        # --------------------------------------------------------
        # Recognition
        # --------------------------------------------------------
        migrations.CreateModel(
            name='Recognition',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('is_active', models.BooleanField(default=True, help_text='Designates whether this content is enabled by an administrator.')),
                ('publish_start', models.DateTimeField(blank=True, help_text='Optional start of the publishing window.', null=True)),
                ('publish_end', models.DateTimeField(blank=True, help_text='Optional end of the publishing window.', null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('title', models.CharField(help_text='Name of the award or certificate (e.g., \'ISO 27001 Certified\').', max_length=200)),
                ('issuing_organization', models.CharField(blank=True, help_text='Organization that issued the award or certificate.', max_length=200)),
                ('description', models.TextField(blank=True, help_text='Optional description or context for this recognition.')),
                ('image', models.ImageField(blank=True, help_text='Certificate, badge, or logo image.', null=True, upload_to='recognitions/')),
                ('year', models.CharField(blank=True, help_text="Year received (e.g., '2024'). Optional.", max_length=10)),
                ('display_order', models.PositiveIntegerField(default=0, help_text='Lower numbers appear first.')),
                ('entity', models.ForeignKey(
                    help_text='Entity this recognition belongs to.',
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='recognitions',
                    to='banners.entity',
                )),
            ],
            options={
                'verbose_name': 'Recognition',
                'verbose_name_plural': 'Recognitions',
                'ordering': ['display_order', '-created_at'],
                'indexes': [
                    models.Index(
                        fields=['entity', 'is_active', 'display_order'],
                        name='banners_rec_entity__a1b2c3_idx',
                    ),
                ],
            },
        ),

        # --------------------------------------------------------
        # TeamCertificate
        # --------------------------------------------------------
        migrations.CreateModel(
            name='TeamCertificate',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('is_active', models.BooleanField(default=True, help_text='Designates whether this content is enabled by an administrator.')),
                ('publish_start', models.DateTimeField(blank=True, help_text='Optional start of the publishing window.', null=True)),
                ('publish_end', models.DateTimeField(blank=True, help_text='Optional end of the publishing window.', null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('title', models.CharField(help_text="Name of the certification (e.g., 'Cisco CCNP').", max_length=200)),
                ('issuing_organization', models.CharField(blank=True, help_text="Organization that issued the certification (e.g., 'Cisco', 'Microsoft').", max_length=200)),
                ('description', models.TextField(blank=True, help_text='Optional description of the certification and its relevance.')),
                ('image', models.ImageField(blank=True, help_text='Certification logo or badge image.', null=True, upload_to='team_certificates/')),
                ('year', models.CharField(blank=True, help_text="Year the certification was achieved (e.g., '2024'). Optional.", max_length=10)),
                ('display_order', models.PositiveIntegerField(default=0, help_text='Lower numbers appear first.')),
                ('entity', models.ForeignKey(
                    help_text='Entity this team certificate belongs to.',
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='team_certificates',
                    to='banners.entity',
                )),
            ],
            options={
                'verbose_name': 'Team Certificate',
                'verbose_name_plural': 'Team Certificates',
                'ordering': ['display_order', '-created_at'],
                'indexes': [
                    models.Index(
                        fields=['entity', 'is_active', 'display_order'],
                        name='banners_tc_entity__d4e5f6_idx',
                    ),
                ],
            },
        ),
    ]
