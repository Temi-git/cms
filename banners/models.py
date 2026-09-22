from django.core.exceptions import ValidationError
from django.core.validators import FileExtensionValidator
from django.db import models
from django.utils import timezone


# ============================================================
# ENTITY
# ============================================================

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

    # ============================================================
    # ENTITY PROPERTIES - ALL CONTENT COUNTS
    # ============================================================

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

    # New properties for Proxynet models
    @property
    def things_we_do_count(self):
        return self.things_we_do.count()

    @property
    def cybersecurity_solutions_count(self):
        return self.cybersecurity_solutions.count()

    @property
    def projects_count(self):
        return self.projects.count()

    @property
    def blog_posts_count(self):
        return self.blog_posts.count()

    @property
    def recognition_count(self):
        return self.recognitions.count()

    @property
    def team_certificate_count(self):
        return self.team_certificates.count()

    @property
    def case_study_count(self):
        return self.case_studies.count()

    @property
    def total_content_count(self):
        """Total count of all content across all models for this entity"""
        return (
            self.banner_count +
            self.gif_count +
            self.flash_sale_count +
            self.today_deal_count +
            self.affiliate_banner_count +
            self.event_count +
            self.things_we_do_count +
            self.cybersecurity_solutions_count +
            self.projects_count +
            self.blog_posts_count +
            self.recognition_count +
            self.team_certificate_count +
            self.case_study_count
        )


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

    MEDIA_CHOICES = [
        ('image', 'Image'),
        ('video', 'Video'),
        ('youtube', 'YouTube Video'),
    ]

    entities = models.ManyToManyField(
        Entity,
        related_name="banners",
        help_text="Select one or more entities this banner belongs to.",
        verbose_name="Entities",
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

    # --- Existing Image Field ---
    image = models.ImageField(
        upload_to="banners/",
        help_text="Recommended size: 1920 x 650 px. Upload an image (if media type is 'Image').",
        blank=True,
        null=True,
    )

    # --- New Media Fields ---
    media_type = models.CharField(
        max_length=10,
        choices=MEDIA_CHOICES,
        default='image',
        help_text="Select the type of media for this banner.",
    )

    video_file = models.FileField(
        upload_to='banner_videos/',
        blank=True,
        null=True,
        help_text="Upload an MP4 or WebM video file (if media type is 'Video'). Recommended max size: 20MB.",
    )

    video_url = models.URLField(
        blank=True,
        help_text="Enter a YouTube or Vimeo URL (if media type is 'YouTube Video'). Example: https://www.youtube.com/watch?v=VIDEO_ID",
    )
    # --- End New Fields ---

    proxy_title = models.CharField(
        max_length=200,
        blank=True,
        help_text="Optional title override used by proxy/external displays. Leave blank to use the main title.",
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
                fields=["is_active", "display_order"]
            ),
        ]

    def __str__(self):
        entity_names = ", ".join(
            e.name for e in self.entities.all()
        ) or "No Entity"
        return f"{self.title} - [{entity_names}]"


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

