# Multi-Entity Banner Management System

A production-ready Django backend designed to serve promotional banners and upcoming events for multiple entities via RESTful JSON APIs and a feature-packed Django Admin interface.

---

## Features

- **Multi-Entity Support**: Manage multiple organizations/entities, each with its own slug, website URL, banners, and upcoming events.
- **Separate RESTful API Endpoints**:
  - `GET /api/banner/<slug>/`: Returns ONLY active banner data.
  - `GET /api/events/<slug>/`: Returns ONLY active upcoming events data.
  - `GET /api/combined/<slug>/`: Returns BOTH banners and upcoming events (for backward compatibility).
  - `GET /api/entities/`: Returns summary list of active entities and counts.
- **Enhanced Django Admin**:
  - Prepopulated slug fields.
  - Inlines for fast creation of Banners and Upcoming Events (3 empty formsets).
  - List displays showing image thumbnail previews, event date hierarchy, and custom count columns (`banner_count` and `event_count`).
  - Custom Admin actions ("Activate selected banners", "Deactivate selected banners").
- **Automatic Seed Data**: Includes custom management command `python manage.py seed_data` to automatically create test entities, banners with generated test images, upcoming events, and default admin credentials.

---

## Tech Stack & Requirements

- **Python**: 3.10+
- **Framework**: Django 5.0+
- **Image Processing**: Pillow
- **CORS Support**: `django-cors-headers`
- **Database**: SQLite3 (default for local development)

---

## Quick Start Guide

### 1. Prerequisites & Virtual Environment

Clone or download the project folder, then navigate to the root directory:

```bash
# Windows (PowerShell)
python -m venv venv
.\venv\Scripts\Activate.ps1

# Linux / macOS
python3 -m venv venv
source venv/bin/activate
```

### 2. Install Dependencies

Install all required Python packages from `requirements.txt`:

```bash
pip install -r requirements.txt
```

### 3. Run Migrations & Seed Data

Apply database migrations and populate sample test data + admin credentials:

```bash
python manage.py makemigrations
python manage.py migrate
python manage.py seed_data
```

> **Default Superuser Credentials:**
> - **Username**: `admin`
> - **Password**: `admin123`
> - **Email**: `admin@example.com`

### 4. Run the Server on Port 8001

Start the Django development server on port **8001**:

```bash
python manage.py runserver 8001
```

Access the Django Admin panel at: **[http://127.0.0.1:8001/admin/](http://127.0.0.1:8001/admin/)**

---

## API Documentation

All API endpoints return JSON and include CORS preflight headers (`Access-Control-Allow-Origin: *`).

### 1. Get Banner Data Only

- **Endpoint**: `GET /api/banner/<slug>/`
- **Example Request**: `GET http://127.0.0.1:8001/api/banner/tech-corp/`

#### Sample Success Response (`200 OK`):

```json
{
    "status": "success",
    "entity": "TechCorp Solutions",
    "slug": "tech-corp",
    "banners": [
        {
            "title": "Summer Sale 2026",
            "text": "Get 50% off all software licenses during our annual summer event.",
            "link": "https://techcorp.example.com/summer-sale",
            "image": "http://127.0.0.1:8001/media/banners/summer_sale.png"
        },
        {
            "title": "Cloud Migration Offer",
            "text": "Upgrade your legacy systems to our cloud platform today.",
            "link": "https://techcorp.example.com/cloud",
            "image": "http://127.0.0.1:8001/media/banners/cloud_offer.png"
        }
    ]
}
```

---

### 2. Get Upcoming Events Data Only

- **Endpoint**: `GET /api/events/<slug>/`
- **Example Request**: `GET http://127.0.0.1:8001/api/events/tech-corp/`

#### Sample Success Response (`200 OK`):

```json
{
    "status": "success",
    "entity": "TechCorp Solutions",
    "slug": "tech-corp",
    "upcoming_events": [
        {
            "name": "Global Tech Developer Summit",
            "description": "Annual developer conference bringing together engineers worldwide.",
            "event_date": "November 20, 2026"
        },
        {
            "name": "Product Launch 2026",
            "description": "Join us live for the grand unveil of our next-gen platform.",
            "event_date": "December 15, 2026"
        }
    ]
}
```

---

### 3. Get Combined Banners & Events (Backward Compatibility)

- **Endpoint**: `GET /api/combined/<slug>/`
- **Example Request**: `GET http://127.0.0.1:8001/api/combined/tech-corp/`

---

### 4. List All Active Entities

- **Endpoint**: `GET /api/entities/`
- **Example Request**: `GET http://127.0.0.1:8001/api/entities/`

---

## Running Unit Tests

To run the automated Django test suite:

```bash
python manage.py test
```
