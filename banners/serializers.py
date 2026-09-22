"""
banners/serializers.py

All serializer functions for the banners app.
Views import from here; helpers (build_media_url, filter_*) stay in api_helpers.py.
"""

from .api_helpers import build_media_url


# ============================================================
# BANNER / MEDIA SERIALIZERS
# ============================================================

def serialize_banner(request, banner):
    return {
        "id": banner.id,
        "title": banner.title or "",
        "proxy_title": banner.proxy_title or "",
        "text": banner.text or "",
        "link": banner.link or "",
        "image": build_media_url(request, banner.image),
        "media_type": banner.media_type or "image",
        "video_file": build_media_url(request, banner.video_file),
        "video_url": banner.video_url or "",
        "display_order": banner.display_order,
    }


def serialize_gif(request, gif):
    return {
        "id": gif.id,
        "title": gif.title or "",
        "description": gif.description or "",
        "media_file": build_media_url(request, gif.media_file),
        "link": gif.link or "",
        "display_order": gif.display_order,
    }


def serialize_affiliate_banner(request, banner):
    return {
        "id": banner.id,
        "title": banner.title or "",
        "image": build_media_url(request, banner.image),
        "affiliate_url": banner.affiliate_url or "",
        "display_order": banner.display_order,
    }


# ============================================================
# EVENT SERIALIZERS
# ============================================================

def serialize_event(request, event):
    return {
        "id": event.id,
        "name": event.name or "",
        "description": event.description or "",
        "location": event.location or "",
        "event_type": event.event_type or "",
        "event_date": (
            event.event_date.strftime("%B %d, %Y")
            if event.event_date
            else ""
        ),
        "event_datetime": (
            event.event_date.isoformat()
            if event.event_date
            else ""
        ),
        "status": event.lifecycle_status,
        "image": build_media_url(request, event.image),
        "registration_link": event.registration_link or "",
    }


def serialize_event_detail(request, event):
    """Extended serializer including the event gallery."""
    return {
        "id": event.id,
        "name": event.name or "",
        "description": event.description or "",
        "location": event.location or "",
        "event_type": event.event_type or "",
        "event_date": (
            event.event_date.strftime("%B %d, %Y")
            if event.event_date
            else ""
        ),
        "event_datetime": (
            event.event_date.isoformat()
            if event.event_date
            else ""
        ),
        "status": event.lifecycle_status,
        "image": build_media_url(request, event.image),
        "registration_link": event.registration_link or "",
        "gallery": [
            {
                "id": item.id,
                "media_type": item.media_type,
                "image": build_media_url(request, item.image),
                "video_file": build_media_url(request, item.video_file),
                "caption": item.caption or "",
                "display_order": item.display_order,
            }
            for item in event.media.order_by("display_order", "created_at")
        ],
    }


# ============================================================
# PROMOTION SERIALIZERS
# ============================================================

def serialize_flash_sale(request, flash_sale):
    return {
        "id": flash_sale.id,
        "title": flash_sale.title or "",
        "description": flash_sale.description or "",
        "image": build_media_url(request, flash_sale.image),
        "start_datetime": (
            flash_sale.start_datetime.isoformat()
            if flash_sale.start_datetime
            else ""
        ),
        "end_datetime": (
            flash_sale.end_datetime.isoformat()
            if flash_sale.end_datetime
            else ""
        ),
        "is_live": flash_sale.is_currently_visible(),
        "seconds_remaining": flash_sale.seconds_remaining,
        "display_order": flash_sale.display_order,
    }


def serialize_today_deal(request, deal):
    return {
        "id": deal.id,
        "title": deal.title or "",
        "subtitle": deal.subtitle or "",
        "image": build_media_url(request, deal.image),
        "product_id": deal.product.id if deal.product else None,
        "start_datetime": (
            deal.start_datetime.isoformat()
            if deal.start_datetime
            else ""
        ),
        "end_datetime": (
            deal.end_datetime.isoformat()
            if deal.end_datetime
            else ""
        ),
        "is_live": deal.is_currently_visible(),
        "seconds_remaining": deal.seconds_remaining,
        "display_order": deal.display_order,
    }


# ============================================================
# CONTENT SERIALIZERS (Things We Do, Cybersecurity, Projects, Blog)
# ============================================================

def serialize_thing_we_do(request, thing):
    return {
        "id": thing.id,
        "title": thing.title or "",
        "description": thing.description or "",
        "full_description": thing.full_description or "",
        "image": build_media_url(request, thing.image),
        "display_order": thing.display_order,
    }


def serialize_cybersecurity_solution(request, solution):
    return {
        "id": solution.id,
        "title": solution.title or "",
        "product_name": solution.product_name or "",
        "description": solution.description or "",
        "image": build_media_url(request, solution.image),
        "product_logo": build_media_url(request, solution.product_logo),
        "display_order": solution.display_order,
    }


