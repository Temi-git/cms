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

urlpatterns = [
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
    path('admin/', admin.site.urls),
    path('', include('banners.urls')),
]

# Serve media files during development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