class TodayDeal(ScheduledMixin):

    entity = models.ForeignKey(
        Entity,
        related_name="today_deals",
        on_delete=models.CASCADE,
        help_text="Entity this deal belongs to.",
    )

    product = models.ForeignKey(
        'Product',
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

    location = models.CharField(
        max_length=300,
        blank=True,
        help_text="Venue or location of the event (e.g., 'Lagos Business School, Lekki').",
    )

    event_type = models.CharField(
        max_length=100,
        blank=True,
        default="",
        verbose_name="Event Type",
        help_text="Type of event (e.g., Conference, Exhibition, Product Launch, Workshop).",
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

    @property
    def is_upcoming(self):
        """True if the event date/time is in the future (UTC-aware)."""
        return self.event_date > timezone.now()

    @property
    def is_past(self):
        """True if the event date/time has already passed."""
        return self.event_date <= timezone.now()

    @property
    def lifecycle_status(self):
        """Returns 'upcoming' or 'past' based on event_date vs now."""
        return "upcoming" if self.is_upcoming else "past"


# ============================================================
# EVENT MEDIA
# ============================================================

class EventMedia(models.Model):
    """
    Gallery item (image or video) belonging to a single UpcomingEvent.
    One UpcomingEvent → many EventMedia records.
    Follows the same pattern as CaseStudyImage.
    """

    MEDIA_TYPE_IMAGE = "image"
    MEDIA_TYPE_VIDEO = "video"
    MEDIA_TYPE_CHOICES = [
        (MEDIA_TYPE_IMAGE, "Image"),
        (MEDIA_TYPE_VIDEO, "Video"),
    ]

    event = models.ForeignKey(
        UpcomingEvent,
        related_name="media",
        on_delete=models.CASCADE,
        help_text="The event this media item belongs to.",
    )

    media_type = models.CharField(
        max_length=10,
        choices=MEDIA_TYPE_CHOICES,
        default=MEDIA_TYPE_IMAGE,
        help_text="Select Image or Video.",
    )

    # Used for images
    image = models.ImageField(
        upload_to="events/gallery/",
        blank=True,
        null=True,
        help_text="Upload an event photo (JPEG/PNG recommended).",
    )

    # Used for videos
    video_file = models.FileField(
        upload_to="events/videos/",
        blank=True,
        null=True,
        validators=[
            FileExtensionValidator(
                allowed_extensions=["mp4", "webm", "mov", "avi"]
            )
        ],
        help_text="Upload an event video (MP4/WebM recommended, max ~50 MB).",
    )

    caption = models.CharField(
        max_length=250,
        blank=True,
        help_text="Optional caption displayed beneath the media item.",
    )

    display_order = models.PositiveIntegerField(
        default=0,
        help_text="Lower numbers appear first in the gallery.",
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["display_order", "created_at"]
        verbose_name = "Event Media"
        verbose_name_plural = "Event Media"
        indexes = [
            models.Index(
                fields=["event", "media_type", "display_order"],
                name="banners_em_event__idx",
            ),
        ]

    def __str__(self):
        return (
            f"{self.get_media_type_display()} for "
            f"'{self.event.name}' (order {self.display_order})"
        )


# ============================================================
# PROXYNET GROUP MODELS
# ============================================================

# ============================================================
# THINGS WE DO
# ============================================================

class ThingWeDo(PublishableMixin):
    """
    Represents a service/offering in the "What We Do" section.
    """

    entity = models.ForeignKey(
        Entity,
        related_name="things_we_do",
        on_delete=models.CASCADE,
        help_text="Entity this service belongs to.",
    )

    title = models.CharField(
        max_length=200,
        help_text="Title of the service (e.g., 'LFD & Smart Signage').",
    )

    description = models.TextField(
        blank=True,
        help_text="Description of the service.",
    )

    full_description = models.TextField(
        blank=True,
        help_text="Full/expanded description shown when the user clicks the card.",
        verbose_name="Full Description",
    )

    image = models.ImageField(
        upload_to="things_we_do/",
        blank=True,
        null=True,
        help_text="Optional image for this service.",
    )

    display_order = models.PositiveIntegerField(
        default=0,
        help_text="Lower numbers appear first.",
    )

    class Meta:
        ordering = ["display_order", "-created_at"]
        verbose_name = "Thing We Do"
        verbose_name_plural = "Things We Do"

        indexes = [
            models.Index(
                fields=["entity", "is_active", "display_order"]
            ),
        ]

    def __str__(self):
        return f"{self.title} - {self.entity.name}"


# ============================================================
# CYBERSECURITY SOLUTION
# ============================================================

class CybersecuritySolution(PublishableMixin):
    """
    Represents a cybersecurity solution card.
    """

    entity = models.ForeignKey(
        Entity,
        related_name="cybersecurity_solutions",
        on_delete=models.CASCADE,
        help_text="Entity this cybersecurity solution belongs to.",
    )

    title = models.CharField(
        max_length=200,
        help_text="Solution/category title (e.g., 'Identity & Authentication').",
    )

    product_name = models.CharField(
        max_length=200,
        blank=True,
        help_text="Product or vendor name (e.g., 'V-Key'). Displayed below the category title.",
        verbose_name="Product Name",
    )

    description = models.TextField(
        blank=True,
        help_text="Description of the cybersecurity solution.",
    )

    image = models.ImageField(
        upload_to="cybersecurity_solutions/",
        help_text="MAIN PRODUCT IMAGE — the large image shown in the solution card/slide.",
    )

    product_logo = models.ImageField(
        upload_to="cybersecurity_solutions/logos/",
        blank=True,
        null=True,
        help_text="PRODUCT/VENDOR LOGO — the small logo displayed below the product description (e.g., V-Key logo). Different from the main image above.",
        verbose_name="Product/Vendor Logo",
    )

    display_order = models.PositiveIntegerField(
        default=0,
        help_text="Lower numbers appear first.",
    )

    class Meta:
        ordering = ["display_order", "-created_at"]
        verbose_name = "Cybersecurity Solution"
        verbose_name_plural = "Cybersecurity Solutions"

        indexes = [
            models.Index(
                fields=["entity", "is_active", "display_order"]
            ),
        ]

    def __str__(self):
        return f"{self.title} - {self.entity.name}"


# ============================================================
# PROJECT (WORK WE ARE PROUD OF)
# ============================================================

class Project(PublishableMixin):
    """
    Represents a featured project in the "Work We're Proud Of" section.
    """

    entity = models.ForeignKey(
        Entity,
        related_name="projects",
        on_delete=models.CASCADE,
        help_text="Entity this project belongs to.",
    )

    title = models.CharField(
        max_length=200,
        help_text="Project title (e.g., 'Videowall & NOC').",
    )

    category = models.CharField(
        max_length=200,
        blank=True,
        help_text="Project category or industry (e.g., 'NOC', 'Cybersecurity').",
    )

    description = models.TextField(
        blank=True,
        help_text="Project description.",
    )

    more_description = models.TextField(
        blank=True,
        help_text="More Description About the Project (e.g., 'Deployed a 15-screen NOC enabling real-time monitoring.').",
        verbose_name="More Description",
    )

    image = models.ImageField(
        upload_to="projects/",
        help_text="Main project image.",
    )

    project_url = models.URLField(
        blank=True,
        help_text="Optional URL for the project case study.",
    )

    display_order = models.PositiveIntegerField(
        default=0,
        help_text="Lower numbers appear first.",
    )

    class Meta:
        ordering = ["display_order", "-created_at"]
        verbose_name = "Project"
        verbose_name_plural = "Work We Are Proud Of"

        indexes = [
            models.Index(
                fields=["entity", "is_active", "display_order"]
            ),
        ]

    def __str__(self):
        return f"{self.title} - {self.entity.name}"


# ============================================================
# BLOG POST
# ============================================================

class BlogPost(PublishableMixin):
    """
    Represents a blog post in the "Latest Insights" section.
    """

    entity = models.ForeignKey(
        Entity,
        related_name="blog_posts",
        on_delete=models.CASCADE,
        help_text="Entity this blog post belongs to.",
    )

    title = models.CharField(
        max_length=250,
        help_text="Blog post title.",
    )

    slug = models.SlugField(
        max_length=250,
        unique=True,
        blank=True,
        help_text="URL-friendly version of the blog title.",
    )

    image = models.ImageField(
        upload_to="blog_posts/",
        blank=True,
        null=True,
        help_text="Featured image for the blog post.",
    )

    excerpt = models.TextField(
        blank=True,
        help_text="Short preview text shown on the homepage.",
    )

    content = models.TextField(
        help_text="Full blog post content.",
    )

    published_at = models.DateTimeField(
        blank=True,
        null=True,
        help_text="Date and time the blog post was published.",
    )

    display_order = models.PositiveIntegerField(
        default=0,
        help_text="Optional homepage display order.",
    )

    class Meta:
        ordering = ["-published_at", "-created_at"]
        verbose_name = "Blog Post"
        verbose_name_plural = "Blog Posts"

        indexes = [
            models.Index(
                fields=["entity", "is_active", "published_at"]
            ),
        ]

    def __str__(self):
        return f"{self.title} - {self.entity.name}"

    def save(self, *args, **kwargs):
        if not self.slug:
            from django.utils.text import slugify
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        """Returns the URL for the blog detail page."""
        from django.urls import reverse
        return reverse('banners:blog-detail', kwargs={'slug': self.slug})


# ============================================================
# RECOGNITION (AWARDS & CERTIFICATES)
# ============================================================

class Recognition(PublishableMixin):
    """
    Represents an award, certificate, or recognition on the About page.
    """

    entity = models.ForeignKey(
        Entity,
        related_name="recognitions",
        on_delete=models.CASCADE,
        help_text="Entity this recognition belongs to.",
    )

    title = models.CharField(
        max_length=200,
        help_text="Name of the award or certificate (e.g., 'ISO 27001 Certified').",
    )

    issuing_organization = models.CharField(
        max_length=200,
        blank=True,
        help_text="Organization that issued the award or certificate.",
    )

    description = models.TextField(
        blank=True,
        help_text="Optional description or context for this recognition.",
    )

    image = models.ImageField(
        upload_to="recognitions/",
        blank=True,
        null=True,
        help_text="Certificate, badge, or logo image.",
    )

    year = models.CharField(
        max_length=10,
        blank=True,
        help_text="Year received (e.g., '2024'). Optional.",
    )

    display_order = models.PositiveIntegerField(
        default=0,
        help_text="Lower numbers appear first.",
    )

    class Meta:
        ordering = ["display_order", "-created_at"]
        verbose_name = "Recognition"
        verbose_name_plural = "Recognitions"
        indexes = [
            models.Index(
                fields=["entity", "is_active", "display_order"],
                name="banners_rec_entity__a1b2c3_idx",
            ),
        ]

    def __str__(self):
        return f"{self.title} - {self.entity.name}"


# ============================================================
# TEAM CERTIFICATE
# ============================================================

class TeamCertificate(PublishableMixin):
    """
    Represents a team-level technical certification on the About page.
    """

    entity = models.ForeignKey(
        Entity,
        related_name="team_certificates",
        on_delete=models.CASCADE,
        help_text="Entity this team certificate belongs to.",
    )

    title = models.CharField(
        max_length=200,
        help_text="Name of the certification (e.g., 'Cisco CCNP').",
    )

    issuing_organization = models.CharField(
        max_length=200,
        blank=True,
        help_text="Organization that issued the certification (e.g., 'Cisco', 'Microsoft').",
    )

    description = models.TextField(
        blank=True,
        help_text="Optional description of the certification and its relevance.",
    )

    image = models.ImageField(
        upload_to="team_certificates/",
        blank=True,
        null=True,
        help_text="Certification logo or badge image.",
    )

    year = models.CharField(
        max_length=10,
        blank=True,
        help_text="Year the certification was achieved (e.g., '2024'). Optional.",
    )

    display_order = models.PositiveIntegerField(
        default=0,
        help_text="Lower numbers appear first.",
    )

    class Meta:
        ordering = ["display_order", "-created_at"]
        verbose_name = "Team Certificate"
        verbose_name_plural = "Team Certificates"
        indexes = [
            models.Index(
                fields=["entity", "is_active", "display_order"],
                name="banners_tc_entity__d4e5f6_idx",
            ),
        ]

    def __str__(self):
        return f"{self.title} - {self.entity.name}"


# ============================================================
# CASE STUDY
# ============================================================

class CaseStudy(PublishableMixin):
    """
    A fully dynamic Case Study managed entirely from Django Admin.
    Solution, industry, and country are plain text fields on the model —
    no separate lookup tables required.  Filter options are derived
    dynamically from active records at query time.
    """

    entity = models.ForeignKey(
        Entity,
        related_name="case_studies",
        on_delete=models.CASCADE,
        help_text="Entity this case study belongs to.",
    )

    title = models.CharField(
        max_length=250,
        help_text="Case study title (e.g., 'Access Bank Videowall — Ikota Branch').",
    )

    slug = models.SlugField(
        max_length=250,
        unique=True,
        blank=True,
        help_text="URL-friendly identifier. Auto-generated from title if left blank.",
    )

    client = models.CharField(
        max_length=200,
        help_text="Client / organisation name (e.g., 'Access Bank').",
    )

    solution = models.CharField(
        max_length=200,
        help_text="Solution delivered (e.g., 'Videowall & Digital Signage').",
    )

    industry = models.CharField(
        max_length=200,
        help_text="Client industry (e.g., 'Financial Services').",
    )

    country = models.CharField(
        max_length=100,
        help_text="Country where the project was delivered (e.g., 'Nigeria').",
    )

    short_description = models.TextField(
        blank=True,
        help_text="Brief summary shown on the listing card.",
    )

    featured_image = models.ImageField(
        upload_to="case_studies/featured/",
        blank=True,
        null=True,
        help_text="Main hero image for the case study.",
    )

    # ── Full case-study content ──────────────────────────────
    client_overview = models.TextField(
        blank=True,
        help_text="Background information about the client.",
        verbose_name="Client Overview",
    )

    challenge = models.TextField(
        blank=True,
        help_text="The challenge or problem the client faced.",
    )

    solution_details = models.TextField(
        blank=True,
        help_text="Detailed description of the solution delivered.",
    )

    implementation = models.TextField(
        blank=True,
        help_text="How the solution was implemented.",
    )

    # ── Publishing ───────────────────────────────────────────
    display_order = models.PositiveIntegerField(
        default=0,
        help_text="Lower numbers appear first in the listing.",
    )

    class Meta:
        ordering = ["display_order", "-created_at"]
        verbose_name = "Case Study"
        verbose_name_plural = "Case Studies"
        indexes = [
            models.Index(
                fields=["is_active", "display_order"],
                name="banners_cs_active__order_idx",
            ),
        ]

    def __str__(self):
        return f"{self.title} — {self.client}"

    def save(self, *args, **kwargs):
        if not self.slug:
            from django.utils.text import slugify
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)


# ============================================================
# CASE STUDY IMAGE
# ============================================================

class CaseStudyImage(models.Model):
    """
    Additional gallery images for a single CaseStudy.
    Deleting a CaseStudy cascades and removes all its images.
    """

    case_study = models.ForeignKey(
        CaseStudy,
        related_name="images",
        on_delete=models.CASCADE,
        help_text="The case study this image belongs to.",
    )

    image = models.ImageField(
        upload_to="case_studies/gallery/",
        help_text="Gallery image for this case study.",
    )

    caption = models.CharField(
        max_length=250,
        blank=True,
        help_text="Optional caption displayed beneath the image.",
    )

    display_order = models.PositiveIntegerField(
        default=0,
        help_text="Lower numbers appear first.",
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["display_order", "created_at"]
        verbose_name = "Case Study Image"
        verbose_name_plural = "Case Study Images"

    def __str__(self):
        return f"Image for '{self.case_study.title}' (order {self.display_order})"

# ============================================================
# CASE STUDY TECHNOLOGY
# ============================================================

class CaseStudyTechnology(models.Model):
    """
    A single technology item used in a Case Study.
    One CaseStudy → many CaseStudyTechnology records.
    """

    case_study = models.ForeignKey(
        CaseStudy,
        related_name="technologies",
        on_delete=models.CASCADE,
        help_text="The case study this technology belongs to.",
    )

    name = models.CharField(
        max_length=200,
        help_text="Technology name (e.g., 'Samsung LED Display', 'Taurus TU15').",
    )

    display_order = models.PositiveIntegerField(
        default=0,
        help_text="Lower numbers appear first.",
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["display_order", "created_at"]
        verbose_name = "Technology Used"
        verbose_name_plural = "Technologies Used"

    def __str__(self):
        return f"{self.name} — {self.case_study.title}"


# ============================================================
# CASE STUDY RESULT & ROI
# ============================================================

class CaseStudyResultROI(models.Model):
    """
    A single Result & ROI item for a Case Study.
    One CaseStudy → many CaseStudyResultROI records.
    """

    case_study = models.ForeignKey(
        CaseStudy,
        related_name="result_roi_items",
        on_delete=models.CASCADE,
        help_text="The case study this result belongs to.",
    )

    content = models.TextField(
        help_text="Result or ROI statement (e.g., 'Improved visual communication').",
    )

    display_order = models.PositiveIntegerField(
        default=0,
        help_text="Lower numbers appear first.",
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["display_order", "created_at"]
        verbose_name = "Result & ROI Item"
        verbose_name_plural = "Result & ROI Items"

    def __str__(self):
        return f"Result for '{self.case_study.title}' (order {self.display_order})"


# ============================================================
# TECHNOLOGY PARTNER
# ============================================================

class TechnologyPartner(models.Model):
    """
    A technology partner/vendor displayed in the
    "Our Technology Partners" section.
    """

    name = models.CharField(
        max_length=200,
        help_text="Partner/vendor name (e.g., 'Fortinet', 'V-Key').",
    )

    entity = models.ForeignKey(
        Entity,
        related_name="technology_partners",
        on_delete=models.CASCADE,
        help_text="Entity this technology partner belongs to.",
    )

    description = models.TextField(
        blank=True,
        help_text="Short description of the technology partner and their offering.",
    )

    logo = models.ImageField(
        upload_to="partners/",
        help_text="Partner/vendor logo image.",
    )

    display_order = models.PositiveIntegerField(
        default=0,
        help_text="Lower numbers appear first.",
    )

    is_active = models.BooleanField(
        default=True,
        help_text="Uncheck to hide this partner without deleting it.",
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["display_order", "created_at"]
        verbose_name = "Technology Partner"
        verbose_name_plural = "Technology Partners"

    def __str__(self):
        return f"{self.name} ({self.entity.name})"
