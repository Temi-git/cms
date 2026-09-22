from django.contrib import admin
from django.utils.html import format_html
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.admin import TokenAdmin


# to change the admin 
admin.site.site_header = "Banner Control Management"
admin.site.site_title = "CMS Admin"
admin.site.index_title = "CMS Administration"

from .models import (
    Entity,
    Banner,
    HomepageGif,
    FlashSale,
    TodayDeal,
    AffiliateBanner,
    UpcomingEvent,
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


# ============================================================
# ENTITY INLINE CONTENT
# ============================================================

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


class EventMediaInline(admin.TabularInline):
    model = EventMedia
    extra = 2
    fields = ('media_type', 'image', 'video_file', 'caption', 'display_order')
    verbose_name = "Gallery Item"
    verbose_name_plural = "Event Gallery"


class ThingWeDoInline(admin.TabularInline):
    model = ThingWeDo
    extra = 1


class CybersecuritySolutionInline(admin.TabularInline):
    model = CybersecuritySolution
    extra = 1


class ProjectInline(admin.TabularInline):
    model = Project
    extra = 1


class BlogPostInline(admin.TabularInline):
    model = BlogPost
    extra = 1


class RecognitionInline(admin.TabularInline):
    model = Recognition
    extra = 1


class TeamCertificateInline(admin.TabularInline):
    model = TeamCertificate
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
        'recognition_count',
        'team_certificate_count',
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
        HomepageGifInline,
        FlashSaleInline,
        TodayDealInline,
        AffiliateBannerInline,
        # FeaturedProductInline,
        UpcomingEventInline,
        ThingWeDoInline,
        CybersecuritySolutionInline,
        ProjectInline,
        BlogPostInline,
        RecognitionInline,
        TeamCertificateInline,
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

    @admin.display(description='Recognitions')
    def recognition_count(self, obj):
        return obj.recognitions.count()

    @admin.display(description='Team Certificates')
    def team_certificate_count(self, obj):
        return obj.team_certificates.count()



# ============================================================
# BANNER ADMIN
# ============================================================


@admin.register(Banner)
class BannerAdmin(admin.ModelAdmin):

    list_display = (
        'title',
        'entity_list',
        'media_type',
        'media_preview',
        'is_active',
        'created_at',
    )

    list_filter = (
        'entities',
        'media_type',
        'is_active',
        'created_at',
    )

    search_fields = (
        'title',
        'text',
        'entities__name',
    )

    # filter_horizontal renders a dual-listbox in the admin:
    #   Available Entities  →  Chosen Entities
    # The admin can tick Proxynet Group, Promallshop, or both.
    filter_horizontal = ('entities',)

    # Organize fields into sections for better admin UX
    fieldsets = (
        (None, {
            'fields': (
                'title',
                'proxy_title',
                'text',
                'link',
                'entities',        # ← replaces the old 'entity' FK field
                'media_type',
            )
        }),
        ('Media File', {
            'fields': (
                'image',
                'video_file',
                'video_url',
            ),
            'description': 'Upload the appropriate media based on the selected Media Type above.'
        }),
        ('Display Settings', {
            'fields': (
                'display_order',
                'is_active',
                'publish_start',
                'publish_end',
            ),
            'classes': ('collapse',),
        }),
    )

    @admin.display(description='Entities')
    def entity_list(self, obj):
        """Show all assigned entities as a comma-separated string."""
        names = [e.name for e in obj.entities.all()]
        if not names:
            return '—'
        return ', '.join(names)

    @admin.display(description='Media Preview')
    def media_preview(self, obj):
        """Show a preview of the media (image or video)"""
        if obj.media_type == 'video' and obj.video_file:
            return format_html(
                '<video style="max-height:50px; max-width:100px; border-radius:4px;" muted>'
                '<source src="{}" type="video/mp4">'
                'Your browser does not support the video tag.</video>',
                obj.video_file.url
            )
        elif obj.media_type == 'image' and obj.image:
            return format_html(
                '<img src="{}" style="max-height:50px; max-width:100px; border-radius:4px; object-fit:cover;" />',
                obj.image.url
            )
        elif obj.media_type == 'youtube' and obj.video_url:
            return format_html(
                '<span style="color:#666; font-size:0.8em;">🎬 YouTube Video</span>'
            )
        return "No Media"

    @admin.display(description='Thumbnail')
    def image_preview(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" style="max-height:50px; max-width:100px; border-radius:4px; object-fit:cover;" />',
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
        "event_type",
        'entity',
        'location',
        'event_date',
        'lifecycle_status',
        'image_preview',
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
        'location',
        'entity__name',
    )

    list_select_related = ('entity',)

    autocomplete_fields = ['entity']

    date_hierarchy = 'event_date'

    inlines = [EventMediaInline]

    fieldsets = (
        ('Event Information', {
            'fields': (
                'entity',
                'name',
                'event_type',
                'description',
                'location',
            ),
        }),
        ('Schedule', {
            'fields': (
                'event_date',
                'registration_link',
            ),
        }),
        ('Cover Image', {
            'fields': (
                'image',
            ),
        }),
        ('Publishing', {
            'fields': (
                'is_active',
                'publish_start',
                'publish_end',
            ),
            'classes': ('collapse',),
        }),
    )

    @admin.display(description='Status')
    def lifecycle_status(self, obj):
        status = obj.lifecycle_status
        colour = '#16a34a' if status == 'upcoming' else '#64748b'
        label = 'Upcoming' if status == 'upcoming' else 'Past'
        return format_html(
            '<span style="color:{};font-weight:600;">{}</span>',
            colour,
            label,
        )

    @admin.display(description='Thumbnail')
    def image_preview(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" style="max-height:50px; '
                'max-width:100px; border-radius:4px; '
                'object-fit:cover;" />',
                obj.image.url,
            )
        return "No Image"




# ============================================================
# THINGS WE DO ADMIN
# ============================================================

@admin.register(ThingWeDo)
class ThingWeDoAdmin(admin.ModelAdmin):

    list_display = (
        'title',
        'entity',
        'image_preview',
        'is_active',
        'display_order',
        'created_at',
    )

    list_filter = (
        'entity',
        'is_active',
    )

    search_fields = (
        'title',
        'description',
        'full_description',
    )

    list_select_related = ('entity',)

    autocomplete_fields = ['entity']

    fieldsets = (
        (None, {
            'fields': (
                'title',
                'description',
                'full_description',
                'entity',
            )
        }),
        ('Media', {
            'fields': (
                'image',
            ),
        }),
        ('Display Settings', {
            'fields': (
                'display_order',
                'is_active',
                'publish_start',
                'publish_end',
            ),
            'classes': ('collapse',),
        }),
    )

    @admin.display(description='Image')
    def image_preview(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" style="max-height:50px; max-width:100px; '
                'border-radius:4px; object-fit:cover;" />',
                obj.image.url
            )
        return "No Image"


# ============================================================
# CYBERSECURITY SOLUTION ADMIN
# ============================================================

@admin.register(CybersecuritySolution)
class CybersecuritySolutionAdmin(admin.ModelAdmin):

    list_display = (
        'title',
        'product_name',
        'entity',
        'image_preview',
        'is_active',
        'display_order',
        'created_at',
    )

    list_filter = (
        'entity',
        'is_active',
    )

    search_fields = (
        'title',
        'product_name',
        'description',
    )

    list_select_related = ('entity',)

    autocomplete_fields = ['entity']

    fieldsets = (
        ('Solution Details', {
            'fields': (
                'entity',
                'title',
                'product_name',
                'description',
            ),
            'description': (
                'Title = solution category (e.g. "Identity & Authentication"). '
                'Product Name = vendor/product (e.g. "V-Key").'
            ),
        }),
        ('Images', {
            'fields': (
                'image',
                'product_logo',
            ),
            'description': (
                '"Main Product Image" is the large card/slide image. '
                '"Product/Vendor Logo" is the small logo shown below the description.'
            ),
        }),
        ('Display Settings', {
            'fields': (
                'display_order',
                'is_active',
                'publish_start',
                'publish_end',
            ),
            'classes': ('collapse',),
        }),
    )

    @admin.display(description='Image')
    def image_preview(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" style="max-height:50px; max-width:100px; '
                'border-radius:4px; object-fit:cover;" />',
                obj.image.url
            )
        return "No Image"


# ============================================================
# PROJECT ADMIN
# ============================================================

@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):

    list_display = (
        'title',
        'category',
        'entity',
        'image_preview',
        'is_active',
        'display_order',
        'created_at',
    )

    list_filter = (
        'entity',
        'category',
        'is_active',
    )

    search_fields = (
        'title',
        'description',
        'more_description',
        'category',
    )

    list_select_related = ('entity',)

    autocomplete_fields = ['entity']

    fieldsets = (
        (None, {
            'fields': (
                'title',
                'description',
                'more_description',
                'entity',
            )
        }),
        ('Media & Links', {
            'fields': (
                'category',
                'image',
                'project_url',
            ),
        }),
        ('Display Settings', {
            'fields': (
                'display_order',
                'is_active',
                'publish_start',
                'publish_end',
            ),
            'classes': ('collapse',),
        }),
    )

    @admin.display(description='Image')
    def image_preview(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" style="max-height:50px; max-width:100px; '
                'border-radius:4px; object-fit:cover;" />',
                obj.image.url
            )
        return "No Image"


