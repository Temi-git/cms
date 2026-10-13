from django.urls import path

from .views import (
    proxy_banner_api,
    proxy_events_api,
    proxy_combined_api,
    proxy_entities_api,
    get_banner_api,
    get_events_api,
    get_combined_api,
    get_entities_api,
    get_things_we_do_api,
    get_cybersecurity_solutions_api,
    get_projects_api,
    get_blog_posts_api,
    get_blog_post_detail_api,
    proxy_things_we_do_api,
    proxy_cybersecurity_solutions_api,
    proxy_projects_api,
    proxy_blog_posts_api,
    proxy_blog_detail_api,
    get_recognitions_api,
    get_team_certificates_api,
    proxy_recognitions_api,
    proxy_team_certificates_api,
    get_case_studies_api,
    get_case_study_filters_api,
    get_case_study_detail_api,
    proxy_case_studies_api,
    proxy_case_study_filters_api,
    proxy_case_study_detail_api,
    get_event_detail_api,
    proxy_event_detail_api,
    get_partners_api,
    proxy_partners_api,
    get_promall_affiliate_banners_api,
    get_promall_events_api,
    get_promall_event_types_api,
    proxy_promall_affiliate_banners_api,
    proxy_promall_events_api,
    proxy_promall_event_types_api,
    get_promall_banners_api,
    proxy_promall_banners_api,
    get_promall_categories_api,
    get_promall_category_detail_api,
    get_promall_subcategory_products_api,
    get_promall_products_api,
    get_promall_product_detail_api,
    get_promall_flash_sale_api,
    get_promall_featured_api,
    proxy_promall_categories_api,
    proxy_promall_category_detail_api,
    proxy_promall_subcategory_products_api,
    proxy_promall_products_api,
    proxy_promall_product_detail_api,
    proxy_promall_flash_sale_api,
    proxy_promall_featured_api,
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

    # ============================================================
    # THINGS WE DO
    # ============================================================

    path(
        "proxy/things-we-do/<slug:slug>/",
        proxy_things_we_do_api,
        name="proxy-things-we-do",
    ),

    path(
        "api/things-we-do/<slug:slug>/",
        get_things_we_do_api,
        name="api-things-we-do",
    ),

    # ============================================================
    # CYBERSECURITY SOLUTIONS
    # ============================================================

    path(
        "proxy/cybersecurity-solutions/<slug:slug>/",
        proxy_cybersecurity_solutions_api,
        name="proxy-cybersecurity-solutions",
    ),

    path(
        "api/cybersecurity-solutions/<slug:slug>/",
        get_cybersecurity_solutions_api,
        name="api-cybersecurity-solutions",
    ),

    # ============================================================
    # PROJECTS
    # ============================================================

    path(
        "proxy/projects/<slug:slug>/",
        proxy_projects_api,
        name="proxy-projects",
    ),

    path(
        "api/projects/<slug:slug>/",
        get_projects_api,
        name="api-projects",
    ),

    # ============================================================
    # BLOG POSTS
    # ============================================================

    path(
        "proxy/blog-posts/<slug:slug>/",
        proxy_blog_posts_api,
        name="proxy-blog-posts",
    ),

    path(
        "api/blog-posts/<slug:slug>/",
        get_blog_posts_api,
        name="api-blog-posts",
    ),

    # ============================================================
    # BLOG POST DETAIL
    # ============================================================

    path(
        "proxy/blog-detail/<slug:slug>/",
        proxy_blog_detail_api,
        name="proxy-blog-detail",
    ),

    path(
        "api/blog-detail/<slug:slug>/",
        get_blog_post_detail_api,
        name="blog-detail",
    ),

    # ============================================================
    # RECOGNITIONS
    # ============================================================

    path(
        "proxy/recognitions/<slug:slug>/",
        proxy_recognitions_api,
        name="proxy-recognitions",
    ),

    path(
        "api/recognitions/<slug:slug>/",
        get_recognitions_api,
        name="api-recognitions",
    ),

    # ============================================================
    # TEAM CERTIFICATES
    # ============================================================

    path(
        "proxy/team-certificates/<slug:slug>/",
        proxy_team_certificates_api,
        name="proxy-team-certificates",
    ),

    path(
        "api/team-certificates/<slug:slug>/",
        get_team_certificates_api,
        name="api-team-certificates",
    ),

    # ============================================================
    # CASE STUDIES
    # Static routes (no slug param) placed BEFORE the slug-param
    # detail route so Django matches them first.
    # ============================================================

    # Public proxy — listing (supports ?solution= ?industry= ?country=)
    path(
        "proxy/case-studies/",
        proxy_case_studies_api,
        name="proxy-case-studies",
    ),

    # Public proxy — filter options
    path(
        "proxy/case-study-filters/",
        proxy_case_study_filters_api,
        name="proxy-case-study-filters",
    ),

    # Public proxy — detail by case-study slug
    path(
        "proxy/case-studies/<slug:slug>/",
        proxy_case_study_detail_api,
        name="proxy-case-study-detail",
    ),

    # Protected API — listing + filtering
    path(
        "api/case-studies/",
        get_case_studies_api,
        name="api-case-studies",
    ),

    # Protected API — filter options (no slug, placed before detail)
    path(
        "api/case-study-filters/",
        get_case_study_filters_api,
        name="api-case-study-filters",
    ),

    # Protected API — detail by case-study slug
    path(
        "api/case-studies/<slug:slug>/",
        get_case_study_detail_api,
        name="api-case-study-detail",
    ),

    # ============================================================
    # EVENT DETAIL (with gallery)
    # ============================================================

    path(
        "proxy/event-detail/<int:event_id>/",
        proxy_event_detail_api,
        name="proxy-event-detail",
    ),

    path(
        "api/event-detail/<int:event_id>/",
        get_event_detail_api,
        name="api-event-detail",
    ),

    # ============================================================
    # TECHNOLOGY PARTNERS
    # ============================================================

    path(
        "proxy/partners/<slug:slug>/",
        proxy_partners_api,
        name="proxy-partners",
    ),

    path(
        "api/partners/<slug:slug>/",
        get_partners_api,
        name="api-partners",
    ),

    # ============================================================
    # PROMALLSHOP SITE CONTENT ? PROTECTED API
    path("api/promall/affiliate-banners/", get_promall_affiliate_banners_api, name="api-promall-affiliate-banners"),
    path("api/promall/events/", get_promall_events_api, name="api-promall-events"),
    path("api/promall/event-types/", get_promall_event_types_api, name="api-promall-event-types"),

    # PROMALLSHOP SITE CONTENT ? PUBLIC PROXY
    path("proxy/promall/affiliate-banners/", proxy_promall_affiliate_banners_api, name="proxy-promall-affiliate-banners"),
    path("proxy/promall/events/", proxy_promall_events_api, name="proxy-promall-events"),
    path("proxy/promall/event-types/", proxy_promall_event_types_api, name="proxy-promall-event-types"),

    # PROMALLSHOP BANNERS
    path("api/promall/banners/", get_promall_banners_api, name="api-promall-banners"),
    path("proxy/promall/banners/", proxy_promall_banners_api, name="proxy-promall-banners"),

    # PROMALLSHOP CATALOG — PROTECTED API
    # ============================================================

    path(
        'api/promall/categories/',
        get_promall_categories_api,
        name='api-promall-categories',
    ),

    path(
        'api/promall/categories/<slug:slug>/',
        get_promall_category_detail_api,
        name='api-promall-category-detail',
    ),

    path(
        'api/promall/categories/<slug:category_slug>/subcategories/<slug:subcategory_slug>/products/',
        get_promall_subcategory_products_api,
        name='api-promall-subcategory-products',
    ),

    path(
        'api/promall/products/',
        get_promall_products_api,
        name='api-promall-products',
    ),

    path(
        'api/promall/products/<str:product_id>/',
        get_promall_product_detail_api,
        name='api-promall-product-detail',
    ),

    path(
        'api/promall/flash-sale/<slug:slug>/',
        get_promall_flash_sale_api,
        name='api-promall-flash-sale',
    ),

    path(
        'api/promall/featured/<slug:slug>/',
        get_promall_featured_api,
        name='api-promall-featured',
    ),

    # ============================================================
    # PROMALLSHOP CATALOG — PUBLIC PROXY
    # ============================================================

    path(
        'proxy/promall/categories/',
        proxy_promall_categories_api,
        name='proxy-promall-categories',
    ),

    path(
        'proxy/promall/categories/<slug:slug>/',
        proxy_promall_category_detail_api,
        name='proxy-promall-category-detail',
    ),

    path(
        'proxy/promall/categories/<slug:category_slug>/subcategories/<slug:subcategory_slug>/products/',
        proxy_promall_subcategory_products_api,
        name='proxy-promall-subcategory-products',
    ),

    path(
        'proxy/promall/products/',
        proxy_promall_products_api,
        name='proxy-promall-products',
    ),

    path(
        'proxy/promall/products/<str:product_id>/',
        proxy_promall_product_detail_api,
        name='proxy-promall-product-detail',
    ),

    path(
        'proxy/promall/flash-sale/<slug:slug>/',
        proxy_promall_flash_sale_api,
        name='proxy-promall-flash-sale',
    ),

    path(
        'proxy/promall/featured/<slug:slug>/',
        proxy_promall_featured_api,
        name='proxy-promall-featured',
    ),
]
