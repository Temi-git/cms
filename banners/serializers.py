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


# def serialize_gif(request, gif):
#     return {
#         "id": gif.id,
#         "title": gif.title or "",
#         "description": gif.description or "",
#         "media_file": build_media_url(request, gif.media_file),
#         "link": gif.link or "",
#         "display_order": gif.display_order,
#     }


def serialize_affiliate_banner(request, banner):
    data = {
        "id": banner.id,
        "title": banner.title or "",
        "image": build_media_url(request, banner.image),
        "placement": banner.placement,
        "display_order": banner.display_order,
    }

    if banner.placement == "program":
        data["affiliate_url"] = banner.affiliate_url or ""

    return data




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
        "buy_now_url": deal.buy_now_url or "",
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
    """Lightweight serializer for listing cards â€” includes related items."""
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


# ============================================================
# PROMALLSHOP CATALOG SERIALIZERS
# ============================================================
# Note: 'from django.conf import settings' is imported below to avoid
# shadowing any variable named 'settings' in this module scope.
from django.conf import settings as _django_settings  # noqa: E402


def build_promall_image_urls(request, product):
    """
    Returns a list of absolute image URL strings for a PromallProduct.

    Priority:
    1. Admin-uploaded image (product.image) -> built with build_media_url.
    2. External image paths from product.external_image_paths -> built using
       PROMALL_EXTERNAL_MEDIA_BASE_URL + path.
    """
    urls = []
    if product.image:
        url = build_media_url(request, product.image)
        if url:
            urls.append(url)
    if product.external_image_paths:
        base = (_django_settings.PROMALL_EXTERNAL_MEDIA_BASE_URL or '').rstrip('/')
        for raw_path in product.external_image_paths.split(','):
            path = raw_path.strip()
            if path:
                urls.append(base + '/' + path.lstrip('/'))
    return urls


def serialize_promall_subcategory(request, sub):
    return {
        'id': sub.id,
        'external_id': sub.external_id or '',
        'name': sub.name or '',
        'slug': sub.slug or '',
        'display_order': sub.display_order,
    }


def serialize_promall_category(request, cat):
    return {
        'id': cat.id,
        'external_id': cat.external_id or '',
        'name': cat.name or '',
        'slug': cat.slug or '',
        'description': cat.description or '',
        'icon': build_media_url(request, cat.icon),
        'display_order': cat.display_order,
        'subcategories': [
            serialize_promall_subcategory(request, sub)
            for sub in cat.subcategories.filter(is_active=True)
                                        .order_by('display_order', 'name')
        ],
    }


def serialize_promall_category_detail(request, cat):
    data = serialize_promall_category(request, cat)
    data['faqs'] = [
        {
            'id': faq.id,
            'question': faq.question or '',
            'answer': faq.answer or '',
            'display_order': faq.display_order,
        }
        for faq in cat.faqs.filter(is_active=True).order_by('display_order', 'created_at')
    ]
    return data


def serialize_promall_product_list(request, product):
    images = build_promall_image_urls(request, product)
    badge = 'HOT' if product.is_hot else ('SPECIAL' if product.is_special else '')
    return {
        'id': product.id,
        'external_id': product.external_id or '',
        'name': product.name or '',
        'slug': product.slug or '',
        'short_description': product.short_description or '',
        'category_id': product.category_id,
        'category_name': product.category.name if product.category_id else '',
        'subcategory_id': product.subcategory_id,
        'subcategory_name': (product.subcategory.name if product.subcategory else ''),
        'price': str(product.price) if product.price is not None else '',
        'end_user_price': str(product.end_user_price) if product.end_user_price is not None else '',
        'discount': str(product.discount) if product.discount is not None else '',
        'is_hot': product.is_hot,
        'is_special': product.is_special,
        'display_order': product.display_order,
        'image': images[0] if images else '',
        'badge': badge,
    }


def serialize_promall_banner(request, banner):
    """
    Serializer for PromallBanner (Promallshop's dedicated main homepage banners).
    Does NOT include button_text or button_link - those fields have been removed
    from the model and will be dropped from the DB once migration 0037 is applied.
    """
    return {
        "id": banner.id,
        "title": banner.title or "",
        "description": banner.description or "",
        "image": build_media_url(request, banner.image),
        "display_order": banner.display_order,
    }


def serialize_promall_event(request, event):
    """
    Serializer for PromallEvent (Promallshop-specific events).
    Uses event_datetime (not event_date) and exposes event_type as a nested object.
    """
    return {
        "id": event.id,
        "name": event.name or "",
        "description": event.description or "",
        "event_datetime": (
            event.event_datetime.isoformat()
            if event.event_datetime
            else ""
        ),
        "location": event.location or "",
        "event_type": (
            {
                "id": event.event_type.id,
                "name": event.event_type.name,
                "slug": event.event_type.slug,
            }
            if event.event_type
            else None
        ),
        "image": build_media_url(request, event.image),
        "registration_link": event.registration_link or "",
        "display_order": event.display_order,
    }


def serialize_promall_event_type(event_type):
    """
    Serializer for PromallEventType.
    No request needed - no media fields.
    """
    return {
        "id": event_type.id,
        "name": event_type.name or "",
        "slug": event_type.slug or "",
        "display_order": event_type.display_order,
    }


def serialize_promall_product_detail(request, product):
    data = serialize_promall_product_list(request, product)
    data.update({
        'description': product.description or '',
        'model_number': product.model_number or '',
        'part_number': product.part_number or '',
        'warranty': product.warranty or '',
        'video_url': product.video_url or '',
        'quantity': product.quantity,
        'meta_title': product.meta_title or '',
        'meta_description': product.meta_description or '',
        'keywords': product.keywords or '',
        'all_images': build_promall_image_urls(request, product),
        'faqs': [
            {
                'id': faq.id,
                'question': faq.question or '',
                'answer': faq.answer or '',
                'display_order': faq.display_order,
            }
            for faq in product.faqs.filter(is_active=True).order_by('display_order', 'created_at')
        ],
    })
    return data