# ============================================================
# BLOG POST ADMIN
# ============================================================

@admin.register(BlogPost)
class BlogPostAdmin(admin.ModelAdmin):

    list_display = (
        'title',
        'entity',
        'image_preview',
        'published_at',
        'is_active',
        'created_at',
    )

    list_filter = (
        'entity',
        'is_active',
        'published_at',
    )

    search_fields = (
        'title',
        'excerpt',
        'content',
    )

    list_select_related = ('entity',)

    autocomplete_fields = ['entity']

    prepopulated_fields = {'slug': ('title',)}

    date_hierarchy = 'published_at'

    fieldsets = (
        (None, {
            'fields': (
                'title',
                'slug',
                'entity',
            )
        }),
        ('Content', {
            'fields': (
                'excerpt',
                'content',
                'image',
            ),
        }),
        ('Meta', {
            'fields': (
                'published_at',
            ),
        }),
        ('Display Settings', {
            'fields': (
                'display_order',
                'is_active',
                'publish_start',
                'publish_end',
            ),
            'classes': ('collapse',),
        }),
    )

    @admin.display(description='Image')
    def image_preview(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" style="max-height:50px; max-width:100px; '
                'border-radius:4px; object-fit:cover;" />',
                obj.image.url
            )
        return "No Image"
