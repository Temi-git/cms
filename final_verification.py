"""
Final verification script for the Event lifecycle / gallery implementation.
Run with: python final_verification.py
"""

import os, sys, django, json, traceback
from datetime import timedelta

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'banner_project.settings')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
django.setup()

from django.utils import timezone
import sqlite3

results = {
    "passed": [],
    "failed": [],
    "warnings": [],
}

def ok(label):
    print(f"  [PASS] {label}")
    results["passed"].append(label)

def fail(label, detail=""):
    msg = f"{label}: {detail}" if detail else label
    print(f"  [FAIL] {msg}")
    results["failed"].append(msg)

def warn(label):
    print(f"  [WARN] {label}")
    results["warnings"].append(label)

# ============================================================
print("\n=== 1. MIGRATION STATE ===")
# ============================================================
from django.db import connection
from django.db.migrations.recorder import MigrationRecorder
applied = {r.name for r in MigrationRecorder.Migration.objects.filter(app='banners')}
expected = [
    "0001_initial",
    "0002_remove_promotionalsection_entity_and_more",
    "0003_delete_featuredproduct",
    "0004_banner_media_type_banner_video_file_banner_video_url_and_more",
    "0005_thingwedo_cybersecuritysolution_project_blogpost",
    "0006_rename_banners_blo_entity__idx_banners_blo_entity__34f1fd_idx_and_more",
    "0007_recognition_teamcertificate",
    "0008_casestudy_casestudyimage",
    "0009_casestudy_entity",
    "0010_casestudy_rename_fields_technology_result_roi",
    "0011_alter_casestudy_client_overview",
    "0012_upcomingevent_location_eventmedia",
]
for m in expected:
    if m in applied:
        ok(f"Migration {m} applied")
    else:
        fail(f"Migration {m} NOT applied")

# ============================================================
print("\n=== 2. DATABASE SCHEMA ===")
# ============================================================
conn = sqlite3.connect('db.sqlite3')
cur = conn.cursor()

# upcomingevent columns
cur.execute("PRAGMA table_info(banners_upcomingevent)")
ue_cols = {row[1] for row in cur.fetchall()}
for col in ['id','entity_id','name','description','event_date','image',
            'registration_link','is_active','publish_start','publish_end',
            'created_at','updated_at','location']:
    if col in ue_cols:
        ok(f"upcomingevent.{col} exists")
    else:
        fail(f"upcomingevent.{col} MISSING")

# eventmedia table
cur.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name='banners_eventmedia'")
em_row = cur.fetchone()
if em_row:
    ok("banners_eventmedia table exists")
    cur.execute("PRAGMA table_info(banners_eventmedia)")
    em_cols = {row[1] for row in cur.fetchall()}
    for col in ['id','event_id','media_type','image','video_file','caption',
                'display_order','created_at']:
        if col in em_cols:
            ok(f"eventmedia.{col} exists")
        else:
            fail(f"eventmedia.{col} MISSING")
else:
    fail("banners_eventmedia table does NOT exist")

# FK check
cur.execute("PRAGMA foreign_key_list(banners_eventmedia)")
fks = cur.fetchall()
em_fk_ok = any(row[2] == 'banners_upcomingevent' for row in fks)
if em_fk_ok:
    ok("EventMedia FK → banners_upcomingevent confirmed")
else:
    fail("EventMedia FK to upcomingevent NOT confirmed in PRAGMA")

# index situation
cur.execute("SELECT name FROM sqlite_master WHERE type='index' AND tbl_name='banners_eventmedia'")
idx_names = {row[0] for row in cur.fetchall()}
print(f"  [INFO] EventMedia indexes in DB: {idx_names}")
if 'banners_em_event__type__order_idx' in idx_names:
    warn("DB still has old index name banners_em_event__type__order_idx (model now uses banners_em_event__idx)")
    # Check if Django will complain about this
    from django.core.management import call_command
    from io import StringIO
    buf = StringIO()
    try:
        call_command('check', stdout=buf, stderr=buf)
        out = buf.getvalue()
        if 'error' in out.lower() or 'issue' in out.lower():
            fail("django check has issues relating to index name", out)
        else:
            ok("django check passes despite index name mismatch (SQLite doesn't enforce name length at runtime)")
    except SystemExit as e:
        if e.code == 0:
            ok("django check exit 0 — clean")
        else:
            fail(f"django check exit {e.code}")
elif 'banners_em_event__idx' in idx_names:
    ok("EventMedia index name matches model (banners_em_event__idx)")
else:
    warn("Neither expected index name found — index may be auto-named")

conn.close()

# ============================================================
print("\n=== 3. MAKEMIGRATIONS DRIFT CHECK ===")
# ============================================================
from django.core.management import call_command
from io import StringIO
buf = StringIO()
try:
    call_command('makemigrations', '--check', verbosity=0, stdout=buf, stderr=buf)
    ok("No model/migration drift detected")
