import os, sys, django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'banner_project.settings')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
django.setup()

from django.core.management import call_command
from io import StringIO

print("=== migrate banners ===")
call_command('migrate', 'banners', verbosity=2)

print("\n=== django check ===")
buf = StringIO()
try:
    call_command('check', stdout=buf)
    print(buf.getvalue().strip() or "System check identified no issues (0 silenced).")
except SystemExit as e:
    print(f"Exit {e.code}: {buf.getvalue()}")

print("\n=== makemigrations --check ===")
buf2 = StringIO()
try:
    call_command('makemigrations', '--check', verbosity=1, stdout=buf2, stderr=buf2)
    print("No drift — models and migrations are in sync.")
except SystemExit as e:
    if e.code == 0:
        print("No drift (exit 0).")
    else:
        print(f"DRIFT DETECTED (exit {e.code}):\n{buf2.getvalue()}")

print("\n=== confirm proxy_title column in DB ===")
import sqlite3
conn = sqlite3.connect('db.sqlite3')
cur = conn.cursor()
cur.execute("PRAGMA table_info(banners_banner)")
cols = {row[1] for row in cur.fetchall()}
if 'proxy_title' in cols:
    print("  [PASS] proxy_title column exists in banners_banner")
else:
    print("  [FAIL] proxy_title column NOT found in banners_banner")
conn.close()
