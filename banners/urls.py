from django.urls import path

from .views import (
    proxy_banner_api,
    proxy_events_api,
    proxy_combined_api,
    proxy_entities_api,
    get_product_api,
    proxy_product_api,
    get_banner_api,
    get_events_api,
    get_combined_api,
    get_entities_api,
)

app_name = "banners"

urlpatterns = [

    # ============================================================
    # PUBLIC PROXY ENDPOINTS
    # Frontend uses these.
    # Frontend does NOT send the API token.
    # ============================================================

    path(
        "proxy/banner/<slug:slug>/",
        proxy_banner_api,
        name="proxy-banner",
    ),

    path(
        "proxy/events/<slug:slug>/",
        proxy_events_api,
        name="proxy-events",
    ),

    path(
        "proxy/combined/<slug:slug>/",
        proxy_combined_api,
        name="proxy-combined",
    ),

    path(
        "proxy/entities/",
        proxy_entities_api,
        name="proxy-entities",
    ),


    # ============================================================
    # PROTECTED INTERNAL API ENDPOINTS
    # Proxy calls these using the Token.
    # ============================================================

    path(
        "api/banner/<slug:slug>/",
        get_banner_api,
        name="banner-detail",
    ),

    path(
        "api/events/<slug:slug>/",
        get_events_api,
        name="events-detail",
    ),

    path(
        "api/combined/<slug:slug>/",
        get_combined_api,
        name="combined-detail",
    ),

    path(
        "api/entities/",
        get_entities_api,
        name="entity-list",
    ),

     # Product API (protected)
    path('api/product/<int:product_id>/', get_product_api, name='get_product'),
    
    # Product Proxy (public)
    path('proxy/product/<int:product_id>/', proxy_product_api, name='proxy_product'),
]