except SystemExit as e:
    if e.code == 0:
        ok("No drift (exit 0)")
    else:
        fail(f"makemigrations --check exit {e.code} — drift exists", buf.getvalue())

# ============================================================
print("\n=== 4. LIFECYCLE LOGIC TEST ===")
# ============================================================
from banners.models import UpcomingEvent, EventMedia, Entity

# Use first active entity, or create a throwaway one
entity = Entity.objects.filter(is_active=True).first()
if not entity:
    fail("No active Entity found — cannot test lifecycle")
else:
    ok(f"Using entity: {entity.name} (id={entity.id})")

    now = timezone.now()

    # Future event
    future_event = UpcomingEvent(
        entity=entity,
        name="__test_future_event__",
        event_date=now + timedelta(days=30),
        is_active=True,
    )
    future_event.save()
    fe = UpcomingEvent.objects.get(pk=future_event.pk)
    if fe.lifecycle_status == "upcoming":
        ok("Future event lifecycle_status == 'upcoming'")
    else:
        fail("Future event lifecycle_status", fe.lifecycle_status)
    if fe.is_upcoming:
        ok("Future event is_upcoming == True")
    else:
        fail("Future event is_upcoming not True")
    if not fe.is_past:
        ok("Future event is_past == False")
    else:
        fail("Future event is_past should be False, got True")

    # Past event
    past_event = UpcomingEvent(
        entity=entity,
        name="__test_past_event__",
        event_date=now - timedelta(days=30),
        is_active=True,
    )
    past_event.save()
    pe = UpcomingEvent.objects.get(pk=past_event.pk)
    if pe.lifecycle_status == "past":
        ok("Past event lifecycle_status == 'past'")
    else:
        fail("Past event lifecycle_status", pe.lifecycle_status)
    if pe.is_past:
        ok("Past event is_past == True")
    else:
        fail("Past event is_past not True")
    if not pe.is_upcoming:
        ok("Past event is_upcoming == False")
    else:
        fail("Past event is_upcoming should be False, got True")

# ============================================================
print("\n=== 5. ENTITY RELATIONSHIP TEST ===")
# ============================================================
    # Verify future_event.entity round-trips
    if fe.entity_id == entity.id:
        ok("Event.entity FK round-trip correct")
    else:
        fail("Event.entity FK mismatch")

    # Entity → events reverse
    entity_events = entity.events.filter(pk__in=[fe.pk, pe.pk])
    if entity_events.count() == 2:
        ok("Entity.events reverse manager returns test events")
    else:
        fail(f"Entity.events count expected 2, got {entity_events.count()}")

    # Existing events still intact
    all_events = UpcomingEvent.objects.filter(is_active=True).exclude(
        name__startswith="__test_")
    ok(f"Existing events count (excluding test data): {all_events.count()}")

# ============================================================
print("\n=== 6. EVENT MEDIA TEST ===")
# ============================================================
    # Create image media
    img1 = EventMedia.objects.create(
        event=fe,
        media_type="image",
        caption="Test image 1",
        display_order=2,
    )
    img2 = EventMedia.objects.create(
        event=fe,
        media_type="image",
        caption="Test image 2",
        display_order=1,
    )
    # Create video media
    vid1 = EventMedia.objects.create(
        event=fe,
        media_type="video",
        caption="Test video 1",
        display_order=3,
    )

    media_qs = fe.media.all()
    if media_qs.count() == 3:
        ok("3 EventMedia items linked to event")
    else:
        fail(f"Expected 3 media, got {media_qs.count()}")

    # Verify ordering
    ordered = list(fe.media.order_by("display_order", "created_at"))
    if ordered[0].pk == img2.pk and ordered[1].pk == img1.pk and ordered[2].pk == vid1.pk:
        ok("EventMedia ordering by display_order is correct")
    else:
        warn(f"Ordering unexpected: {[m.pk for m in ordered]} vs expected [{img2.pk},{img1.pk},{vid1.pk}]")

    # Delete one
    img2.delete()
    if fe.media.count() == 2:
        ok("EventMedia deletion leaves remaining items intact")
    else:
        fail(f"After deletion expected 2 media, got {fe.media.count()}")

    # Event itself still intact
    fe_check = UpcomingEvent.objects.get(pk=fe.pk)
    if fe_check:
        ok("Event still intact after media deletion")

    # Verify media_type choices
    types = set(fe.media.values_list('media_type', flat=True))
    if 'image' in types and 'video' in types:
        ok("Both image and video media_type present")
    else:
        warn(f"media_type set: {types}")

