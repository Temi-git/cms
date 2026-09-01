from datetime import datetime

import requests

from django.conf import settings
from django.db import models
from django.http import JsonResponse
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt

from rest_framework.authentication import TokenAuthentication
from rest_framework.decorators import (
    api_view,
    authentication_classes,
    permission_classes,
)
from rest_framework.permissions import IsAuthenticated, AllowAny

from .models import (
    Entity,
    Banner,
    UpcomingEvent,
    HomepageGif,
    FlashSale,
    AffiliateBanner, 
    TodayDeal,
    Product,
)


# ============================================================
# CORS RESPONSE HELPER
# ============================================================

def _cors_json_response(data, status=200):
    """
    Return a JSON response with CORS headers.
    """

    response = JsonResponse(data, status=status)

    response["Access-Control-Allow-Origin"] = "*"
    response["Access-Control-Allow-Methods"] = "GET, OPTIONS"
    response["Access-Control-Allow-Headers"] = "Content-Type, Authorization"

    return response


# ============================================================
# MEDIA URL HELPER
# ============================================================

def build_media_url(request, file_field):
    """
    Convert a Django FileField/ImageField into an absolute URL.
    """

    if not file_field:
        return ""

    try:
        return request.build_absolute_uri(file_field.url)
    except Exception:
        return ""


# ============================================================
# PUBLISHABLE FILTER
# ============================================================

def filter_publishable(queryset):
    """
    Return currently visible PublishableMixin records.

    Conditions:

    is_active=True

    AND

    publish_start is NULL OR publish_start <= now

    AND

    publish_end is NULL OR publish_end >= now
    """

    now = timezone.now()

    return queryset.filter(
        is_active=True,
    ).filter(
        models.Q(
            publish_start__isnull=True
        ) | models.Q(
            publish_start__lte=now
        ),
        models.Q(
            publish_end__isnull=True
        ) | models.Q(
            publish_end__gte=now
        ),
    )


# ============================================================
# SCHEDULED FILTER
# ============================================================

def filter_scheduled(queryset):
    """
    Return currently live ScheduledMixin records.
    """

    now = timezone.now()

    return queryset.filter(
        is_active=True,
        start_datetime__lte=now,
        end_datetime__gte=now,
    )


# ============================================================
# SERIALIZERS
# ============================================================

def serialize_banner(request, banner):
    return {
        "id": banner.id,
        "title": banner.title or "",
        "text": banner.text or "",
        "link": banner.link or "",
        "image": build_media_url(request, banner.image),
        "display_order": banner.display_order,
    }


def serialize_gif(request, gif):
    return {
        "id": gif.id,
        "title": gif.title or "",
        "description": gif.description or "",
        "media_file": build_media_url(
            request,
            gif.media_file,
        ),
        "link": gif.link or "",
        "display_order": gif.display_order,
    }



