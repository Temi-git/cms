"""
Migration 0010 — Case Study field renames + new related models

Operations in order:
  1. RenameField  client_background → client_overview   (data preserved by rename)
  2. RenameField  results           → result_roi         (data preserved by rename)
  3. CreateModel  CaseStudyTechnology
  4. CreateModel  CaseStudyResultROI
  5. RunPython    data migration — copy non-empty result_roi text into
                  one CaseStudyResultROI record per case study
  6. RemoveField  casestudy.result_roi                  (now safe to drop)
"""

import django.db.models.deletion
from django.db import migrations, models


def copy_results_to_result_roi(apps, schema_editor):
    """
    For every CaseStudy that has non-empty result_roi text,
    create exactly one CaseStudyResultROI record with:
      - content = the existing result_roi text
      - display_order = 1
    """
    CaseStudy = apps.get_model('banners', 'CaseStudy')
    CaseStudyResultROI = apps.get_model('banners', 'CaseStudyResultROI')

    for cs in CaseStudy.objects.all():
        text = (cs.result_roi or '').strip()
        if text:
            CaseStudyResultROI.objects.create(
                case_study=cs,
                content=text,
                display_order=1,
            )


def reverse_copy_results(apps, schema_editor):
    """
    Reverse: copy the first CaseStudyResultROI item back into
    CaseStudy.result_roi so the field is restored on rollback.
    """
    CaseStudy = apps.get_model('banners', 'CaseStudy')
    CaseStudyResultROI = apps.get_model('banners', 'CaseStudyResultROI')

    for cs in CaseStudy.objects.all():
        first = (
            CaseStudyResultROI.objects
            .filter(case_study=cs)
            .order_by('display_order', 'created_at')
            .first()
        )
        if first:
            cs.result_roi = first.content
            cs.save(update_fields=['result_roi'])


class Migration(migrations.Migration):

    dependencies = [
        ('banners', '0009_casestudy_entity'),
    ]

    operations = [

        # ── Step 1: rename client_background → client_overview ──────────
        migrations.RenameField(
            model_name='casestudy',
            old_name='client_background',
            new_name='client_overview',
        ),

        # ── Step 2: rename results → result_roi ─────────────────────────
        migrations.RenameField(
            model_name='casestudy',
            old_name='results',
            new_name='result_roi',
        ),

        # ── Step 3: create CaseStudyTechnology ──────────────────────────
        migrations.CreateModel(
            name='CaseStudyTechnology',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(
                    help_text="Technology name (e.g., 'Samsung LED Display', 'Taurus TU15').",
                    max_length=200,
                )),
                ('display_order', models.PositiveIntegerField(
                    default=0,
                    help_text='Lower numbers appear first.',
                )),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('case_study', models.ForeignKey(
                    help_text='The case study this technology belongs to.',
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='technologies',
                    to='banners.casestudy',
                )),
            ],
            options={
                'verbose_name': 'Technology Used',
                'verbose_name_plural': 'Technologies Used',
                'ordering': ['display_order', 'created_at'],
            },
        ),

        # ── Step 4: create CaseStudyResultROI ───────────────────────────
        migrations.CreateModel(
            name='CaseStudyResultROI',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('content', models.TextField(
                    help_text="Result or ROI statement (e.g., 'Improved visual communication').",
                )),
                ('display_order', models.PositiveIntegerField(
                    default=0,
                    help_text='Lower numbers appear first.',
                )),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('case_study', models.ForeignKey(
                    help_text='The case study this result belongs to.',
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='result_roi_items',
                    to='banners.casestudy',
                )),
            ],
            options={
                'verbose_name': 'Result & ROI Item',
                'verbose_name_plural': 'Result & ROI Items',
                'ordering': ['display_order', 'created_at'],
            },
        ),

        # ── Step 5: copy existing results text into CaseStudyResultROI ──
        migrations.RunPython(
            copy_results_to_result_roi,
            reverse_code=reverse_copy_results,
        ),

        # ── Step 6: drop the now-redundant result_roi TextField ──────────
        migrations.RemoveField(
            model_name='casestudy',
            name='result_roi',
        ),
    ]