def serialize_project(request, project):
    return {
        "id": project.id,
        "title": project.title or "",
        "category": project.category or "",
        "description": project.description or "",
        "more_description": project.more_description or "",
        "image": build_media_url(request, project.image),
        "project_url": project.project_url or "",
        "display_order": project.display_order,
    }


def serialize_blog_post(request, post, full=False):
    data = {
        "id": post.id,
        "title": post.title,
        "slug": post.slug,
        "image": build_media_url(request, post.image),
        "excerpt": post.excerpt,
        "published_at": (
            post.published_at.isoformat()
            if post.published_at
            else None
        ),
        "created_at": (
            post.created_at.isoformat()
            if post.created_at
            else None
        ),
        "url": f"/proxy/blog-detail/{post.slug}/",
    }
    if full:
        data["content"] = post.content
    return data


def serialize_recognition(request, obj):
    return {
        "id": obj.id,
        "title": obj.title or "",
        "issuing_organization": obj.issuing_organization or "",
        "description": obj.description or "",
        "image": build_media_url(request, obj.image),
        "year": obj.year or "",
        "display_order": obj.display_order,
    }


def serialize_team_certificate(request, obj):
    return {
        "id": obj.id,
        "title": obj.title or "",
        "issuing_organization": obj.issuing_organization or "",
        "description": obj.description or "",
        "image": build_media_url(request, obj.image),
        "year": obj.year or "",
        "display_order": obj.display_order,
    }


# ============================================================
# CASE STUDY SERIALIZERS
# ============================================================

def _slugify_value(value):
    """Normalize a text value to a URL-safe slug for filtering."""
    from django.utils.text import slugify
    return slugify(value)


def serialize_case_study_image(request, img):
    return {
        "id": img.id,
        "image": build_media_url(request, img.image),
        "caption": img.caption or "",
        "display_order": img.display_order,
    }


def serialize_case_study_list(request, cs):
    """Lightweight serializer for listing cards — includes related items."""
    return {
        "id": cs.id,
        "title": cs.title or "",
        "slug": cs.slug or "",
        "entity_slug": cs.entity.slug if cs.entity else "",
        "entity_name": cs.entity.name if cs.entity else "",
        "client": cs.client or "",
        "solution": cs.solution or "",
        "solution_slug": _slugify_value(cs.solution),
        "industry": cs.industry or "",
        "industry_slug": _slugify_value(cs.industry),
        "country": cs.country or "",
        "country_slug": _slugify_value(cs.country),
        "short_description": cs.short_description or "",
        "featured_image": build_media_url(request, cs.featured_image),
        "display_order": cs.display_order,
        "technologies": [
            {
                "id": tech.id,
                "name": tech.name or "",
                "display_order": tech.display_order,
            }
            for tech in cs.technologies.order_by("display_order", "created_at")
        ],
        "results_roi": [
            {
                "id": item.id,
                "content": item.content or "",
                "display_order": item.display_order,
            }
            for item in cs.result_roi_items.order_by("display_order", "created_at")
        ],
    }


def serialize_case_study_detail(request, cs):
    """Full serializer for the detail page."""
    return {
        "id": cs.id,
        "title": cs.title or "",
        "slug": cs.slug or "",
        "entity_slug": cs.entity.slug if cs.entity else "",
        "entity_name": cs.entity.name if cs.entity else "",
        "client": cs.client or "",
        "solution": cs.solution or "",
        "solution_slug": _slugify_value(cs.solution),
        "industry": cs.industry or "",
        "industry_slug": _slugify_value(cs.industry),
        "country": cs.country or "",
        "country_slug": _slugify_value(cs.country),
        "short_description": cs.short_description or "",
        "featured_image": build_media_url(request, cs.featured_image),
        "client_overview": cs.client_overview or "",
        "challenge": cs.challenge or "",
        "solution_details": cs.solution_details or "",
        "implementation": cs.implementation or "",
        "technologies": [
            {
                "id": tech.id,
                "name": tech.name or "",
                "display_order": tech.display_order,
            }
            for tech in cs.technologies.order_by("display_order", "created_at")
        ],
        "results_roi": [
            {
                "id": item.id,
                "content": item.content or "",
                "display_order": item.display_order,
            }
            for item in cs.result_roi_items.order_by("display_order", "created_at")
        ],
        "display_order": cs.display_order,
        "images": [
            serialize_case_study_image(request, img)
            for img in cs.images.order_by("display_order", "created_at")
        ],
    }


# ============================================================
# TECHNOLOGY PARTNER SERIALIZER
# ============================================================

def serialize_technology_partner(request, partner):
    return {
        "id": partner.id,
        "name": partner.name or "",
        "entity": partner.entity.name if partner.entity else "",
        "description": partner.description or "",
        "logo": build_media_url(request, partner.logo),
        "type": "Authorized Partner",
        "display_order": partner.display_order,
    }
