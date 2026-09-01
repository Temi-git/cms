from django.core.exceptions import ValidationError
from django.core.validators import FileExtensionValidator
from django.db import models
from django.utils import timezone


# ============================================================
# ENTITY
# ============================================================


# models.py (add this near the top, after imports)

class Product(models.Model):
    name = models.CharField(
        max_length=200,
        help_text="Product name.",
    )
    slug = models.SlugField(
        max_length=200,
        unique=True,
        blank=True,
        help_text="URL-friendly version of the name.",
    )
    image = models.ImageField(
        upload_to="products/",
        help_text="Recommended size: 800 x 800 px. Product main image.",
    )
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Product price (optional).",
    )
    description = models.TextField(
        blank=True,
        help_text="Product description.",
    )
    is_active = models.BooleanField(
        default=True,
        help_text="Show this product on the site.",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']
        verbose_name = "Product"
        verbose_name_plural = "Products"

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            from django.utils.text import slugify
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)



class Entity(models.Model):
    """
    Represents a website/organization that owns homepage content.
    """

    name = models.CharField(
        max_length=200,
        help_text="The name of the entity.",
    )

    slug = models.SlugField(
        max_length=200,
        unique=True,
        help_text="Unique slug used in API URLs.",
    )

    url = models.URLField(
        help_text="The actual website URL for this entity.",
    )

    is_active = models.BooleanField(
        default=True,
        help_text="Designates whether this entity is active.",
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Entity"
        verbose_name_plural = "Entities"

    def __str__(self):
        return self.name

    @property
    def banner_count(self):
        return self.banners.count()

    @property
    def event_count(self):
        return self.events.count()

    @property
    def gif_count(self):
        return self.gifs.count()

    

    @property
    def flash_sale_count(self):
        return self.flash_sales.count()

    @property
    def affiliate_banner_count(self):
        return self.affiliate_banners.count()
    

    @property
    def today_deal_count(self):
        return self.today_deals.count()

    @property
    def upcoming_events(self):
        return self.events


# ============================================================
# PUBLISHABLE MIXIN
# ============================================================

class PublishableMixin(models.Model):
    """
    Shared active flag and optional publish window for homepage content.
    """

    is_active = models.BooleanField(
        default=True,
        help_text="Designates whether this content is enabled by an administrator.",
    )

    publish_start = models.DateTimeField(
        blank=True,
        null=True,
        help_text="Optional start of the publishing window.",
    )

    publish_end = models.DateTimeField(
        blank=True,
        null=True,
        help_text="Optional end of the publishing window.",
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True

    def clean(self):
        super().clean()

        if (
            self.publish_start
            and self.publish_end
            and self.publish_start > self.publish_end
        ):
            raise ValidationError({
                "publish_end": "Publish end must be on or after publish start.",
            })

    def is_currently_visible(self, at=None):
        if not self.is_active:
            return False

        moment = at or timezone.now()

        if self.publish_start and moment < self.publish_start:
            return False

        if self.publish_end and moment > self.publish_end:
            return False

        return True


# ============================================================
# SCHEDULED MIXIN
# ============================================================

class ScheduledMixin(models.Model):
    """
    Shared active flag and required schedule window for time-bound content.
    """

    is_active = models.BooleanField(
        default=True,
        help_text="Designates whether this content is enabled by an administrator.",
    )

    start_datetime = models.DateTimeField(
        help_text="When this content becomes eligible to display.",
    )

    end_datetime = models.DateTimeField(
        help_text="When this content stops being eligible to display.",
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True

    def clean(self):
        super().clean()

        if (
            self.start_datetime
            and self.end_datetime
            and self.start_datetime > self.end_datetime
        ):
            raise ValidationError({
                "end_datetime": "End datetime must be on or after start datetime.",
            })

    def is_currently_visible(self, at=None):
        if not self.is_active:
            return False

        moment = at or timezone.now()

        return self.start_datetime <= moment <= self.end_datetime

    @property
    def is_live_now(self):
        return self.is_currently_visible()

    @property
    def seconds_remaining(self):
        if not self.is_currently_visible():
            return 0

        remaining = (
            self.end_datetime - timezone.now()
        ).total_seconds()

        return max(0, int(remaining))


# ============================================================
# BANNER
# ============================================================

class Banner(PublishableMixin):

    entity = models.ForeignKey(
        Entity,
        related_name="banners",
        on_delete=models.CASCADE,
        help_text="Entity this banner belongs to.",
    )

    title = models.CharField(
        max_length=200,
        help_text="Title of the banner.",
    )

    text = models.TextField(
        blank=True,
        help_text="Banner description or body text.",
    )

    link = models.URLField(
        blank=True,
        help_text="Target URL when the banner is clicked.",
    )

    image = models.ImageField(
        upload_to="banners/",
        help_text="Recommended size: 1920 x 650 px",
    )

    display_order = models.PositiveIntegerField(
        default=0,
        help_text="Display order on the homepage. Lower numbers appear first.",
    )

    class Meta:
        ordering = ["display_order", "-created_at"]
        verbose_name = "Banner"
        verbose_name_plural = "Banners"

        indexes = [
            models.Index(
                fields=["entity", "is_active", "display_order"]
            ),
        ]

    def __str__(self):
        return f"{self.title} - {self.entity.name}"


# ============================================================
# HOMEPAGE GIF
# ============================================================

class HomepageGif(PublishableMixin):

    entity = models.ForeignKey(
        Entity,
        related_name="gifs",
        on_delete=models.CASCADE,
        help_text="Entity this GIF belongs to.",
    )

    title = models.CharField(
        max_length=200,
        help_text="Internal name or label for this GIF.",
    )

    description = models.TextField(
        blank=True,
        help_text="Optional description shown with the GIF.",
    )

    media_file = models.FileField(
        upload_to="gifs/",
        validators=[
            FileExtensionValidator(
                allowed_extensions=["gif"]
            )
        ],
        help_text="Recommended max width: 1200px, keep file size under 1MB",
    )

    link = models.URLField(
        blank=True,
        help_text="Optional destination URL when the GIF is clicked.",
    )

    display_order = models.PositiveIntegerField(
        default=0,
        help_text="Display order on the homepage. Lower numbers appear first.",
    )

    class Meta:
        ordering = ["display_order", "-created_at"]
        verbose_name = "Homepage GIF"
        verbose_name_plural = "Homepage GIFs"

        indexes = [
            models.Index(
                fields=["entity", "is_active", "display_order"]
            ),
        ]

    def __str__(self):
        return f"{self.title} - {self.entity.name}"



# ============================================================
# FLASH SALE
# ============================================================

class FlashSale(ScheduledMixin):

    entity = models.ForeignKey(
        Entity,
        related_name="flash_sales",
        on_delete=models.CASCADE,
        help_text="Entity this flash sale belongs to.",
    )

    title = models.CharField(
        max_length=200,
        help_text="Flash sale title.",
    )

    description = models.TextField(
        blank=True,
        help_text="Flash sale description.",
    )

    image = models.ImageField(
        upload_to="flash_sales/",
        help_text="Recommended size: 1200 x 267 px (use animated GIF)",
    )

    display_order = models.PositiveIntegerField(
        default=0,
        help_text="Display order on the homepage. Lower numbers appear first.",
    )

    class Meta:
        ordering = ["display_order", "-created_at"]
        verbose_name = "Flash Sale"
        verbose_name_plural = "Flash Sales"

        indexes = [
            models.Index(
                fields=[
                    "entity",
                    "is_active",
                    "start_datetime",
                    "end_datetime",
                ]
            ),
        ]

    def __str__(self):
        return f"{self.title} - {self.entity.name}"


# ============================================================
# TODAY'S DEAL
# ============================================================

# models.py – update TodayDeal

class TodayDeal(ScheduledMixin):

    entity = models.ForeignKey(
        Entity,
        related_name="today_deals",
        on_delete=models.CASCADE,
        help_text="Entity this deal belongs to.",
    )

    product = models.ForeignKey(
        'Product',  # Now this will work!
        on_delete=models.CASCADE,
        related_name='today_deals',
        help_text="Select the product. The 'BUY NOW' button will navigate to this product.",
    )

    title = models.CharField(
        max_length=200,
        help_text="Product/deal title, e.g. 'Yealink Flagship Smart Video Phone VP59'.",
    )

    subtitle = models.CharField(
        max_length=200,
        blank=True,
        help_text="Supporting text, e.g. 'Get one Belkin Power Surge free'.",
    )

    image = models.ImageField(
        upload_to="today_deals/",
        help_text="Recommended size: 800 x 800 px (square). Product/banner image.",
    )

    display_order = models.PositiveIntegerField(
        default=0,
        help_text="Display order. Lower numbers appear first.",
    )

    class Meta:
        ordering = ["display_order", "-created_at"]
        verbose_name = "Today's Deal"
        verbose_name_plural = "Today's Deals"

        indexes = [
            models.Index(
                fields=[
                    "entity",
                    "is_active",
                    "start_datetime",
                    "end_datetime",
                ]
            ),
        ]

    def __str__(self):
        entity_name = self.entity.name if self.entity else "No Entity"
        product_name = self.product.name if self.product else "No Product"
        return f"{self.title} - {entity_name} → {product_name}"

# ============================================================
# AFFILIATE BANNER
# ============================================================

class AffiliateBanner(PublishableMixin):

    entity = models.ForeignKey(
        Entity,
        related_name="affiliate_banners",
        on_delete=models.CASCADE,
        help_text="Entity this affiliate banner belongs to.",
    )

    title = models.CharField(
        max_length=200,
        help_text="Internal title for this affiliate banner.",
    )

    image = models.ImageField(
        upload_to="affiliate_banners/",
        help_text="Recommended size: 300 x 250 px or 728 x 90 px",
    )

    affiliate_url = models.URLField(
        help_text="External affiliate or target URL.",
    )

    display_order = models.PositiveIntegerField(
        default=0,
        help_text="Display order on the homepage. Lower numbers appear first.",
    )

    class Meta:
        ordering = ["display_order", "-created_at"]
        verbose_name = "Affiliate Banner"
        verbose_name_plural = "Affiliate Banners"

        indexes = [
            models.Index(
                fields=["entity", "is_active", "display_order"]
            ),
        ]

    def __str__(self):
        return f"{self.title} - {self.entity.name}"


# ============================================================
# UPCOMING EVENT
# ============================================================

class UpcomingEvent(PublishableMixin):

    entity = models.ForeignKey(
        Entity,
        related_name="events",
        on_delete=models.CASCADE,
        help_text="Entity this event belongs to.",
    )

    name = models.CharField(
        max_length=200,
        help_text="Event name.",
    )

    description = models.TextField(
        blank=True,
        help_text="Detailed description of the event.",
    )

    event_date = models.DateTimeField(
        help_text="Scheduled date and time for the event.",
    )

    image = models.ImageField(
        upload_to="events/",
        blank=True,
        null=True,
        help_text="Recommended size: 800 x 500 px (16:10 ratio)",
    )

    registration_link = models.URLField(
        blank=True,
        help_text="Optional registration or RSVP URL.",
    )

    class Meta:
        ordering = ["event_date"]
        verbose_name = "Upcoming Event"
        verbose_name_plural = "Upcoming Events"

        indexes = [
            models.Index(
                fields=["entity", "is_active", "event_date"]
            ),
        ]

    def __str__(self):
        return f"{self.name} - {self.entity.name}"

