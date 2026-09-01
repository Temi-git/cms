from django.db.models import Q
from django.utils import timezone


def build_media_url(request, file_field):
    if not file_field:
        return ''
    try:
        return request.build_absolute_uri(file_field.url)
    except Exception:
        return ''


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


def serialize_banner(request, banner):
    return {
        'id': banner.id,
        'title': banner.title or '',
        'text': banner.text or '',
        'link': banner.link or '',
        'image': build_media_url(request, banner.image),
        'display_order': banner.display_order,
    }


def serialize_event(request, event):
    return {
        'id': event.id,
        'name': event.name or '',
        'description': event.description or '',
        'event_date': (
            event.event_date.strftime('%B %d, %Y')
            if event.event_date
            else ''
        ),
        'event_datetime': (
            event.event_date.isoformat()
            if event.event_date
            else ''
        ),
        'image': build_media_url(request, event.image),
        'registration_link': event.registration_link or '',
    }


def serialize_gif(request, gif):
    return {
        'id': gif.id,
        'title': gif.title or '',
        'description': gif.description or '',
        'media_file': build_media_url(request, gif.media_file),
        'link': gif.link or '',
        'display_order': gif.display_order,
    }



def serialize_flash_sale(request, flash_sale):
    return {
        'id': flash_sale.id,
        'title': flash_sale.title or '',
        'description': flash_sale.description or '',
        'image': build_media_url(request, flash_sale.image),
        'start_datetime': flash_sale.start_datetime.isoformat(),
        'end_datetime': flash_sale.end_datetime.isoformat(),
        'is_live': flash_sale.is_currently_visible(),
        'seconds_remaining': flash_sale.seconds_remaining,
        'display_order': flash_sale.display_order,
    }



def serialize_today_deal(request, deal):
    return {
        'id': deal.id,
        'title': deal.title or '',
        'subtitle': deal.subtitle or '',
        'image': build_media_url(request, deal.image),
        'product_id': deal.product.id if deal.product else None,
        'start_datetime': deal.start_datetime.isoformat(),
        'end_datetime': deal.end_datetime.isoformat(),
        'is_live': deal.is_currently_visible(),
        'seconds_remaining': deal.seconds_remaining,
        'display_order': deal.display_order,
    }


def serialize_affiliate_banner(request, banner):
    return {
        'id': banner.id,
        'title': banner.title or '',
        'image': build_media_url(request, banner.image),
        'affiliate_url': banner.affiliate_url or '',
        'display_order': banner.display_order,
    }


def build_homepage_payload(request, entity):
    banners = filter_publishable(
        entity.banners.all()
    ).order_by('display_order', '-created_at')

    gifs = filter_publishable(
        entity.gifs.all()
    ).order_by('display_order', '-created_at')

   
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
        'gifs': [serialize_gif(request, item) for item in gifs],
        'flash_sales': [
            serialize_flash_sale(request, item)
            for item in flash_sales
        ],
        'today_deals': [
            serialize_today_deal(request, item)
            for item in today_deals
        ],
        'affiliate_banners': [
            serialize_affiliate_banner(request, item)
            for item in affiliate_banners
        ],
        'events': [serialize_event(request, item) for item in events],
        
    }