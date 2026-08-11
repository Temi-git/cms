# BannerControl

Admin-only Django app to manage responsive banners for multiple external websites (Entities).

Quick start

1. Create virtualenv and install dependencies:

```bash
python -m venv .venv
source .venv/Scripts/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

2. Run migrations and create superuser:

```bash
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

3. Open admin at `http://127.0.0.1:8000/admin/` and add Entities and Banners.

Embedding the widget

Add a container with `data-entity` set to the slug of the entity and include the widget script:

```html
<div id="banner-container" data-entity="your-entity-slug"></div>
<script src="https://yourdomain.com/static/js/banner-widget.js"></script>
```

Development notes

- Media files are served from `/media/` in DEBUG.
- Settings include `BANNERCONTROL_AUTO_DEACTIVATE_PREVIOUS` (default True) which deactivates previous active banners when a new one is saved active.
