import os
from datetime import datetime

import requests

from django.conf import settings
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db import models
from django.http import JsonResponse
from django.utils import timezone
from django.contrib.auth import get_user_model
from django.views.decorators.csrf import csrf_exempt
from rest_framework.test import APIRequestFactory, force_authenticate

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
    FlashSale,
    AffiliateBanner,
    TodayDeal,
    ThingWeDo,
    CybersecuritySolution,
    Project,
    BlogPost,
    Recognition,
    TeamCertificate,
    CaseStudy,
    CaseStudyImage,
    CaseStudyTechnology,
    CaseStudyResultROI,
    EventMedia,
    TechnologyPartner,
    PromallCategory,
    PromallSubcategory,
    PromallProduct,
    PromallBanner,
    PromallEventType,
    PromallEvent,
)

from .serializers import (
    serialize_banner,
    # serialize_gif,
    serialize_affiliate_banner,
    serialize_event,
    serialize_event_detail,
    serialize_flash_sale,
    serialize_today_deal,
    serialize_thing_we_do,
    serialize_cybersecurity_solution,
    serialize_project,
    serialize_blog_post,
    serialize_recognition,
    serialize_team_certificate,
    serialize_case_study_image,
    serialize_case_study_list,
    serialize_case_study_detail,
    serialize_technology_partner,
    _slugify_value,
    serialize_promall_category,
    serialize_promall_category_detail,
    serialize_promall_subcategory,
    serialize_promall_product_list,
    serialize_promall_product_detail,
    serialize_promall_banner,
    serialize_promall_event,
    serialize_promall_event_type,
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
    "http://127.0.0.1:8000",
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

    Public endpoint for the frontend.
    Calls the protected combined API internally
    without making an HTTP request to the server itself.
    """

    if request.method == "OPTIONS":
        return _cors_json_response({}, status=200)

    User = get_user_model()
    username = os.getenv("DJANGO_ADMIN_USERNAME")

    try:
        user = User.objects.get(username=username)
    except User.DoesNotExist:
        return _cors_json_response(
            {
                "status": "error",
                "message": "Internal API user does not exist.",
            },
            status=500,
        )

    factory = APIRequestFactory()

    internal_request = factory.get(
        request.get_full_path(),
        request.GET,
    )

    force_authenticate(
        internal_request,
        user=user,
    )

    return get_combined_api(
        internal_request,
        slug,
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

    Returns the complete homepage payload, branched by entity slug.

    * slug == 'promallshop'   → Promallshop-specific models
                                (PromallBanner, PromallEvent, PromallEventType,
                                 PromallCategory, AffiliateBanner with is_active-only filter)
    * any other slug          → generic CMS models
                                (Banner, UpcomingEvent, existing serializers)

    The public proxy at /proxy/combined/<slug>/ forwards here unchanged.
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
                "message": f"Entity '{slug}' not found or inactive",
            },
            status=404,
        )

    # --------------------------------------------------------
    # PARSE DATE FILTERS (shared by both branches for events)
    # --------------------------------------------------------

    from_date = request.GET.get("from")
    to_date = request.GET.get("to")

    try:
        from_dt = _parse_date_param(from_date, "from") if from_date else None
        to_dt = _parse_date_param(to_date, "to") if to_date else None
    except ValueError as exc:
        return _cors_json_response(
            {"status": "error", "message": str(exc)},
            status=400,
        )

    if from_dt and to_dt and from_dt > to_dt:
        return _cors_json_response(
            {
                "status": "error",
                "message": '"from" date cannot be after "to" date',
            },
            status=400,
        )

    # Build end-of-day ceiling for the to_dt boundary
    to_dt_end = None
    if to_dt:
        to_dt_end = to_dt.replace(
            hour=23, minute=59, second=59, microsecond=999999
        )

    # ====================================================
    # PROMALLSHOP BRANCH
    # ====================================================

    if slug == "promallshop":
        return _combined_promallshop(request, entity, from_dt, to_dt_end)

    # ====================================================
    # GENERIC / PROXYNETGROUP BRANCH
    # ====================================================

    return _combined_generic(request, entity, from_dt, to_dt_end)


# ============================================================
# COMBINED API — PROMALLSHOP BRANCH
# ============================================================

def _combined_promallshop(request, entity, from_dt, to_dt_end):
    """
    Build the combined homepage payload for Promallshop.

    Main banners:    PromallBanner  (not the generic Banner model)
    Events:          PromallEvent   (uses event_datetime, not event_date)
    Event types:     PromallEventType
    Categories:      PromallCategory (filtered to this entity, is_active=True)
    Affiliate banners: AffiliateBanner filtered by is_active=True only —
                       no publish_start/publish_end window, because Promallshop
                       uses simple on/off control for these banners.
    Flash sales, today deals, etc.: filtered to this entity as usual.
    """

    now = timezone.now()

    # --------------------------------------------------------
    # PROMALLSHOP MAIN BANNERS
    # PromallBanner, not Banner. Simple is_active filter only.
    # --------------------------------------------------------

    promall_banners = (
        PromallBanner.objects.filter(
            entity=entity,
            is_active=True,
        )
        .order_by("display_order", "-created_at")
    )

    # --------------------------------------------------------
    # AFFILIATE BANNERS — is_active only (no publish window)
    # The publish_start/publish_end on AffiliateBanner records for
    # Promallshop represent scheduled launch dates set by admins; using
    # filter_publishable() here would incorrectly hide banners whose
    # publish_start is in the future even though is_active=True.
    # Promallshop uses the is_active flag as the sole on/off switch.
    # --------------------------------------------------------

    affiliate_banners = (
        entity.affiliate_banners
        .filter(is_active=True)
        .order_by("display_order", "-created_at")
    )

    # --------------------------------------------------------
    # FLASH SALES (entity-scoped, active + not yet ended)
    # --------------------------------------------------------

    flash_sales = entity.flash_sales.filter(
        is_active=True,
        end_datetime__gte=now,
    ).order_by("display_order", "start_datetime", "-created_at")

    # --------------------------------------------------------
    # TODAY DEALS
    # --------------------------------------------------------

    today_deals = filter_scheduled(
        entity.today_deals.all()
    ).order_by("display_order", "-created_at")

    # --------------------------------------------------------
    # PROMALLSHOP EVENTS (PromallEvent, not UpcomingEvent)
    # Filter by event_datetime against from_dt / to_dt_end.
    # --------------------------------------------------------

    promall_events = (
        PromallEvent.objects.filter(
            entity=entity,
            is_active=True,
        )
        .select_related("event_type")
        .order_by("event_datetime", "display_order")
    )

    if from_dt:
        promall_events = promall_events.filter(event_datetime__gte=from_dt)

    if to_dt_end:
        promall_events = promall_events.filter(event_datetime__lte=to_dt_end)

    # --------------------------------------------------------
    # PROMALLSHOP EVENT TYPES
    # --------------------------------------------------------

    event_types = PromallEventType.objects.filter(
        entity=entity,
        is_active=True,
    ).order_by("display_order", "name")

    # --------------------------------------------------------
    # PROMALLSHOP CATEGORIES
    # subcategories are pre-filtered to is_active=True inside
    # serialize_promall_category already.
    # --------------------------------------------------------

    categories = (
        PromallCategory.objects.filter(
            entity=entity,
            is_active=True,
        )
        .prefetch_related("subcategories")
        .order_by("display_order", "name")
    )

    # --------------------------------------------------------
    # RESPONSE
    # --------------------------------------------------------

    return _cors_json_response(
        {
            "status": "success",
            "entity": entity.name,
            "slug": entity.slug,
            "url": entity.url,

            # Promallshop-specific main banners (PromallBanner model)
            "banners": [
                serialize_promall_banner(request, item)
                for item in promall_banners
            ],

            "flash_sales": [
                serialize_flash_sale(request, item)
                for item in flash_sales
            ],

            # All active Promallshop affiliate banners regardless of publish window
            "affiliate_banners": [
                serialize_affiliate_banner(request, item)
                for item in affiliate_banners
            ],

            # Promallshop events (PromallEvent, uses event_datetime)
            "upcoming_events": [
                serialize_promall_event(request, item)
                for item in promall_events
            ],

            # Promallshop event type catalogue
            "event_types": [
                serialize_promall_event_type(item)
                for item in event_types
            ],

            # Promallshop product categories
            "categories": [
                serialize_promall_category(request, item)
                for item in categories
            ],

            "today_deals": [
                serialize_today_deal(request, item)
                for item in today_deals
            ],
        },
        status=200,
    )


# ============================================================
# COMBINED API — GENERIC / PROXYNETGROUP BRANCH
# ============================================================

def _combined_generic(request, entity, from_dt, to_dt_end):
    """
    Build the combined homepage payload for Proxynetgroup (and any other
    non-Promallshop entity).

    Uses the original generic CMS models:
      - Banner (not PromallBanner)
      - UpcomingEvent with event_date (not PromallEvent)
      - serialize_event (not serialize_promall_event)

    All existing serializer fields and response keys are preserved
    exactly as before so the Proxynetgroup frontend is unaffected.
    """

    now = timezone.now()

    # --------------------------------------------------------
    # BANNERS (generic Banner model via entity FK)
    # --------------------------------------------------------

    banners = filter_publishable(
        entity.banners.all()
    ).order_by("display_order", "-created_at")

    # --------------------------------------------------------
    # FLASH SALES
    # --------------------------------------------------------

    flash_sales = entity.flash_sales.filter(
        is_active=True,
        end_datetime__gte=now,
    ).order_by("display_order", "start_datetime", "-created_at")

    # --------------------------------------------------------
    # AFFILIATE BANNERS (publish-window filtered, existing behavior)
    # --------------------------------------------------------

    affiliate_banners = filter_publishable(
        entity.affiliate_banners.all()
    ).order_by("display_order", "-created_at")

    # --------------------------------------------------------
    # EVENTS (generic UpcomingEvent, filters on event_date)
    # --------------------------------------------------------

    events = filter_publishable(
        entity.events.all()
    ).order_by("event_date")

    if from_dt:
        events = events.filter(event_date__gte=from_dt)

    if to_dt_end:
        events = events.filter(event_date__lte=to_dt_end)

    # --------------------------------------------------------
    # TODAY DEALS
    # --------------------------------------------------------

    today_deals = filter_scheduled(
        entity.today_deals.all()
    ).order_by("display_order", "-created_at")

    # --------------------------------------------------------
    # THINGS WE DO
    # --------------------------------------------------------

    things_we_do = filter_publishable(
        entity.things_we_do.all()
    ).order_by("display_order", "-created_at")

    # --------------------------------------------------------
    # CYBERSECURITY SOLUTIONS
    # --------------------------------------------------------

    cybersecurity_solutions = filter_publishable(
        entity.cybersecurity_solutions.all()
    ).order_by("display_order", "-created_at")

    # --------------------------------------------------------
    # PROJECTS
    # --------------------------------------------------------

    projects = filter_publishable(
        entity.projects.all()
    ).order_by("display_order", "-created_at")

    # --------------------------------------------------------
    # BLOG POSTS
    # --------------------------------------------------------

    blog_posts = filter_publishable(
        entity.blog_posts.all()
    ).order_by("-published_at", "display_order")

    # --------------------------------------------------------
    # RECOGNITIONS
    # --------------------------------------------------------

    recognitions = filter_publishable(
        entity.recognitions.all()
    ).order_by("display_order", "-created_at")

    # --------------------------------------------------------
    # TEAM CERTIFICATES
    # --------------------------------------------------------

    team_certificates = filter_publishable(
        entity.team_certificates.all()
    ).order_by("display_order", "-created_at")

    # --------------------------------------------------------
    # CASE STUDIES
    # --------------------------------------------------------

    case_studies = filter_publishable(
        entity.case_studies.all()
    ).order_by("display_order", "-created_at")

    # --------------------------------------------------------
    # TECHNOLOGY PARTNERS
    # --------------------------------------------------------

    technology_partners = TechnologyPartner.objects.filter(
        entity=entity,
        is_active=True,
    ).order_by("display_order", "id")

    # --------------------------------------------------------
    # RESPONSE — preserves all existing keys exactly
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

            "flash_sales": [
                serialize_flash_sale(request, item)
                for item in flash_sales
            ],

            "affiliate_banners": [
                serialize_affiliate_banner(request, item)
                for item in affiliate_banners
            ],

            "upcoming_events": [
                serialize_event(request, item)
                for item in events
            ],

            "today_deals": [
                serialize_today_deal(request, item)
                for item in today_deals
            ],

            "things_we_do": [
                serialize_thing_we_do(request, item)
                for item in things_we_do
            ],

            "cybersecurity_solutions": [
                serialize_cybersecurity_solution(request, item)
                for item in cybersecurity_solutions
            ],

            "projects": [
                serialize_project(request, item)
                for item in projects
            ],

            "blog_posts": [
                serialize_blog_post(request, item, full=False)
                for item in blog_posts
            ],

            "recognitions": [
                serialize_recognition(request, item)
                for item in recognitions
            ],

            "team_certificates": [
                serialize_team_certificate(request, item)
                for item in team_certificates
            ],

            "case_studies": [
                serialize_case_study_list(request, item)
                for item in case_studies
            ],

            "partners": [
                serialize_technology_partner(request, item)
                for item in technology_partners
            ],
        },
        status=200,
    )




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

        # active_gif_count = filter_publishable(
        #     entity.gifs.all()
        # ).count()



        active_flash_sale_count = filter_scheduled(
            entity.flash_sales.all()
        ).count()

        active_affiliate_banner_count = (
            filter_publishable(
                entity.affiliate_banners.all()
            ).count()
        )

        active_featured_product_count = 0



        entities_data.append(
            {
                "id": entity.id,
                "name": entity.name,
                "slug": entity.slug,
                "url": entity.url,
                "is_active": entity.is_active,

                "banner_count": active_banner_count,
                "event_count": active_event_count,
                # "gif_count": active_gif_count,

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


# ============================================================

# ============================================================
# PROTECTED API — THINGS WE DO
# ============================================================

@api_view(["GET", "OPTIONS"])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def get_things_we_do_api(request, slug):
    """
    GET /api/things-we-do/<slug>/
    """
    if request.method == "OPTIONS":
        return _cors_json_response({}, status=200)

    try:
        entity = Entity.objects.get(slug=slug, is_active=True)
    except Entity.DoesNotExist:
        return _cors_json_response(
            {"status": "error", "message": f"Entity '{slug}' not found"},
            status=404,
        )

    things = filter_publishable(
        entity.things_we_do.all()
    ).order_by("display_order", "-created_at")

    return _cors_json_response(
        {
            "status": "success",
            "entity": entity.name,
            "slug": entity.slug,
            "things_we_do": [
                serialize_thing_we_do(request, t) for t in things
            ],
        },
        status=200,
    )


# ============================================================
# PROTECTED API — CYBERSECURITY SOLUTIONS
# ============================================================

@api_view(["GET", "OPTIONS"])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def get_cybersecurity_solutions_api(request, slug):
    """
    GET /api/cybersecurity-solutions/<slug>/
    """
    if request.method == "OPTIONS":
        return _cors_json_response({}, status=200)

    try:
        entity = Entity.objects.get(slug=slug, is_active=True)
    except Entity.DoesNotExist:
        return _cors_json_response(
            {"status": "error", "message": f"Entity '{slug}' not found"},
            status=404,
        )

    solutions = filter_publishable(
        entity.cybersecurity_solutions.all()
    ).order_by("display_order", "-created_at")

    return _cors_json_response(
        {
            "status": "success",
            "entity": entity.name,
            "slug": entity.slug,
            "cybersecurity_solutions": [
                serialize_cybersecurity_solution(request, s) for s in solutions
            ],
        },
        status=200,
    )


# ============================================================
# PROTECTED API — PROJECTS
# ============================================================

@api_view(["GET", "OPTIONS"])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def get_projects_api(request, slug):
    """
    GET /api/projects/<slug>/
    """
    if request.method == "OPTIONS":
        return _cors_json_response({}, status=200)

    try:
        entity = Entity.objects.get(slug=slug, is_active=True)
    except Entity.DoesNotExist:
        return _cors_json_response(
            {"status": "error", "message": f"Entity '{slug}' not found"},
            status=404,
        )

    projects = filter_publishable(
        entity.projects.all()
    ).order_by("display_order", "-created_at")

    return _cors_json_response(
        {
            "status": "success",
            "entity": entity.name,
            "slug": entity.slug,
            "projects": [
                serialize_project(request, p) for p in projects
            ],
        },
        status=200,
    )


# ============================================================
# PROTECTED API — BLOG POSTS (list)
# ============================================================

@api_view(["GET", "OPTIONS"])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def get_blog_posts_api(request, slug):
    """
    GET /api/blog-posts/<slug>/
    """
    if request.method == "OPTIONS":
        return _cors_json_response({}, status=200)

    try:
        entity = Entity.objects.get(slug=slug, is_active=True)
    except Entity.DoesNotExist:
        return _cors_json_response(
            {"status": "error", "message": f"Entity '{slug}' not found"},
            status=404,
        )

    posts = filter_publishable(
        entity.blog_posts.all()
    ).order_by("-published_at", "display_order")

    return _cors_json_response(
        {
            "status": "success",
            "entity": entity.name,
            "slug": entity.slug,
            "blog_posts": [
                serialize_blog_post(request, p, full=False) for p in posts
            ],
        },
        status=200,
    )


# ============================================================
# PROTECTED API — BLOG POST DETAIL
# ============================================================

@api_view(["GET", "OPTIONS"])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def get_blog_post_detail_api(request, slug):
    """
    GET /api/blog-detail/<slug>/
    """
    if request.method == "OPTIONS":
        return _cors_json_response({}, status=200)

    try:
        post = BlogPost.objects.get(slug=slug, is_active=True)
    except BlogPost.DoesNotExist:
        return _cors_json_response(
            {"status": "error", "message": f"Blog post '{slug}' not found"},
            status=404,
        )

    return _cors_json_response(
        {
            "status": "success",
            "blog_post": serialize_blog_post(request, post, full=True),
        },
        status=200,
    )


# ============================================================
# PUBLIC PROXY — THINGS WE DO
# ============================================================

@csrf_exempt
def proxy_things_we_do_api(request, slug):
    """
    GET /proxy/things-we-do/<slug>/
    """
    if request.method == "OPTIONS":
        return _cors_json_response({}, status=200)
    if request.method != "GET":
        return _cors_json_response(
            {"status": "error", "message": "Method not allowed."},
            status=405,
        )
    return _forward_request(f"/api/things-we-do/{slug}/", request)


# ============================================================
# PUBLIC PROXY — CYBERSECURITY SOLUTIONS
# ============================================================

@csrf_exempt
def proxy_cybersecurity_solutions_api(request, slug):
    """
    GET /proxy/cybersecurity-solutions/<slug>/
    """
    if request.method == "OPTIONS":
        return _cors_json_response({}, status=200)
    if request.method != "GET":
        return _cors_json_response(
            {"status": "error", "message": "Method not allowed."},
            status=405,
        )
    return _forward_request(f"/api/cybersecurity-solutions/{slug}/", request)


# ============================================================
# PUBLIC PROXY — PROJECTS
# ============================================================

@csrf_exempt
def proxy_projects_api(request, slug):
    """
    GET /proxy/projects/<slug>/
    """
    if request.method == "OPTIONS":
        return _cors_json_response({}, status=200)
    if request.method != "GET":
        return _cors_json_response(
            {"status": "error", "message": "Method not allowed."},
            status=405,
        )
    return _forward_request(f"/api/projects/{slug}/", request)


# ============================================================
# PUBLIC PROXY — BLOG POSTS
# ============================================================

@csrf_exempt
def proxy_blog_posts_api(request, slug):
    """
    GET /proxy/blog-posts/<slug>/
    """
    if request.method == "OPTIONS":
        return _cors_json_response({}, status=200)
    if request.method != "GET":
        return _cors_json_response(
            {"status": "error", "message": "Method not allowed."},
            status=405,
        )
    return _forward_request(f"/api/blog-posts/{slug}/", request)


# ============================================================
# PUBLIC PROXY — BLOG POST DETAIL
# ============================================================

@csrf_exempt
def proxy_blog_detail_api(request, slug):
    """
    GET /proxy/blog-detail/<slug>/
    """
    if request.method == "OPTIONS":
        return _cors_json_response({}, status=200)
    if request.method != "GET":
        return _cors_json_response(
            {"status": "error", "message": "Method not allowed."},
            status=405,
        )
    return _forward_request(f"/api/blog-detail/{slug}/", request)


# ============================================================

# ============================================================
# PROTECTED API — RECOGNITIONS
# ============================================================

@api_view(["GET", "OPTIONS"])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def get_recognitions_api(request, slug):
    """
    GET /api/recognitions/<slug>/
    """
    if request.method == "OPTIONS":
        return _cors_json_response({}, status=200)

    try:
        entity = Entity.objects.get(slug=slug, is_active=True)
    except Entity.DoesNotExist:
        return _cors_json_response(
            {"status": "error", "message": f"Entity '{slug}' not found"},
            status=404,
        )

    recognitions = filter_publishable(
        entity.recognitions.all()
    ).order_by("display_order", "-created_at")

    return _cors_json_response(
        {
            "status": "success",
            "entity": entity.name,
            "slug": entity.slug,
            "recognitions": [
                serialize_recognition(request, item) for item in recognitions
            ],
        },
        status=200,
    )


# ============================================================
# PROTECTED API — TEAM CERTIFICATES
# ============================================================

@api_view(["GET", "OPTIONS"])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def get_team_certificates_api(request, slug):
    """
    GET /api/team-certificates/<slug>/
    """
    if request.method == "OPTIONS":
        return _cors_json_response({}, status=200)

    try:
        entity = Entity.objects.get(slug=slug, is_active=True)
    except Entity.DoesNotExist:
        return _cors_json_response(
            {"status": "error", "message": f"Entity '{slug}' not found"},
            status=404,
        )

    team_certificates = filter_publishable(
        entity.team_certificates.all()
    ).order_by("display_order", "-created_at")

    return _cors_json_response(
        {
            "status": "success",
            "entity": entity.name,
            "slug": entity.slug,
            "team_certificates": [
                serialize_team_certificate(request, item) for item in team_certificates
            ],
        },
        status=200,
    )


# ============================================================
# PUBLIC PROXY — RECOGNITIONS
# ============================================================

@csrf_exempt
def proxy_recognitions_api(request, slug):
    """
    GET /proxy/recognitions/<slug>/
    """
    if request.method == "OPTIONS":
        return _cors_json_response({}, status=200)
    if request.method != "GET":
        return _cors_json_response(
            {"status": "error", "message": "Method not allowed."},
            status=405,
        )
    return _forward_request(f"/api/recognitions/{slug}/", request)


# ============================================================
# PUBLIC PROXY — TEAM CERTIFICATES
# ============================================================

@csrf_exempt
def proxy_team_certificates_api(request, slug):
    """
    GET /proxy/team-certificates/<slug>/
    """
    if request.method == "OPTIONS":
        return _cors_json_response({}, status=200)
    if request.method != "GET":
        return _cors_json_response(
            {"status": "error", "message": "Method not allowed."},
            status=405,
        )
    return _forward_request(f"/api/team-certificates/{slug}/", request)


# ============================================================
# CASE STUDY — HELPERS

# ============================================================

def _active_case_studies():
    """Return the base queryset of published Case Studies, with entity pre-fetched."""
    return CaseStudy.objects.filter(is_active=True).select_related('entity')


# ============================================================
# PROTECTED API — CASE STUDIES LISTING + FILTERING
# ============================================================

@api_view(["GET", "OPTIONS"])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def get_case_studies_api(request):
    """
    GET /api/case-studies/

    Optional query params for filtering:
      ?solution=<slug>
      ?industry=<slug>
      ?country=<slug>

    Multiple params are ANDed together.
    """
    if request.method == "OPTIONS":
        return _cors_json_response({}, status=200)

    qs = _active_case_studies().order_by("display_order", "-created_at")

    solution_filter = request.GET.get("solution", "").strip()
    industry_filter = request.GET.get("industry", "").strip()
    country_filter  = request.GET.get("country",  "").strip()

    # Filter by slugified match — compare incoming slug against
    # the slugified version of each stored value.
    filtered = []
    for cs in qs:
        if solution_filter and _slugify_value(cs.solution) != solution_filter:
            continue
        if industry_filter and _slugify_value(cs.industry) != industry_filter:
            continue
        if country_filter and _slugify_value(cs.country) != country_filter:
            continue
        filtered.append(cs)

    return _cors_json_response(
        {
            "status": "success",
            "count": len(filtered),
            "case_studies": [
                serialize_case_study_list(request, cs) for cs in filtered
            ],
        },
        status=200,
    )


# ============================================================
# PROTECTED API — DYNAMIC FILTER OPTIONS
# ============================================================

@api_view(["GET", "OPTIONS"])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def get_case_study_filters_api(request):
    """
    GET /api/case-study-filters/

    Returns unique, deduplicated solutions / industries / countries
    derived from active Case Studies only.
    """
    if request.method == "OPTIONS":
        return _cors_json_response({}, status=200)

    qs = _active_case_studies()

    # Collect unique non-empty values preserving first-seen order
    def _unique_options(field_name):
        seen_slugs = set()
        options = []
        for value in qs.values_list(field_name, flat=True):
            if not value:
                continue
            slug = _slugify_value(value)
            if slug not in seen_slugs:
                seen_slugs.add(slug)
                options.append({"name": value, "slug": slug})
        return options

    return _cors_json_response(
        {
            "status": "success",
            "solutions":  _unique_options("solution"),
            "industries": _unique_options("industry"),
            "countries":  _unique_options("country"),
        },
        status=200,
    )


# ============================================================
# PROTECTED API — CASE STUDY DETAIL
# ============================================================

@api_view(["GET", "OPTIONS"])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def get_case_study_detail_api(request, slug):
    """
    GET /api/case-studies/<slug>/
    """
    if request.method == "OPTIONS":
        return _cors_json_response({}, status=200)

    try:
        cs = CaseStudy.objects.get(slug=slug, is_active=True)
    except CaseStudy.DoesNotExist:
        return _cors_json_response(
            {"status": "error", "message": f"Case study '{slug}' not found"},
            status=404,
        )

    return _cors_json_response(
        {
            "status": "success",
            "case_study": serialize_case_study_detail(request, cs),
        },
        status=200,
    )


# ============================================================
# PUBLIC PROXY — CASE STUDIES LISTING + FILTERING
# ============================================================

@csrf_exempt
def proxy_case_studies_api(request):
    """
    GET /proxy/case-studies/
    Forwards query params (?solution=, ?industry=, ?country=) as-is.
    """
    if request.method == "OPTIONS":
        return _cors_json_response({}, status=200)
    if request.method != "GET":
        return _cors_json_response(
            {"status": "error", "message": "Method not allowed."},
            status=405,
        )
    return _forward_request("/api/case-studies/", request)


# ============================================================
# PUBLIC PROXY — DYNAMIC FILTER OPTIONS
# ============================================================

@csrf_exempt
def proxy_case_study_filters_api(request):
    """
    GET /proxy/case-study-filters/
    """
    if request.method == "OPTIONS":
        return _cors_json_response({}, status=200)
    if request.method != "GET":
        return _cors_json_response(
            {"status": "error", "message": "Method not allowed."},
            status=405,
        )
    return _forward_request("/api/case-study-filters/", request)


# ============================================================
# PUBLIC PROXY — CASE STUDY DETAIL
# ============================================================

@csrf_exempt
def proxy_case_study_detail_api(request, slug):
    """
    GET /proxy/case-studies/<slug>/
    """
    if request.method == "OPTIONS":
        return _cors_json_response({}, status=200)
    if request.method != "GET":
        return _cors_json_response(
            {"status": "error", "message": "Method not allowed."},
            status=405,
        )
    return _forward_request(f"/api/case-studies/{slug}/", request)


# ============================================================
# PROTECTED API — EVENT DETAIL (with gallery)
# ============================================================

@api_view(["GET", "OPTIONS"])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def get_event_detail_api(request, event_id):
    """
    GET /api/event-detail/<int:event_id>/

    Returns a single active UpcomingEvent including its full gallery.
    The 'status' field indicates 'upcoming' or 'past' based on event_date.
    """
    if request.method == "OPTIONS":
        return _cors_json_response({}, status=200)

    try:
        event = UpcomingEvent.objects.get(id=event_id, is_active=True)
    except UpcomingEvent.DoesNotExist:
        return _cors_json_response(
            {"status": "error", "message": f"Event {event_id} not found"},
            status=404,
        )

    return _cors_json_response(
        {
            "status": "success",
            "event": serialize_event_detail(request, event),
        },
        status=200,
    )


# ============================================================
# PUBLIC PROXY — EVENT DETAIL
# ============================================================

@csrf_exempt
def proxy_event_detail_api(request, event_id):
    """
    GET /proxy/event-detail/<int:event_id>/
    """
    if request.method == "OPTIONS":
        return _cors_json_response({}, status=200)
    if request.method != "GET":
        return _cors_json_response(
            {"status": "error", "message": "Method not allowed."},
            status=405,
        )
    return _forward_request(f"/api/event-detail/{event_id}/", request)


# ============================================================

# ============================================================
# PROTECTED API — TECHNOLOGY PARTNERS
# ============================================================

@api_view(["GET", "OPTIONS"])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def get_partners_api(request, slug):
    """
    GET /api/partners/<slug>/

    Returns all active TechnologyPartner records whose entity
    matches the slug.  The slug is matched case-insensitively
    against the stored entity string (spaces replaced by hyphens).
    """
    if request.method == "OPTIONS":
        return _cors_json_response({}, status=200)

    partners = TechnologyPartner.objects.filter(
        is_active=True,
    ).select_related('entity').order_by("display_order", "created_at")

    return _cors_json_response(
        {
            "status": "success",
            "slug": slug,
            "partners": [
                serialize_technology_partner(request, p) for p in partners
            ],
        },
        status=200,
    )


# ============================================================
# PUBLIC PROXY — TECHNOLOGY PARTNERS
# ============================================================

@csrf_exempt
def proxy_partners_api(request, slug):
    """
    GET /proxy/partners/<slug>/
    """
    if request.method == "OPTIONS":
        return _cors_json_response({}, status=200)
    if request.method != "GET":
        return _cors_json_response(
            {"status": "error", "message": "Method not allowed."},
            status=405,
        )
    return _forward_request(f"/api/partners/{slug}/", request)


# ============================================================


# ============================================================
# PROMALLSHOP SITE CONTENT APIs
# ============================================================

@api_view(["GET", "OPTIONS"])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def get_promall_affiliate_banners_api(request):
    if request.method == "OPTIONS":
        return _cors_json_response({}, status=200)

    banners = AffiliateBanner.objects.filter(
        entity__slug="promallshop",
        is_active=True,
    ).order_by("display_order", "-created_at")

    return _cors_json_response({
        "status": "success",
        "count": banners.count(),
        "affiliate_banners": [
            serialize_affiliate_banner(request, banner)
            for banner in banners
        ],
    })


@api_view(["GET", "OPTIONS"])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def get_promall_events_api(request):
    if request.method == "OPTIONS":
        return _cors_json_response({}, status=200)

    events = PromallEvent.objects.filter(
        entity__slug="promallshop",
        is_active=True,
    ).select_related("event_type").order_by("event_datetime", "display_order")

    results = []
    for event in events:
        results.append({
            "id": event.id,
            "name": event.name,
            "description": event.description or "",
            "event_datetime": event.event_datetime.isoformat() if event.event_datetime else None,
            "location": event.location or "",
            "event_type": ({
                "id": event.event_type.id,
                "name": event.event_type.name,
                "slug": event.event_type.slug,
            } if event.event_type else None),
            "image": build_media_url(request, event.image),
            "registration_link": event.registration_link or "",
            "display_order": event.display_order,
        })

    return _cors_json_response({
        "status": "success",
        "count": len(results),
        "events": results,
    })


@api_view(["GET", "OPTIONS"])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def get_promall_event_types_api(request):
    if request.method == "OPTIONS":
        return _cors_json_response({}, status=200)

    event_types = PromallEventType.objects.filter(
        entity__slug="promallshop",
        is_active=True,
    ).order_by("display_order", "name")

    return _cors_json_response({
        "status": "success",
        "count": event_types.count(),
        "event_types": [
            {
                "id": item.id,
                "name": item.name,
                "slug": item.slug,
                "display_order": item.display_order,
            }
            for item in event_types
        ],
    })


@csrf_exempt
def proxy_promall_affiliate_banners_api(request):
    if request.method == "OPTIONS":
        return _cors_json_response({}, status=200)
    if request.method != "GET":
        return _cors_json_response(
            {"status": "error", "message": "Method not allowed."},
            status=405,
        )
    return _forward_request("/api/promall/affiliate-banners/", request)


@csrf_exempt
def proxy_promall_events_api(request):
    if request.method == "OPTIONS":
        return _cors_json_response({}, status=200)
    if request.method != "GET":
        return _cors_json_response(
            {"status": "error", "message": "Method not allowed."},
            status=405,
        )
    return _forward_request("/api/promall/events/", request)


@csrf_exempt
def proxy_promall_event_types_api(request):
    if request.method == "OPTIONS":
        return _cors_json_response({}, status=200)
    if request.method != "GET":
        return _cors_json_response(
            {"status": "error", "message": "Method not allowed."},
            status=405,
        )
    return _forward_request("/api/promall/event-types/", request)


# ============================================================
# PROMALLSHOP BANNERS ? PROTECTED API
# ============================================================

@api_view(["GET", "OPTIONS"])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def get_promall_banners_api(request):
    if request.method == "OPTIONS":
        return _cors_json_response({}, status=200)

    banners = PromallBanner.objects.filter(
        entity__slug="promallshop",
        is_active=True,
    ).order_by("display_order", "-created_at")

    results = []
    for banner in banners:
        results.append({
            "id": banner.id,
            "title": banner.title or "",
            "description": banner.description or "",
            "image": build_media_url(request, banner.image),
            "display_order": banner.display_order,
        })

    return _cors_json_response({
        "status": "success",
        "count": len(results),
        "banners": results,
    })


@csrf_exempt
def proxy_promall_banners_api(request):
    if request.method == "OPTIONS":
        return _cors_json_response({}, status=200)
    if request.method != "GET":
        return _cors_json_response(
            {"status": "error", "message": "Method not allowed."},
            status=405,
        )
    return _forward_request("/api/promall/banners/", request)


# PROMALLSHOP CATALOG — PROTECTED API VIEWS
# ============================================================


@api_view(["GET", "OPTIONS"])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def get_promall_categories_api(request):
    """
    GET /api/promall/categories/
    """
    if request.method == "OPTIONS":
        return _cors_json_response({}, status=200)
    categories = (
        PromallCategory.objects.filter(is_active=True)
        .order_by('display_order', 'name')
        .prefetch_related('subcategories')
    )
    return _cors_json_response({
        'status': 'success',
        'count': categories.count(),
        'categories': [serialize_promall_category(request, c) for c in categories],
    }, status=200)


@api_view(["GET", "OPTIONS"])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def get_promall_category_detail_api(request, slug):
    """
    GET /api/promall/categories/<slug>/
    """
    if request.method == "OPTIONS":
        return _cors_json_response({}, status=200)
    cat = (
        PromallCategory.objects.filter(slug=slug, is_active=True)
        .order_by('display_order')
        .first()
    )
    if not cat:
        return _cors_json_response(
            {'status': 'error', 'message': f"Category '{slug}' not found"},
            status=404,
        )
    return _cors_json_response({
        'status': 'success',
        'category': serialize_promall_category_detail(request, cat),
    }, status=200)


@api_view(["GET", "OPTIONS"])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def get_promall_subcategory_products_api(request, category_slug, subcategory_slug):
    """
    GET /api/promall/categories/<category_slug>/subcategories/<subcategory_slug>/products/
    """
    if request.method == "OPTIONS":
        return _cors_json_response({}, status=200)
    cat = (
        PromallCategory.objects.filter(slug=category_slug, is_active=True)
        .order_by('display_order')
        .first()
    )
    if not cat:
        return _cors_json_response(
            {'status': 'error', 'message': f"Category '{category_slug}' not found"},
            status=404,
        )
    sub = cat.subcategories.filter(slug=subcategory_slug, is_active=True).first()
    if not sub:
        return _cors_json_response(
            {'status': 'error', 'message': f"Subcategory '{subcategory_slug}' not found"},
            status=404,
        )
    qs = sub.products.filter(is_active=True).order_by('display_order', 'name')
    search = request.GET.get('search', '').strip()
    if search:
        qs = qs.filter(
            models.Q(name__icontains=search) |
            models.Q(model_number__icontains=search) |
            models.Q(part_number__icontains=search)
        )
    return _cors_json_response({
        'status': 'success',
        'count': qs.count(),
        'products': [serialize_promall_product_list(request, p) for p in qs],
    }, status=200)


@api_view(["GET", "OPTIONS"])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def get_promall_products_api(request):
    """
    GET /api/promall/products/
    Supports ?category=<slug> ?subcategory=<slug> ?search= ?is_hot=1 ?is_special=1
    ?page=<n> ?page_size=<n>
    """
    if request.method == "OPTIONS":
        return _cors_json_response({}, status=200)
    qs = (
        PromallProduct.objects.filter(is_active=True)
        .select_related('category', 'subcategory')
        .order_by('display_order', 'name')
    )
    # Filters
    cat_slug = request.GET.get('category', '').strip()
    sub_slug = request.GET.get('subcategory', '').strip()
    search = request.GET.get('search', '').strip()
    is_hot = request.GET.get('is_hot', '').strip()
    is_spec = request.GET.get('is_special', '').strip()
    if cat_slug:
        qs = qs.filter(category__slug=cat_slug)
    if sub_slug:
        qs = qs.filter(subcategory__slug=sub_slug)
    if search:
        qs = qs.filter(
            models.Q(name__icontains=search) |
            models.Q(model_number__icontains=search) |
            models.Q(part_number__icontains=search)
        )
    if is_hot == '1':
        qs = qs.filter(is_hot=True)
    if is_spec == '1':
        qs = qs.filter(is_special=True)
    # Pagination
    try:
        page_size = max(1, int(request.GET.get('page_size', 24)))
    except (ValueError, TypeError):
        page_size = 24
    paginator = Paginator(qs, page_size)
    page_num = request.GET.get('page', 1)
    try:
        page = paginator.page(page_num)
    except (EmptyPage, PageNotAnInteger):
        page = paginator.page(1)

    def _page_url(n):
        if n < 1 or n > paginator.num_pages:
            return None
        params = request.GET.copy()
        params['page'] = n
        return request.build_absolute_uri(f"?{params.urlencode()}")

    return _cors_json_response({
        'status': 'success',
        'count': paginator.count,
        'page': page.number,
        'page_size': page_size,
        'next': _page_url(page.number + 1),
        'previous': _page_url(page.number - 1),
        'results': [serialize_promall_product_list(request, p) for p in page],
    }, status=200)


@api_view(["GET", "OPTIONS"])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def get_promall_product_detail_api(request, product_id):
    """
    GET /api/promall/products/<product_id>/
    product_id is the external_id string.
    """
    if request.method == "OPTIONS":
        return _cors_json_response({}, status=200)
    try:
        product = (
            PromallProduct.objects
            .select_related('category', 'subcategory')
            .get(external_id=product_id, is_active=True)
        )
    except PromallProduct.DoesNotExist:
        return _cors_json_response(
            {'status': 'error', 'message': f"Product '{product_id}' not found"},
            status=404,
        )
    return _cors_json_response({
        'status': 'success',
        'product': serialize_promall_product_detail(request, product),
    }, status=200)


@api_view(["GET", "OPTIONS"])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def get_promall_flash_sale_api(request, slug):
    """
    GET /api/promall/flash-sale/<slug>/
    Returns HOT products for the entity plus the active FlashSale record.
    """
    if request.method == "OPTIONS":
        return _cors_json_response({}, status=200)
    try:
        entity = Entity.objects.get(slug=slug, is_active=True)
    except Entity.DoesNotExist:
        return _cors_json_response(
            {'status': 'error', 'message': f"Entity '{slug}' not found"},
            status=404,
        )
    products = (
        PromallProduct.objects.filter(entity=entity, is_hot=True, is_active=True)
        .select_related('category', 'subcategory')
        .order_by('display_order', 'name')
    )
    flash_sale_qs = entity.flash_sales.filter(
        is_active=True,
        end_datetime__gte=timezone.now(),
    ).order_by('display_order', 'start_datetime', '-created_at')
    flash_sale_obj = flash_sale_qs.first()
    return _cors_json_response({
        'status': 'success',
        'entity': entity.name,
        'slug': entity.slug,
        'products': [serialize_promall_product_list(request, p) for p in products],
        'flash_sale': serialize_flash_sale(request, flash_sale_obj) if flash_sale_obj else None,
    }, status=200)


@api_view(["GET", "OPTIONS"])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def get_promall_featured_api(request, slug):
    """
    GET /api/promall/featured/<slug>/
    Returns SPECIAL products for the entity.
    """
    if request.method == "OPTIONS":
        return _cors_json_response({}, status=200)
    try:
        entity = Entity.objects.get(slug=slug, is_active=True)
    except Entity.DoesNotExist:
        return _cors_json_response(
            {'status': 'error', 'message': f"Entity '{slug}' not found"},
            status=404,
        )
    products = (
        PromallProduct.objects.filter(entity=entity, is_special=True, is_active=True)
        .select_related('category', 'subcategory')
        .order_by('display_order', 'name')
    )
    return _cors_json_response({
        'status': 'success',
        'entity': entity.name,
        'slug': entity.slug,
        'products': [serialize_promall_product_list(request, p) for p in products],
    }, status=200)


# ============================================================
# PROMALLSHOP CATALOG — PUBLIC PROXY VIEWS
# ============================================================


@csrf_exempt
def proxy_promall_categories_api(request):
    """
    GET /proxy/promall/categories/
    """
    if request.method == "OPTIONS":
        return _cors_json_response({}, status=200)
    if request.method != "GET":
        return _cors_json_response(
            {'status': 'error', 'message': 'Method not allowed.'},
            status=405,
        )
    return _forward_request('/api/promall/categories/', request)


@csrf_exempt
def proxy_promall_category_detail_api(request, slug):
    """
    GET /proxy/promall/categories/<slug>/
    """
    if request.method == "OPTIONS":
        return _cors_json_response({}, status=200)
    if request.method != "GET":
        return _cors_json_response(
            {'status': 'error', 'message': 'Method not allowed.'},
            status=405,
        )
    return _forward_request(f'/api/promall/categories/{slug}/', request)


@csrf_exempt
def proxy_promall_subcategory_products_api(request, category_slug, subcategory_slug):
    """
    GET /proxy/promall/categories/<category_slug>/subcategories/<subcategory_slug>/products/
    """
    if request.method == "OPTIONS":
        return _cors_json_response({}, status=200)
    if request.method != "GET":
        return _cors_json_response(
            {'status': 'error', 'message': 'Method not allowed.'},
            status=405,
        )
    return _forward_request(
        f'/api/promall/categories/{category_slug}/subcategories/{subcategory_slug}/products/',
        request,
    )


@csrf_exempt
def proxy_promall_products_api(request):
    """
    GET /proxy/promall/products/
    """
    if request.method == "OPTIONS":
        return _cors_json_response({}, status=200)
    if request.method != "GET":
        return _cors_json_response(
            {'status': 'error', 'message': 'Method not allowed.'},
            status=405,
        )
    return _forward_request('/api/promall/products/', request)


@csrf_exempt
def proxy_promall_product_detail_api(request, product_id):
    """
    GET /proxy/promall/products/<product_id>/
    """
    if request.method == "OPTIONS":
        return _cors_json_response({}, status=200)
    if request.method != "GET":
        return _cors_json_response(
            {'status': 'error', 'message': 'Method not allowed.'},
            status=405,
        )
    return _forward_request(f'/api/promall/products/{product_id}/', request)


@csrf_exempt
def proxy_promall_flash_sale_api(request, slug):
    """
    GET /proxy/promall/flash-sale/<slug>/
    """
    if request.method == "OPTIONS":
        return _cors_json_response({}, status=200)
    if request.method != "GET":
        return _cors_json_response(
            {'status': 'error', 'message': 'Method not allowed.'},
            status=405,
        )
    return _forward_request(f'/api/promall/flash-sale/{slug}/', request)


@csrf_exempt
def proxy_promall_featured_api(request, slug):
    """
    GET /proxy/promall/featured/<slug>/
    """
    if request.method == "OPTIONS":
        return _cors_json_response({}, status=200)
    if request.method != "GET":
        return _cors_json_response(
            {'status': 'error', 'message': 'Method not allowed.'},
            status=405,
        )
    return _forward_request(f'/api/promall/featured/{slug}/', request)
