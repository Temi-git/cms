"""
banners/api_helpers.py

Pure helper utilities: media URL builder, queryset filters,
and the homepage payload builder.

All serializer functions have been moved to banners/serializers.py.
"""

from django.conf import settings
from django.db.models import Q
from django.utils import timezone


# ============================================================
# MEDIA URL HELPER
# ============================================================

def build_media_url(request, file_field):
    if not file_field:
        return ''

    try:
        return f"{settings.SITE_URL}{file_field.url}"
    except Exception:
        return ''

# ============================================================
# QUERYSET FILTERS
# ============================================================

def filter_publishable(queryset):
    now = timezone.now()
    return queryset.filter(
        is_active=True,
    ).filter(
        Q(publish_start__isnull=True) | Q(publish_start__lte=now),
        Q(publish_end__isnull=True) | Q(publish_end__gte=now),
    )


def filter_scheduled(queryset):
    now = timezone.now()
    return queryset.filter(
        is_active=True,
        start_datetime__lte=now,
        end_datetime__gte=now,
    )


# ============================================================
# HOMEPAGE PAYLOAD BUILDER
# ============================================================

def build_homepage_payload(request, entity):
    """
    Builds the core homepage payload dict for an entity.
    Used by views that need the combined homepage data.
    """
    from .serializers import (
        serialize_banner,
        # serialize_gif,
        serialize_flash_sale,
        serialize_today_deal,
        serialize_affiliate_banner,
        serialize_event,
    )
    from .models import Banner

    banners = filter_publishable(
        Banner.objects.filter(entities=entity)
    ).order_by('display_order', '-created_at')

    # gifs = filter_publishable(
    #     entity.gifs.all()
    # ).order_by('display_order', '-created_at')

    flash_sales = filter_scheduled(
        entity.flash_sales.all()
    ).order_by('display_order', '-created_at')

    today_deals = filter_scheduled(
        entity.today_deals.all()
    ).order_by('display_order', '-created_at')

    affiliate_banners = filter_publishable(
        entity.affiliate_banners.all()
    ).order_by('display_order', '-created_at')

    events = filter_publishable(
        entity.events.all()
    ).order_by('event_date')

    return {
        'banners': [serialize_banner(request, item) for item in banners],
        # 'gifs': [serialize_gif(request, item) for item in gifs],
        'flash_sales': [
            serialize_flash_sale(request, item) for item in flash_sales
        ],
        'today_deals': [
            serialize_today_deal(request, item) for item in today_deals
        ],
        'affiliate_banners': [
            serialize_affiliate_banner(request, item)
            for item in affiliate_banners
        ],
        'events': [serialize_event(request, item) for item in events],
    }
