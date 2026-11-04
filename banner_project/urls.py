from banners.promall_technites_admin import technites_pricing_admin, edit_technites_pricing
from banners.promall_live_taxonomy_admin import edit_live_subcategory
from banners.promall_live_taxonomy_admin import edit_live_category
from banners.promall_live_taxonomy_admin import live_categories_admin, live_subcategories_admin
"""
URL configuration for banner_project.
"""
from django.urls import include, path
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from banners.promall_live_admin import live_products_admin, edit_live_product
from banners.casdnet_cdn_admin import (
    cdn_products_admin,
    cdn_categories_admin,
    edit_cdn_product,
    edit_cdn_category,
)

urlpatterns = [
    path(
        'admin/technites/pricing/<str:product>/<str:tier>/edit/',
        admin.site.admin_view(edit_technites_pricing),
        name='promall_technites_edit',
    ),
    path(
        'admin/technites/pricing/',
        admin.site.admin_view(technites_pricing_admin),
        name='promall_technites_pricing',
    ),
    path('ckeditor5/', include('django_ckeditor_5.urls')),
    path(
        'admin/promall-live/subcategories/<int:subcategory_id>/edit/',
        admin.site.admin_view(edit_live_subcategory),
        name='promall_live_edit_subcategory',
    ),

    path(
        'admin/promall-live/categories/<int:category_id>/edit/',
        admin.site.admin_view(edit_live_category),
        name='promall_live_edit_category',
    ),


    path(
        'admin/promall-live/categories/',
        admin.site.admin_view(live_categories_admin),
        name='promall_live_categories',
    ),
    path(
        'admin/promall-live/subcategories/',
        admin.site.admin_view(live_subcategories_admin),
        name='promall_live_subcategories',
    ),

    path('admin/promall-live/products/<int:product_id>/edit/', admin.site.admin_view(edit_live_product), name='promall_live_edit_product'),
    path('admin/promall-live/products/', admin.site.admin_view(live_products_admin), name='promall_live_products'),
    # CASDNET REMOTE CDN MANAGEMENT
    path(
        'admin/casdnet/cdn-products/',
        admin.site.admin_view(cdn_products_admin),
        name='casdnet_cdn_products',
    ),
    path(
        'admin/casdnet/cdn-products/<str:product_id>/edit/',
        admin.site.admin_view(edit_cdn_product),
        name='casdnet_cdn_edit_product',
    ),
    path(
        'admin/casdnet/cdn-categories/',
        admin.site.admin_view(cdn_categories_admin),
        name='casdnet_cdn_categories',
    ),
    path(
        'admin/casdnet/cdn-categories/<str:category_id>/edit/',
        admin.site.admin_view(edit_cdn_category),
        name='casdnet_cdn_edit_category',
    ),
    path('admin/', admin.site.urls),
    path('', include('banners.urls')),
]

# Serve media files during development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