def serialize_flash_sale(request, flash_sale):
    return {
        "id": flash_sale.id,
        "title": flash_sale.title or "",
        "description": flash_sale.description or "",
        "image": build_media_url(
            request,
            flash_sale.image,
        ),
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



def serialize_affiliate_banner(request, banner):
    return {
        "id": banner.id,
        "title": banner.title or "",
        "image": build_media_url(
            request,
            banner.image,
        ),
        "affiliate_url": banner.affiliate_url or "",
        "display_order": banner.display_order,
    }


def serialize_event(request, event):
    return {
        "id": event.id,
        "name": event.name or "",
        "description": event.description or "",
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
        "image": build_media_url(
            request,
            event.image,
        ),
        "registration_link": event.registration_link or "",
    }



# ============================================================
# DATE HELPER
# ============================================================

def _parse_date_param(raw_value, param_name):
    """
    Convert YYYY-MM-DD into a datetime object.
    """

    if not raw_value:
        return None

    try:
        parsed = datetime.strptime(
            raw_value,
            "%Y-%m-%d",
        )

    except ValueError as exc:
        raise ValueError(
            f'Invalid "{param_name}" date: {raw_value}. '
            "Use YYYY-MM-DD"
        ) from exc

    return (
        timezone.make_aware(parsed)
        if timezone.is_aware(timezone.now())
        else parsed
    )


# ============================================================
# PROXY CONFIGURATION
# ============================================================

API_TOKEN = getattr(
    settings,
    "API_TOKEN",
    "",
)

API_BASE = getattr(
    settings,
    "API_BASE",
    "http://127.0.0.1:8001",
)


# ============================================================
# INTERNAL PROXY FORWARDER
# ============================================================

def _forward_request(endpoint, request):
    """
    Forward a public proxy request to the protected API.
    """

    url = f"{API_BASE}{endpoint}"

    params = request.GET.dict()

    try:
        response = requests.get(
            url,
            params=params,
            headers={
                "Authorization": f"Token {API_TOKEN}",
            },
            timeout=10,
        )

    except requests.exceptions.Timeout:
        return _cors_json_response(
            {
                "status": "error",
                "message": (
                    "The backend API request timed out."
                ),
            },
            status=504,
        )

    except requests.exceptions.ConnectionError:
        return _cors_json_response(
            {
                "status": "error",
                "message": (
                    "Could not connect to the backend API."
                ),
            },
            status=502,
        )

    except requests.exceptions.RequestException as exc:
        return _cors_json_response(
            {
                "status": "error",
                "message": (
                    "An error occurred while contacting "
                    "the backend API."
                ),
                "details": str(exc),
            },
            status=502,
        )

    try:
        data = response.json()

    except ValueError:
        data = {
            "status": "error",
            "message": (
                "Backend API returned an invalid "
                "JSON response."
            ),
        }

    return _cors_json_response(
        data,
        status=response.status_code,
    )


# ============================================================
# PUBLIC PROXY
# ============================================================

@csrf_exempt
def proxy_banner_api(request, slug):
    """
    GET /proxy/banner/<slug>/
    """

    if request.method == "OPTIONS":
        return _cors_json_response({}, status=200)

    if request.method != "GET":
        return _cors_json_response(
            {
                "status": "error",
                "message": "Method not allowed.",
            },
            status=405,
        )

    return _forward_request(
        f"/api/banner/{slug}/",
        request,
    )


@api_view(["GET", "OPTIONS"])
@authentication_classes([])
@permission_classes([AllowAny])
def proxy_events_api(request, slug):
    """
    GET /proxy/events/<slug>/
    """

    if request.method == "OPTIONS":
        return _cors_json_response({}, status=200)

    return _forward_request(
        f"/api/events/{slug}/",
        request,
    )


@api_view(["GET", "OPTIONS"])
@authentication_classes([])
@permission_classes([AllowAny])
def proxy_combined_api(request, slug):
    """
    GET /proxy/combined/<slug>/
    """

    if request.method == "OPTIONS":
        return _cors_json_response({}, status=200)

    return _forward_request(
        f"/api/combined/{slug}/",
        request,
    )


@api_view(["GET", "OPTIONS"])
@authentication_classes([])
@permission_classes([AllowAny])
def proxy_entities_api(request):
    """
    GET /proxy/entities/
    """

    if request.method == "OPTIONS":
        return _cors_json_response({}, status=200)

    return _forward_request(
        "/api/entities/",
        request,
    )


# ============================================================
# PROTECTED BANNER API
# ============================================================

@api_view(["GET", "OPTIONS"])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def get_banner_api(request, slug):
    """
    GET /api/banner/<slug>/
    """

    if request.method == "OPTIONS":
        return _cors_json_response({}, status=200)

    try:
        entity = Entity.objects.get(
            slug=slug,
            is_active=True,
        )

    except Entity.DoesNotExist:
        return _cors_json_response(
            {
                "status": "error",
                "message": (
                    f"Entity '{slug}' not found or inactive"
                ),
            },
            status=404,
        )

    banners = filter_publishable(
        entity.banners.all()
    ).order_by(
        "display_order",
        "-created_at",
    )

    return _cors_json_response(
        {
            "status": "success",
            "entity": entity.name,
            "slug": entity.slug,
            "url": entity.url,
            "banners": [
                serialize_banner(request, banner)
                for banner in banners
            ],
        },
        status=200,
    )


# ============================================================
# PROTECTED EVENTS API
# ============================================================

@api_view(["GET", "OPTIONS"])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def get_events_api(request, slug):
    """
    GET /api/events/<slug>/
    """

    if request.method == "OPTIONS":
        return _cors_json_response({}, status=200)

    try:
        entity = Entity.objects.get(
            slug=slug,
            is_active=True,
        )

    except Entity.DoesNotExist:
        return _cors_json_response(
            {
                "status": "error",
                "message": (
                    f"Entity '{slug}' not found or inactive"
                ),
            },
            status=404,
        )

    from_date = request.GET.get("from")
    to_date = request.GET.get("to")

    try:
        from_dt = (
            _parse_date_param(
                from_date,
                "from",
            )
            if from_date
            else None
        )

        to_dt = (
            _parse_date_param(
                to_date,
                "to",
            )
            if to_date
            else None
        )

    except ValueError as exc:
        return _cors_json_response(
            {
                "status": "error",
                "message": str(exc),
            },
            status=400,
        )

    if from_dt and to_dt and from_dt > to_dt:
        return _cors_json_response(
            {
                "status": "error",
                "message": (
                    '"from" date cannot be after '
                    '"to" date'
                ),
            },
            status=400,
        )

    events = filter_publishable(
        entity.events.all()
    ).order_by(
        "event_date"
    )

    if from_dt:
        events = events.filter(
            event_date__gte=from_dt
        )

    if to_dt:
        to_dt_end = to_dt.replace(
            hour=23,
            minute=59,
            second=59,
            microsecond=999999,
        )

        events = events.filter(
            event_date__lte=to_dt_end
        )

    return _cors_json_response(
        {
            "status": "success",
            "entity": entity.name,
            "slug": entity.slug,
            "url": entity.url,
            "upcoming_events": [
                serialize_event(request, event)
                for event in events
            ],
        },
        status=200,
    )


# ============================================================
# PROTECTED COMBINED API
# ============================================================

@api_view(["GET", "OPTIONS"])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def get_combined_api(request, slug):
    """
    GET /api/combined/<slug>/

    Returns the complete homepage payload.
    """

    if request.method == "OPTIONS":
        return _cors_json_response({}, status=200)

    # --------------------------------------------------------
    # FIND ENTITY
    # --------------------------------------------------------

    try:
        entity = Entity.objects.get(
            slug=slug,
            is_active=True,
        )

    except Entity.DoesNotExist:
        return _cors_json_response(
            {
                "status": "error",
                "message": (
                    f"Entity '{slug}' not found or inactive"
                ),
            },
            status=404,
        )

    # --------------------------------------------------------
    # BANNERS
    # --------------------------------------------------------

    banners = filter_publishable(
        entity.banners.all()
    ).order_by(
        "display_order",
        "-created_at",
    )

    # --------------------------------------------------------
    # GIFS
    # --------------------------------------------------------

    gifs = filter_publishable(
        entity.gifs.all()
    ).order_by(
        "display_order",
        "-created_at",
    )

   

    # --------------------------------------------------------
    # FLASH SALES
    # --------------------------------------------------------

    flash_sales = entity.flash_sales.filter(
    is_active=True,
    end_datetime__gte=timezone.now(),
).order_by(
    "display_order",
    "start_datetime",
    "-created_at",
)

    # --------------------------------------------------------
    # AFFILIATE BANNERS
    # --------------------------------------------------------

    affiliate_banners = filter_publishable(
        entity.affiliate_banners.all()
    ).order_by(
        "display_order",
        "-created_at",
    )

    # --------------------------------------------------------
    # EVENTS
    # --------------------------------------------------------

    events = filter_publishable(
        entity.events.all()
    ).order_by(
        "event_date",
    )

    # --------------------------------------------------------
    # EVENT DATE FILTERS
    # --------------------------------------------------------

    from_date = request.GET.get("from")
    to_date = request.GET.get("to")

    try:
        from_dt = (
            _parse_date_param(
                from_date,
                "from",
            )
            if from_date
            else None
        )

        to_dt = (
            _parse_date_param(
                to_date,
                "to",
            )
            if to_date
            else None
        )

    except ValueError as exc:
        return _cors_json_response(
            {
                "status": "error",
                "message": str(exc),
            },
            status=400,
        )

    if from_dt and to_dt and from_dt > to_dt:
        return _cors_json_response(
            {
                "status": "error",
                "message": (
                    '"from" date cannot be after '
                    '"to" date'
                ),
            },
            status=400,
        )

    if from_dt:
        events = events.filter(
            event_date__gte=from_dt
        )

    if to_dt:
        to_dt_end = to_dt.replace(
            hour=23,
            minute=59,
            second=59,
            microsecond=999999,
        )

        events = events.filter(
            event_date__lte=to_dt_end
        )
    # --------------------------------------------------------
    # TODAY DEALS
    # --------------------------------------------------------

    today_deals = filter_scheduled(
        entity.today_deals.all()
    ).order_by(
        "display_order",
        "-created_at",
    )

    today_deals_list = []

    for deal in today_deals:
        today_deals_list.append({
            "id": deal.id,
            "title": deal.title or "",
            "subtitle": deal.subtitle or "",
            "image": build_media_url(request, deal.image),
            "product_id": deal.product.id if deal.product else None,
            "display_order": deal.display_order,
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
        })

    # --------------------------------------------------------
    # RESPONSE
    # --------------------------------------------------------

    return _cors_json_response(
        {
            "status": "success",
            "entity": entity.name,
            "slug": entity.slug,
            "url": entity.url,

            "banners": [
                serialize_banner(request, item)
                for item in banners
            ],

            "gifs": [
                serialize_gif(request, item)
                for item in gifs
            ],

           
            "flash_sales": [
                serialize_flash_sale(
                    request,
                    item,
                )
                for item in flash_sales
            ],

            "affiliate_banners": [
                serialize_affiliate_banner(
                    request,
                    item,
                )
                for item in affiliate_banners
            ],

            # "featured_products": [
            #     serialize_featured_product(item)
            #     for item in featured_products
            # ],

            "upcoming_events": [
                serialize_event(
                    request,
                    item,
                )
                for item in events
            ],

            "today_deals": today_deals_list,
        },
        status=200,
    )




# ============================================================
# PROXY PRODUCT API
# ============================================================

@api_view(["GET", "OPTIONS"])
@authentication_classes([])
@permission_classes([AllowAny])
def proxy_product_api(request, product_id):
    """
    GET /proxy/product/<product_id>/
    Public proxy for product details.
    """
    
    if request.method == "OPTIONS":
        return _cors_json_response({}, status=200)
    
    return _forward_request(
        f"/api/product/{product_id}/",
        request,
    )
# ============================================================
# PRODUCT API
# ============================================================

@api_view(["GET", "OPTIONS"])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def get_product_api(request, product_id):
    """
    GET /api/product/<product_id>/
    Returns a single product.
    """
    
    if request.method == "OPTIONS":
        return _cors_json_response({}, status=200)
    
    try:
        product = Product.objects.get(id=product_id, is_active=True)
    except Product.DoesNotExist:
        return _cors_json_response(
            {"status": "error", "message": "Product not found"},
            status=404
        )
    
    return _cors_json_response({
        "id": product.id,
        "name": product.name,
        "slug": product.slug,
        "price": str(product.price) if product.price else "",
        "description": product.description or "",
        "image": build_media_url(request, product.image),
        "is_active": product.is_active,
    }, status=200)
# ============================================================
# ENTITIES API
# ============================================================

@api_view(["GET", "OPTIONS"])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def get_entities_api(request):
    """
    GET /api/entities/
    """

    if request.method == "OPTIONS":
        return _cors_json_response({}, status=200)

    active_entities = Entity.objects.filter(
        is_active=True
    ).order_by(
        "name"
    )

    entities_data = []

    for entity in active_entities:

        active_banner_count = filter_publishable(
            entity.banners.all()
        ).count()

        active_event_count = filter_publishable(
            entity.events.all()
        ).count()

        active_gif_count = filter_publishable(
            entity.gifs.all()
        ).count()

        

        active_flash_sale_count = filter_scheduled(
            entity.flash_sales.all()
        ).count()

        active_affiliate_banner_count = (
            filter_publishable(
                entity.affiliate_banners.all()
            ).count()
        )

        active_featured_product_count = (
            filter_publishable(
                entity.featured_products.all()
            ).count()
        )

        

        entities_data.append(
            {
                "id": entity.id,
                "name": entity.name,
                "slug": entity.slug,
                "url": entity.url,
                "is_active": entity.is_active,

                "banner_count": active_banner_count,
                "event_count": active_event_count,
                "gif_count": active_gif_count,
                
                "flash_sale_count": (
                    active_flash_sale_count
                ),
                "affiliate_banner_count": (
                    active_affiliate_banner_count
                ),
                "featured_product_count": (
                    active_featured_product_count
                ),
               
            }
        )

    return _cors_json_response(
        {
            "status": "success",
            "count": len(entities_data),
            "entities": entities_data,
        },
        status=200,
    )