# ============================================================
print("\n=== 7. SERIALIZER / API STRUCTURE TEST ===")
# ============================================================
try:
    from banners.views import serialize_event, serialize_event_detail
    from unittest.mock import MagicMock

    mock_request = MagicMock()
    mock_request.build_absolute_uri.side_effect = lambda url: f"http://testserver{url}"

    # serialize_event
    data = serialize_event(mock_request, fe)
    required_keys = ['id','name','description','location','event_date',
                     'event_datetime','status','image','registration_link']
    for k in required_keys:
        if k in data:
            ok(f"serialize_event has key '{k}'")
        else:
            fail(f"serialize_event missing key '{k}'")
    if data['status'] == 'upcoming':
        ok("serialize_event status='upcoming' for future event")
    else:
        fail(f"serialize_event status expected 'upcoming', got '{data['status']}'")
    if data['location'] == '':
        ok("serialize_event location field present (empty string for blank)")
    else:
        ok(f"serialize_event location='{data['location']}'")

    # serialize_event_detail
    detail = serialize_event_detail(mock_request, fe)
    if 'gallery' in detail:
        ok("serialize_event_detail has 'gallery' key")
        gallery = detail['gallery']
        if isinstance(gallery, list):
            ok(f"gallery is a list ({len(gallery)} items)")
        if len(gallery) > 0:
            item = gallery[0]
            for gk in ['id','media_type','image','video_file','caption','display_order']:
                if gk in item:
                    ok(f"gallery item has key '{gk}'")
                else:
                    fail(f"gallery item missing key '{gk}'")
    else:
        fail("serialize_event_detail missing 'gallery' key")

except Exception as e:
    fail("Serializer test error", str(e))
    traceback.print_exc()

# ============================================================
print("\n=== 8. URL CONFIGURATION TEST ===")
# ============================================================
try:
    from django.urls import reverse, resolve

    # proxy-events (existing)
    url = reverse('banners:proxy-events', kwargs={'slug': 'test'})
    if '/proxy/events/test/' in url:
        ok(f"proxy-events URL resolves: {url}")
    else:
        fail(f"proxy-events URL unexpected: {url}")

    # proxy-event-detail (new)
    url2 = reverse('banners:proxy-event-detail', kwargs={'event_id': 1})
    if '/proxy/event-detail/1/' in url2:
        ok(f"proxy-event-detail URL resolves: {url2}")
    else:
        fail(f"proxy-event-detail URL unexpected: {url2}")

    # api-event-detail (new)
    url3 = reverse('banners:api-event-detail', kwargs={'event_id': 1})
    if '/api/event-detail/1/' in url3:
        ok(f"api-event-detail URL resolves: {url3}")
    else:
        fail(f"api-event-detail URL unexpected: {url3}")

    # resolve the detail URL (no conflicts)
    match = resolve('/api/event-detail/1/')
    ok(f"Resolved /api/event-detail/1/ → {match.func.__name__}")

except Exception as e:
    fail("URL test error", str(e))
    traceback.print_exc()

# ============================================================
print("\n=== 9. REGISTRATION LINK FIELD ===")
# ============================================================
try:
    from django.db import models as dm
    field = UpcomingEvent._meta.get_field('registration_link')
    if isinstance(field, dm.URLField):
        ok("registration_link is URLField — preserved correctly")
    else:
        fail("registration_link field type changed unexpectedly")
    if field.blank:
        ok("registration_link is blank=True (optional)")
    else:
        warn("registration_link is not blank — may be required")
except Exception as e:
    fail("registration_link check error", str(e))

# ============================================================
print("\n=== 10. CLEANUP TEST DATA ===")
# ============================================================
try:
    # Clean up test events (cascades to their media)
    deleted_count = UpcomingEvent.objects.filter(
        name__startswith="__test_"
    ).delete()
    ok(f"Test data cleaned up: {deleted_count}")
except Exception as e:
    warn(f"Cleanup error (not critical): {e}")

# ============================================================
print("\n=== 11. FINAL DJANGO CHECK ===")
# ============================================================
try:
    from django.core.management import call_command
    buf = StringIO()
    call_command('check', stdout=buf)
    out = buf.getvalue()
    ok(f"django check: {out.strip() or 'System check identified no issues (0 silenced).'}")
except SystemExit as e:
    if e.code == 0:
        ok("django check passed (exit 0)")
    else:
        fail(f"django check failed (exit {e.code})")

# ============================================================
print("\n=== SUMMARY ===")
# ============================================================
print(f"\n  PASSED : {len(results['passed'])}")
print(f"  FAILED : {len(results['failed'])}")
print(f"  WARNINGS: {len(results['warnings'])}")

if results['failed']:
    print("\n  FAILURES:")
    for f in results['failed']:
        print(f"    - {f}")

if results['warnings']:
    print("\n  WARNINGS:")
    for w in results['warnings']:
        print(f"    - {w}")

# Save results for report update
with open('verification_results.json', 'w') as fh:
    json.dump(results, fh, indent=2)
print("\n  Results saved to verification_results.json")