# ============================================================
# RECOGNITION ADMIN
# ============================================================

@admin.register(Recognition)
class RecognitionAdmin(admin.ModelAdmin):

    list_display = (
        'title',
        'entity',
        'issuing_organization',
        'year',
        'image_preview',
        'is_active',
        'display_order',
        'created_at',
    )

    list_filter = (
        'entity',
        'is_active',
    )

    search_fields = (
        'title',
        'issuing_organization',
        'description',
    )

    list_select_related = ('entity',)

    autocomplete_fields = ['entity']

    fieldsets = (
        (None, {
            'fields': (
                'title',
                'issuing_organization',
                'description',
                'entity',
            ),
        }),
        ('Media', {
            'fields': (
                'image',
            ),
        }),
        ('Details', {
            'fields': (
                'year',
                'display_order',
            ),
        }),
        ('Display Settings', {
            'fields': (
                'is_active',
                'publish_start',
                'publish_end',
            ),
            'classes': ('collapse',),
        }),
    )

    @admin.display(description='Image')
    def image_preview(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" style="max-height:50px; max-width:100px; '
                'border-radius:4px; object-fit:cover;" />',
                obj.image.url,
            )
        return "No Image"


# ============================================================
# TEAM CERTIFICATE ADMIN
# ============================================================

