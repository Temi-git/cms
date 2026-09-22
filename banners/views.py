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
)

from .serializers import (
    serialize_banner,
    serialize_gif,
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
        Banner.objects.filter(entities=entity)
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
        Banner.objects.filter(entities=entity)
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
                serialize_flash_sale(request, item)
                for item in flash_sales
            ],

            "affiliate_banners": [
                serialize_affiliate_banner(request, item)
                for item in affiliate_banners
            ],

            # "featured_products": [
            #     serialize_featured_product(item)
            #     for item in featured_products
            # ],

            "upcoming_events": [
                serialize_event(request, item)
                for item in events
            ],

            "today_deals": today_deals_list,

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
            Banner.objects.filter(entities=entity)
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
