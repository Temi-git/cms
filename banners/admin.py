from django.contrib import admin
from django.utils.html import format_html
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.admin import TokenAdmin


# to change the admin 
admin.site.site_header = "Banner Control Management"
admin.site.site_title = "BCM Admin"
admin.site.index_title = "BCM Administration"

from .models import (
    Entity,
    Banner,
    HomepageGif,
    FlashSale,
    TodayDeal,
    AffiliateBanner,
    UpcomingEvent,
    Product,
)


# ============================================================
# ENTITY INLINE CONTENT
# ============================================================

class BannerInline(admin.TabularInline):
    model = Banner
    extra = 1


class HomepageGifInline(admin.TabularInline):
    model = HomepageGif
    extra = 1


class FlashSaleInline(admin.TabularInline):
    model = FlashSale
    extra = 1


class TodayDealInline(admin.TabularInline):
    model = TodayDeal
    extra = 1


class AffiliateBannerInline(admin.TabularInline):
    model = AffiliateBanner
    extra = 1



class UpcomingEventInline(admin.TabularInline):
    model = UpcomingEvent
    extra = 1



# ============================================================
# ENTITY ADMIN
# ============================================================

@admin.register(Entity)
class EntityAdmin(admin.ModelAdmin):

    list_display = (
        'name',
        'slug',
        'url',
        'is_active',
        'banner_count',
        'gif_count',
       
        'flash_sale_count',
        'today_deal_count',
        'affiliate_banner_count',
        # 'featured_product_count',
        'event_count',
      
        'created_at',
    )

    search_fields = (
        'name',
        'slug',
        'url',
    )

    list_filter = (
        'is_active',
        'created_at',
    )

    prepopulated_fields = {
        'slug': ('name',)
    }
    # ========================================================
    # ALL HOMEPAGE CONTENT BELONGING TO THIS ENTITY
    # ========================================================

    inlines = [
        BannerInline,
        HomepageGifInline,
      
        FlashSaleInline,
        TodayDealInline,
        AffiliateBannerInline,
        # FeaturedProductInline,
        UpcomingEventInline,
      
    ]

    @admin.display(description='Banners')
    def banner_count(self, obj):
        return obj.banners.count()

    @admin.display(description='GIFs')
    def gif_count(self, obj):
        return obj.gifs.count()

 

    @admin.display(description='Flash Sales')
    def flash_sale_count(self, obj):
        return obj.flash_sales.count()

    @admin.display(description="Today's Deals")
    def today_deal_count(self, obj):
        return obj.today_deals.count()

    @admin.display(description='Affiliate Banners')
    def affiliate_banner_count(self, obj):
        return obj.affiliate_banners.count()

    # @admin.display(description='Featured Products')
    # def featured_product_count(self, obj):
    #     return obj.featured_products.count()

    @admin.display(description='Events')
    def event_count(self, obj):
        return obj.events.count()



# ============================================================
# BANNER ADMIN
# ============================================================

@admin.register(Banner)
class BannerAdmin(admin.ModelAdmin):

    list_display = (
        'title',
        'entity',
        'image_preview',
        'is_active',
        'created_at',
    )

    list_filter = (
        'entity',
        'is_active',
        'created_at',
    )

    search_fields = (
        'title',
        'text',
        'entity__name',
    )

    list_select_related = ('entity',)

    autocomplete_fields = ['entity']

    @admin.display(description='Thumbnail')
    def image_preview(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" style="max-height:50px; '
                'max-width:100px; border-radius:4px; '
                'object-fit:cover;" />',
                obj.image.url
            )

        return "No Image"


# ============================================================
# HOMEPAGE GIF ADMIN
# ============================================================

@admin.register(HomepageGif)
class HomepageGifAdmin(admin.ModelAdmin):

    list_display = (
        'id',
        'entity',
        'is_active',
    )

    list_filter = (
        'entity',
        'is_active',
    )




# ============================================================
# FLASH SALE ADMIN
# ============================================================

@admin.register(FlashSale)
class FlashSaleAdmin(admin.ModelAdmin):

    list_display = (
        'id',
        'entity',
        'is_active',
    )

    list_filter = (
        'entity',
        'is_active',
    )


# ============================================================
# TODAY'S DEAL ADMIN
# ============================================================

# admin.py – Update TodayDealAdmin

@admin.register(TodayDeal)
class TodayDealAdmin(admin.ModelAdmin):

    list_display = (
        'title',
        'entity',
        'product',           # Shows product name
        'image_preview',
        'start_datetime',
        'end_datetime',
        'is_active',
        'created_at',
    )

    list_filter = (
        'entity',
        'is_active',
    )

    search_fields = (
        'title',
        'subtitle',
        'entity__name',
        'product__name',     # Search by product name
    )

    list_select_related = ('entity', 'product')

    autocomplete_fields = ['entity', 'product']  # Nice dropdown!

    fieldsets = (
        (None, {
            'fields': (
                'entity',
                'product',       # Dropdown to select product
                'title',
                'subtitle',
                'image',
                'display_order',
                'is_active',
            ),
            'description': 'Select the product. The "BUY NOW" button will navigate to that product page.'
        }),
        ('Publishing', {
            'fields': (
                'start_datetime',
                'end_datetime',
            ),
            'classes': ('collapse',),
        }),
    )

    @admin.display(description='Thumbnail')
    def image_preview(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" style="max-height:50px; '
                'max-width:100px; border-radius:4px; '
                'object-fit:cover;" />',
                obj.image.url
            )
        return "No Image"


# ============================================================
# AFFILIATE BANNER ADMIN
# ============================================================

@admin.register(AffiliateBanner)
class AffiliateBannerAdmin(admin.ModelAdmin):

    list_display = (
        'id',
        'entity',
        'is_active',
    )

    list_filter = (
        'entity',
        'is_active',
    )



# ============================================================
# UPCOMING EVENT ADMIN
# ============================================================

@admin.register(UpcomingEvent)
class UpcomingEventAdmin(admin.ModelAdmin):

    list_display = (
        'name',
        'entity',
        'image_preview',
        'event_date',
        'is_active',
        'created_at',
    )

    list_filter = (
        'entity',
        'is_active',
        'event_date',
    )

    search_fields = (
        'name',
        'description',
    )

    date_hierarchy = 'event_date'

    @admin.display(description='Thumbnail')
    def image_preview(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" style="max-height:50px; '
                'max-width:100px; border-radius:4px; '
                'object-fit:cover;" />',
                obj.image.url
            )

        return "No Image"



# ============================================================
# TOKEN ADMIN
# ============================================================

@admin.register(Token)
class CustomTokenAdmin(TokenAdmin):

    list_display = (
        'key',
        'user',
        'created',
    )

    fields = (
        'user',
    )

    search_fields = (
        'user__username',
    )

    raw_id_fields = (
        'user',
    )


    # admin.py – Product admin

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'price', 'is_active', 'created_at')
    list_filter = ('is_active',)
    search_fields = ('name', 'slug', 'description')
    prepopulated_fields = {'slug': ('name',)}
    fields = ('name', 'slug', 'image', 'price', 'description', 'is_active')