@admin.register(TeamCertificate)
class TeamCertificateAdmin(admin.ModelAdmin):

    list_display = (
        'title',
        'entity',
        'issuing_organization',
        'year',
        'image_preview',
        'is_active',
        'display_order',
        'created_at',
    )

    list_filter = (
        'entity',
        'is_active',
    )

    search_fields = (
        'title',
        'issuing_organization',
        'description',
    )

    list_select_related = ('entity',)

    autocomplete_fields = ['entity']

    fieldsets = (
        (None, {
            'fields': (
                'title',
                'issuing_organization',
                'description',
                'entity',
            ),
        }),
        ('Media', {
            'fields': (
                'image',
            ),
        }),
        ('Details', {
            'fields': (
                'year',
                'display_order',
            ),
        }),
        ('Display Settings', {
            'fields': (
                'is_active',
                'publish_start',
                'publish_end',
            ),
            'classes': ('collapse',),
        }),
    )

    @admin.display(description='Image')
    def image_preview(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" style="max-height:50px; max-width:100px; '
                'border-radius:4px; object-fit:cover;" />',
                obj.image.url,
            )
        return "No Image"


# ============================================================
# CASE STUDY ADMIN
# ============================================================

class CaseStudyImageInline(admin.TabularInline):
    model = CaseStudyImage
    extra = 2
    fields = ('image', 'caption', 'display_order')


class CaseStudyTechnologyInline(admin.TabularInline):
    model = CaseStudyTechnology
    extra = 2
    fields = ('name', 'display_order')
    verbose_name = "Technology Used"
    verbose_name_plural = "Technologies Used"


class CaseStudyResultROIInline(admin.TabularInline):
    model = CaseStudyResultROI
    extra = 2
    fields = ('content', 'display_order')
    verbose_name = "Result & ROI Item"
    verbose_name_plural = "Result & ROI Items"


@admin.register(CaseStudy)
class CaseStudyAdmin(admin.ModelAdmin):

    list_display = (
        'title',
        'entity',
        'client',
        'solution',
        'industry',
        'country',
        'featured_image_preview',
        'is_active',
        'display_order',
        'created_at',
    )

    list_filter = (
        'entity',
        'is_active',
        'solution',
        'industry',
        'country',
    )

    search_fields = (
        'title',
        'client',
        'solution',
        'industry',
        'country',
        'short_description',
        'entity__name',
    )

    prepopulated_fields = {'slug': ('title',)}

    list_select_related = ('entity',)

    autocomplete_fields = ['entity']

    inlines = [CaseStudyImageInline, CaseStudyTechnologyInline, CaseStudyResultROIInline]

    fieldsets = (
        ('Basic Information', {
            'fields': (
                'entity',
                'title',
                'slug',
                'client',
                'solution',
                'industry',
                'country',
                'short_description',
                'featured_image',
            ),
        }),
        ('Case Study Details', {
            'fields': (
                'client_overview',
                'challenge',
                'solution_details',
                'implementation',
            ),
        }),
        ('Publishing', {
            'fields': (
                'display_order',
                'is_active',
                'publish_start',
                'publish_end',
            ),
            'classes': ('collapse',),
        }),
    )

    @admin.display(description='Featured Image')
    def featured_image_preview(self, obj):
        if obj.featured_image:
            return format_html(
                '<img src="{}" style="max-height:50px; max-width:100px; '
                'border-radius:4px; object-fit:cover;" />',
                obj.featured_image.url,
            )
        return "No Image"


# ============================================================
# TECHNOLOGY PARTNER ADMIN
# ============================================================

@admin.register(TechnologyPartner)
class TechnologyPartnerAdmin(admin.ModelAdmin):

    list_display = (
        'name',
        'entity',
        'logo_preview',
        'is_active',
        'display_order',
        'created_at',
    )

    list_filter = (
        'entity',
        'is_active',
    )

    search_fields = (
        'name',
        'entity__name',
        'description',
    )

    list_select_related = ('entity',)

    autocomplete_fields = ['entity']

    fieldsets = (
        ('Partner Details', {
            'fields': (
                'name',
                'entity',
                'description',
            ),
        }),
        ('Logo', {
            'fields': (
                'logo',
            ),
        }),
        ('Display Settings', {
            'fields': (
                'display_order',
                'is_active',
            ),
        }),
    )

    @admin.display(description='Logo')
    def logo_preview(self, obj):
        if obj.logo:
            return format_html(
                '<img src="{}" style="max-height:50px; max-width:120px; '
                'border-radius:4px; object-fit:contain;" />',
                obj.logo.url,
            )
        return "No Logo"


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