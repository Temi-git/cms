from django.contrib import admin

from django import forms

from django_ckeditor_5.widgets import CKEditor5Widget

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

    FlashSale,

    TodayDeal,

    AffiliateBanner,

    UpcomingEvent,

    ThingWeDo,

    CybersecuritySolution,

    Project,

    Recognition,

    TeamCertificate,

    CaseStudy,

    CaseStudyImage,

    CaseStudyTechnology,

    CaseStudyResultROI,

    EventMedia,

    TechnologyPartner,

    PromallBanner,

    PromallEventType,

    PromallEvent,

    PromallSection1,

    PromallSection2,
    PromallSection3,

    PromallSubsection,
    PromallSubsection3,

    PromallWebsiteFAQ,

)





# ============================================================

# ENTITY INLINE CONTENT

# ============================================================



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

        FlashSaleInline,

        TodayDealInline,

        AffiliateBannerInline,

        # FeaturedProductInline,

        UpcomingEventInline,

        ThingWeDoInline,

        CybersecuritySolutionInline,

        ProjectInline,


        RecognitionInline,

        TeamCertificateInline,

    ]



    @admin.display(description='Banners')

    def banner_count(self, obj):

        return obj.banners.count()











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

        'entity',

        'media_type',

        'is_active',

        'created_at',

    )



    search_fields = (

        'title',

        'text',

        'entity__name',

    )



    # filter_horizontal renders a dual-listbox in the admin:

    #   Available Entities  ÃƒÂ¢Ã¢â‚¬Â Ã¢â‚¬â„¢  Chosen Entities

    # The admin can tick Proxynet Group, Promallshop, or both.

    # filter_horizontal = ('entities',)



    # Organize fields into sections for better admin UX

    fieldsets = (

        (None, {

            'fields': (

                'title',

                'proxy_title',

                'text',

                'link',

                'entity',        # ÃƒÂ¢Ã¢â‚¬Â Ã‚Â replaces the old 'entity' FK field

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



    @admin.display(description='Entity')

    def entity_list(self, obj):

     return obj.entity.name



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

                '<span style="color:#666; font-size:0.8em;">‚Â¬ YouTube Video</span>'

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

# FLASH SALE ADMIN

# ============================================================



@admin.register(FlashSale)

class FlashSaleAdmin(admin.ModelAdmin):



    list_display = (

        'id',

        'entity',

        'start_datetime',

        'end_datetime',

        'is_active',

    )



    fields = (

        'entity',

        'start_datetime',

        'end_datetime',

        'display_order',

        'is_active',

    )



    list_filter = (

        'entity',

        'is_active',

    )





# ============================================================

# TODAY'S DEAL ADMIN

# ============================================================



# admin.py ÃƒÂ¢Ã¢â€šÂ¬Ã¢â‚¬Å“ Update TodayDealAdmin



@admin.register(TodayDeal)

class TodayDealAdmin(admin.ModelAdmin):



    list_display = (

        'title',

        'entity',

        'buy_now_url',

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

    )



    list_select_related = ('entity',)



    autocomplete_fields = ['entity']



    fieldsets = (

        (None, {

            'fields': (

                'entity',

                'buy_now_url',

                'title',

                'subtitle',

                'image',

                'display_order',

                'is_active',

            ),

            'description': "Paste the full product link. The BUY NOW button opens this URL.",

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

        "id",

        "title",

        "entity",

        "placement",

        "is_active",

        "display_order",

    )

    list_filter = ("entity", "placement", "is_active")

    search_fields = ("title", "entity__name")

    list_editable = ("placement", "is_active", "display_order")

    ordering = ("entity", "display_order", "-created_at")



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

    )



    list_select_related = ('entity',)



    autocomplete_fields = ['entity']



    fieldsets = (

        (None, {

            'fields': (

                'title',

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



    def formfield_for_dbfield(self, db_field, request, **kwargs):
        if db_field.name == "issuing_organization":
            kwargs["label"] = "Subtitle"
        return super().formfield_for_dbfield(db_field, request, **kwargs)

    fieldsets = (

        (None, {

            'fields': (

                'title',

                'issuing_organization',

                'description',

                'entity',

            ),

        }),

('Details', {

            'fields': (

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



# ============================================================

# CASE STUDY ADMIN

# ============================================================



class CaseStudyImageInline(admin.TabularInline):

    model = CaseStudyImage

    extra = 2

    fields = ('image', 'video', 'caption', 'display_order')





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





# ============================================================

# PROMALLSHOP CATALOG ADMIN

# ============================================================



from .models import (

    PromallCategory,

    PromallCategoryFAQ,

    PromallSubcategory,

    PromallProduct,

    PromallProductFAQ,

)





class PromallCategoryFAQInline(admin.TabularInline):

    model = PromallCategoryFAQ

    fields = ('question', 'answer', 'display_order', 'is_active')

    extra = 1





class PromallSubcategoryInline(admin.TabularInline):

    model = PromallSubcategory

    fields = ('name', 'slug', 'display_order', 'is_active')

    extra = 1





class PromallProductFAQInline(admin.TabularInline):

    model = PromallProductFAQ

    fields = ('question', 'answer', 'display_order', 'is_active')

    extra = 1





@admin.register(PromallCategory)

class PromallCategoryAdmin(admin.ModelAdmin):

    list_display = ('name', 'slug', 'external_id', 'is_active', 'display_order')

    search_fields = ('name', 'slug', 'external_id')

    list_filter = ('is_active',)

    list_editable = ('is_active', 'display_order')

    prepopulated_fields = {'slug': ('name',)}

    readonly_fields = ('external_id',)

    inlines = [PromallCategoryFAQInline, PromallSubcategoryInline]

    fieldsets = (

        ('Basic Info', {'fields': (

            'entity', 'external_id', 'name', 'slug',

            'description', 'icon', 'display_order', 'is_active',

        )}),

    )





@admin.register(PromallSubcategory)

class PromallSubcategoryAdmin(admin.ModelAdmin):

    list_display = ('name', 'category', 'slug', 'external_id', 'is_active', 'display_order')

    search_fields = ('name', 'slug', 'external_id')

    list_filter = ('category', 'is_active')

    list_editable = ('is_active', 'display_order')

    prepopulated_fields = {'slug': ('name',)}

    readonly_fields = ('external_id',)





@admin.register(PromallProduct)

class PromallProductAdmin(admin.ModelAdmin):

    list_display = (

        'name', 'category', 'subcategory', 'price',

        'is_hot', 'is_special', 'is_active', 'display_order',

    )

    list_editable = ('is_hot', 'is_special', 'is_active')

    search_fields = ('name', 'model_number', 'part_number', 'external_id')

    list_filter = ('category', 'subcategory', 'is_hot', 'is_special', 'is_active')

    list_select_related = ('category', 'subcategory')

    readonly_fields = (

        'external_id', 'external_image_paths',

        'alternative_product_ids', 'complementary_product_ids',

    )

    prepopulated_fields = {'slug': ('name',)}

    inlines = [PromallProductFAQInline]

    fieldsets = (

        ('Product Info', {'fields': (

            'entity', 'external_id', 'category', 'subcategory',

            'name', 'slug', 'short_description', 'description',

            'model_number', 'part_number', 'warranty', 'video_url',

        )}),

        ('Pricing', {'fields': ('price', 'end_user_price', 'discount', 'quantity')}),

        ('Media', {

            'fields': ('image', 'external_image_paths'),

            'description': 'Upload only for admin-created products. Synced products use external_image_paths.',

        }),

        ('Flags', {'fields': ('is_hot', 'is_special', 'is_active', 'display_order')}),

        ('SEO', {'fields': ('meta_title', 'meta_description', 'keywords')}),

        ('API Data (read-only)', {'fields': ('alternative_product_ids', 'complementary_product_ids')}),

    )



# ============================================================

# PROMALL SITE CONTENT ADMIN

# ============================================================



@admin.register(PromallBanner)

class PromallBannerAdmin(admin.ModelAdmin):

    list_display = ("title", "entity", "is_active", "display_order", "created_at")

    list_filter = ("entity", "is_active")

    search_fields = ("title", "description")

    list_editable = ("is_active", "display_order")

    ordering = ("display_order", "-created_at")





@admin.register(PromallEventType)

class PromallEventTypeAdmin(admin.ModelAdmin):

    list_display = ("name", "slug", "entity", "is_active", "display_order")

    list_filter = ("entity", "is_active")

    search_fields = ("name", "slug")

    prepopulated_fields = {"slug": ("name",)}

    list_editable = ("is_active", "display_order")

    ordering = ("display_order", "name")





@admin.register(PromallEvent)

class PromallEventAdmin(admin.ModelAdmin):

    list_display = (

        "name",

        "entity",

        "event_type",

        "event_datetime",

        "location",

        "is_active",

        "display_order",

    )

    list_filter = ("entity", "event_type", "is_active")

    search_fields = ("name", "description", "location")

    list_editable = ("is_active", "display_order")

    ordering = ("event_datetime", "display_order")

    date_hierarchy = "event_datetime"











# ============================================================

# PROMALLSHOP CATEGORY GIF ADMIN

# ============================================================



from .models import PromallCategoryGIF

from .promall_category_gif_forms import PromallCategoryGIFForm





@admin.register(PromallCategoryGIF)

class PromallCategoryGIFAdmin(admin.ModelAdmin):

    form = PromallCategoryGIFForm



    list_display = (

        "category_name",

        "category_id",

        "gif_preview",

        "is_active",

        "updated_at",

    )



    search_fields = ("category_name", "category_id")

    list_filter = ("is_active",)

    readonly_fields = ("gif_preview", "created_at", "updated_at")



    fieldsets = (

        ("Category", {

            "fields": ("category_id",),

        }),

        ("GIF", {

            "fields": ("gif", "gif_preview"),

        }),

        ("Visibility", {

            "fields": ("is_active",),

        }),

        ("Timestamps", {

            "fields": ("created_at", "updated_at"),

        }),

    )





    @admin.display(description="GIF Preview")

    def gif_preview(self, obj):

        if not obj or not obj.pk or not obj.gif:

            return "No GIF uploaded yet"



        return format_html(

            '<img src="{}" alt="Category GIF" '

            'style="max-width:280px; max-height:180px; '

            'object-fit:contain; border-radius:6px;" />',

            obj.gif.url,

        )







# ============================================================

# PROMALLSHOP SECTION 1 AND SECTION 2 ADMIN

# ============================================================



class PromallSubsectionInline(admin.StackedInline):

    model = PromallSubsection

    extra = 1

    fields = ("title", "description", "display_order")

    ordering = ("display_order", "id")





@admin.register(PromallSection1)

class PromallSection1Admin(admin.ModelAdmin):

    list_display = ("title", "entity", "is_active", "updated_at")

    list_filter = ("is_active",)

    search_fields = ("title", "subtitle", "description", "entity__name")

    readonly_fields = ("created_at", "updated_at")

    fieldsets = (

        ("Website and Content", {

            "fields": ("entity", "title", "subtitle", "description", "link")

        }),

        ("Display Settings", {"fields": ("is_active",)}),

        ("Timestamps", {"fields": ("created_at", "updated_at")}),

    )





@admin.register(PromallSection2)

class PromallSection2Admin(admin.ModelAdmin):

    list_display = ("title", "entity", "is_active", "updated_at")

    list_filter = ("is_active",)

    search_fields = ("title", "subtitle", "description", "entity__name")

    readonly_fields = ("created_at", "updated_at")

    inlines = (PromallSubsectionInline,)

    fieldsets = (

        ("Website and Content", {

            "fields": ("entity", "title", "subtitle", "description")

        }),

        ("Display Settings", {"fields": ("is_active",)}),

        ("Timestamps", {"fields": ("created_at", "updated_at")}),

    )






class PromallSubsection3Inline(admin.StackedInline):
    model = PromallSubsection3
    extra = 1
    fields = ("title", "description", "display_order")
    ordering = ("display_order", "id")


@admin.register(PromallSection3)
class PromallSection3Admin(admin.ModelAdmin):
    list_display = ("title", "entity", "is_active", "updated_at")
    list_filter = ("is_active",)
    search_fields = ("title", "subtitle", "entity__name")
    readonly_fields = ("created_at", "updated_at")
    inlines = (PromallSubsection3Inline,)

    fieldsets = (
        ("Website and Content", {
            "fields": ("entity", "title", "subtitle")
        }),
        ("Display Settings", {
            "fields": ("is_active",)
        }),
        ("Timestamps", {
            "fields": ("created_at", "updated_at")
        }),
    )

@admin.register(PromallWebsiteFAQ)

class PromallWebsiteFAQAdmin(admin.ModelAdmin):

    list_display = ("question", "entity", "is_active", "display_order")

    list_filter = ("entity", "is_active")

    search_fields = ("question", "answer", "entity__name")

    list_editable = ("is_active", "display_order")

    ordering = ("display_order", "id")

    readonly_fields = ("created_at", "updated_at")

    fieldsets = (

        ("Website FAQ", {

            "fields": ("entity", "question", "answer")

        }),

        ("Display Settings", {

            "fields": ("display_order", "is_active")

        }),

        ("Timestamps", {

            "fields": ("created_at", "updated_at")

        }),

    )

# ============================================================
# CASDNET ADMIN
# ============================================================

from .models import CasdnetCategory, CasdnetBanner
from django.utils.html import format_html as casdnet_format_html


@admin.register(CasdnetCategory)
class CasdnetCategoryAdmin(admin.ModelAdmin):
    list_display = ("entity", "title", "link", "image_preview", "created_at")
    search_fields = ("title", "link")
    readonly_fields = ("image_preview", "created_at", "updated_at")
    fields = ("entity", "title", "image", "image_preview", "link", "created_at", "updated_at")

    @admin.display(description="Image")
    def image_preview(self, obj):
        if obj and obj.image:
            return casdnet_format_html(
                '<img src="{}" style="max-height:65px;max-width:110px;object-fit:contain;" />',
                obj.image.url,
            )
        return "No image"


@admin.register(CasdnetBanner)
class CasdnetBannerAdmin(admin.ModelAdmin):
    list_display = ("entity", "title", "subtitle", "link", "image_preview", "created_at")
    search_fields = ("title", "subtitle", "link")
    readonly_fields = ("image_preview", "created_at", "updated_at")
    fields = (
        "entity", "title", "subtitle", "link", "image",
        "image_preview", "created_at", "updated_at",
    )

    @admin.display(description="Image")
    def image_preview(self, obj):
        if obj and obj.image:
            return casdnet_format_html(
                '<img src="{}" style="max-height:65px;max-width:110px;object-fit:contain;" />',
                obj.image.url,
            )
        return "No image"



