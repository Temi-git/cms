from .promall_category_gif_storage import PromallCategoryGIFStorage
from django.core.exceptions import ValidationError
from django.core.validators import FileExtensionValidator
from django.db import models
from django.utils import timezone


# ============================================================
# ENTITY
# ============================================================

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
            self.flash_sale_count +
            self.today_deal_count +
            self.affiliate_banner_count +
            self.event_count +
            self.things_we_do_count +
            self.cybersecurity_solutions_count +
            self.projects_count +
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

    entity = models.ForeignKey(
        Entity,
        on_delete=models.CASCADE,
        related_name="banners",
        help_text="Select one or more entities this banner belongs to.",
        verbose_name="Entity",
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
        help_text="Recommended size: 1920 x 650 px. Upload an image (if media type is 'Image') max size 2mb.",
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
     return self.title



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
        return f"Flash Sale #{self.pk} - {self.entity.name}"


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

    buy_now_url = models.URLField(
        max_length=500,
        help_text="Full link the 'BUY NOW' button opens, e.g. https://www.promallshop.com/product/Yealink-VP59-Flagship-Smart-Video-IP-Phone-1043.html",
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
        entity_name = self.entity.name if self.entity_id else "No Entity"
        return f"{self.title} - {entity_name}"


# ============================================================
# AFFILIATE BANNER
# ============================================================

class AffiliateBanner(PublishableMixin):
    PLACEMENT_CHOICES = [
        ("top", "Top"),
        ("program", "Program"),
        ("below_categories", "Below Categories"),
        ("flash_side", "Flash Side"),
        ("below_flash", "Below Flash"),
    ]

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
        help_text="Image dimensions (W × H)  Hero banner 1234 × 681 px  ,Top affiliate GIF 1145 × 60 px  ,Below-categories affiliate GIF 800 × 114 px, Flash side 1200 x 240 px, ",
    )
    placement = models.CharField(
        max_length=30,
        choices=PLACEMENT_CHOICES,
        blank=True,
        default="",
        db_index=True,
        help_text="Choose where this banner appears. Only Program uses a destination URL.",
    )
    affiliate_url = models.URLField(
        blank=True,
        help_text="Required for Program placement only.",
    )
    display_order = models.PositiveIntegerField(
        default=0,
        help_text="Lower numbers appear first.",
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

    def clean(self):
        super().clean()

        if self.placement:
            duplicates = AffiliateBanner.objects.filter(
                entity=self.entity,
                placement=self.placement,
            )
            if self.pk:
                duplicates = duplicates.exclude(pk=self.pk)
            if duplicates.exists():
                raise ValidationError({
                    "placement": "Only one affiliate banner is allowed per entity for each placement."
                })

        if self.placement == "program" and not self.affiliate_url:
            raise ValidationError(
                {"affiliate_url": "A destination URL is required for Program placement."}
            )

        if self.placement != "program":
            self.affiliate_url = ""
    def __str__(self):
        return f"{self.title} - {self.entity.name}"
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
    One UpcomingEvent Ã¢â€ â€™ many EventMedia records.
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
        help_text="Optional image for this service.width=56px height=56px",
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
        help_text='MAIN PRODUCT IMAGE  the large image shown in the solution slide. size width=1244px, height=829px',
    )

    product_logo = models.ImageField(
        upload_to="cybersecurity_solutions/logos/",
        blank=True,
        null=True,
        help_text='PRODUCT/VENDOR LOGO the small logo displayed below the product description (e.g., V-Key logo). size width=1244px, height=373px',
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
        help_text="Main project image 604px X 377px",
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
        help_text="Certificate, badge, or logo image. size width=573.91 height=87.99 max=1mb",
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
        help_text="Certification logo or badge image",
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
    Solution, industry, and country are plain text fields on the model Ã¢â‚¬â€
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
        help_text="Case study title (e.g., 'Access Bank Videowall ??? Ikota Branch').",
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
        help_text="Main hero image for the case study. size width=1244px, height=698px",
    )

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

    # Ã¢â€â‚¬Ã¢â€â‚¬ Publishing Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬
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
        return f"{self.title} Ã¢â‚¬â€ {self.client}"

    def save(self, *args, **kwargs):
        if not self.slug:
            from django.utils.text import slugify
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)


# ============================================================
# CASE STUDY IMAGE
# ============================================================

def validate_case_study_video_size(file):
    max_size = 30 * 1024 * 1024
    if file.size > max_size:
        raise ValidationError("Each case study video must be 30 MB or smaller.")


class CaseStudyImage(models.Model):
    """
    Gallery media for a single CaseStudy. Existing image entries remain supported.
    """

    case_study = models.ForeignKey(
        CaseStudy,
        related_name="images",
        on_delete=models.CASCADE,
        help_text="The case study this media belongs to.",
    )

    image = models.ImageField(
        upload_to="case_studies/gallery/",
        blank=True,
        null=True,
        help_text="Upload an image, or leave empty when uploading a video.",
    )

    video = models.FileField(
        upload_to="case_studies/gallery/videos/",
        blank=True,
        null=True,
        validators=[
            FileExtensionValidator(allowed_extensions=["mp4", "webm", "mov"]),
            validate_case_study_video_size,
        ],
        help_text="Optional video (MP4, WebM or MOV). Maximum size: 30 MB per video.",
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
    One CaseStudy Ã¢â€ â€™ many CaseStudyTechnology records.
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
        return f"{self.name} Ã¢â‚¬â€ {self.case_study.title}"


# ============================================================
# CASE STUDY RESULT & ROI
# ============================================================

class CaseStudyResultROI(models.Model):
    """
    A single Result & ROI item for a Case Study.
    One CaseStudy Ã¢â€ â€™ many CaseStudyResultROI records.
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
        help_text="Partner/vendor logo image. width=499.98px height=196px",
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


# ============================================================
# PROMALLSHOP CATALOG
# ============================================================


class PromallCategory(models.Model):
    """
    A product category synced from the Promall API or created by admin.
    """

    external_id = models.CharField(
        max_length=100,
        unique=True,
        null=True,
        blank=True,
        db_index=True,
        help_text='External category ID from the Promall API. Null for admin-created categories.',
    )

    name = models.CharField(
        max_length=300,
        help_text='Category display name.',
    )

    slug = models.SlugField(
        max_length=300,
        db_index=True,
        help_text='URL-friendly identifier. Not globally unique ??? the same slug may appear in multiple categories.',
    )

    description = models.TextField(
        blank=True,
        help_text='Rich text HTML category description. # TODO: replace with CKEditorField once django-ckeditor-5 is installed.',
    )

    icon = models.ImageField(
        upload_to='promall/categories/',
        blank=True,
        null=True,
        help_text='Admin-uploaded icon only. Synced categories do not use this field. Recommended size: TBC.',
    )

    display_order = models.PositiveIntegerField(
        default=0,
        help_text='Lower numbers appear first.',
    )

    is_active = models.BooleanField(
        default=True,
        help_text='Uncheck to hide this category without deleting it.',
    )

    entity = models.ForeignKey(
        Entity,
        on_delete=models.CASCADE,
        related_name='promall_categories',
        help_text='Must be the Promallshop entity.',
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['display_order', 'name']
        verbose_name = 'Promall Category'
        verbose_name_plural = 'Promall Categories'

    def __str__(self):
        return self.name


class PromallCategoryFAQ(models.Model):
    """
    A FAQ entry belonging to a PromallCategory.
    """

    category = models.ForeignKey(
        PromallCategory,
        related_name='faqs',
        on_delete=models.CASCADE,
        help_text='Category this FAQ belongs to.',
    )

    question = models.CharField(
        max_length=500,
        help_text='FAQ question text.',
    )

    answer = models.TextField(
        help_text='Rich text HTML answer. # TODO: replace with CKEditorField once django-ckeditor-5 is installed.',
    )

    display_order = models.PositiveIntegerField(
        default=0,
        help_text='Lower numbers appear first.',
    )

    is_active = models.BooleanField(
        default=True,
        help_text='Uncheck to hide this FAQ.',
    )

    entity = models.ForeignKey(
        Entity,
        on_delete=models.CASCADE,
        related_name='promall_category_faqs',
        help_text='Must be the Promallshop entity.',
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['display_order', 'created_at']
        verbose_name = 'Promall Category FAQ'

    def __str__(self):
        return f'{self.question[:80]} ({self.category.name})'


class PromallSubcategory(models.Model):
    """
    A product subcategory synced from the Promall API or created by admin.
    """

    external_id = models.CharField(
        max_length=100,
        unique=True,
        null=True,
        blank=True,
        db_index=True,
        help_text='External subcategory ID from the Promall API. Null for admin-created subcategories.',
    )

    category = models.ForeignKey(
        PromallCategory,
        related_name='subcategories',
        on_delete=models.CASCADE,
        help_text='Parent category for this subcategory.',
    )

    name = models.CharField(
        max_length=300,
        help_text='Subcategory display name.',
    )

    slug = models.SlugField(
        max_length=300,
        db_index=True,
        help_text='URL-friendly identifier. Unique within its parent category only.',
    )

    display_order = models.PositiveIntegerField(
        default=0,
        help_text='Lower numbers appear first.',
    )

    is_active = models.BooleanField(
        default=True,
        help_text='Uncheck to hide this subcategory.',
    )

    entity = models.ForeignKey(
        Entity,
        on_delete=models.CASCADE,
        related_name='promall_subcategories',
        help_text='Must be the Promallshop entity.',
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['display_order', 'name']
        unique_together = [('category', 'slug')]
        verbose_name = 'Promall Subcategory'
        verbose_name_plural = 'Promall Subcategories'

    def __str__(self):
        return f'{self.category.name} > {self.name}'


class PromallProduct(models.Model):
    """
    A product synced from the Promall API or created by admin.
    """

    external_id = models.CharField(
        max_length=100,
        unique=True,
        null=True,
        blank=True,
        db_index=True,
        help_text='External product ID from the Promall API. Null for admin-created products.',
    )

    category = models.ForeignKey(
        PromallCategory,
        related_name='products',
        on_delete=models.CASCADE,
        help_text='Category this product belongs to.',
    )

    subcategory = models.ForeignKey(
        PromallSubcategory,
        related_name='products',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        help_text='Subcategory this product belongs to. Optional.',
    )

    name = models.CharField(
        max_length=500,
        help_text='Product display name.',
    )

    slug = models.SlugField(
        max_length=500,
        db_index=True,
        help_text='URL-friendly product identifier.',
    )

    short_description = models.TextField(
        blank=True,
        help_text='Short product description shown on listing cards.',
    )

    description = models.TextField(
        blank=True,
        help_text='Rich text HTML full product description. # TODO: replace with CKEditorField once django-ckeditor-5 is installed.',
    )

    model_number = models.CharField(
        max_length=200,
        blank=True,
        help_text='Product model number.',
    )

    part_number = models.CharField(
        max_length=200,
        blank=True,
        help_text='Product part number.',
    )

    warranty = models.CharField(
        max_length=200,
        blank=True,
        help_text='Warranty information.',
    )

    video_url = models.URLField(
        blank=True,
        help_text='URL of a product demo or overview video.',
    )

    price = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        null=True,
        blank=True,
        help_text='Retail price. Refreshed on every sync.',
    )

    end_user_price = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        null=True,
        blank=True,
        help_text='End-user price. Refreshed on every sync.',
    )

    discount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        help_text='Discount value. Refreshed on every sync.',
    )

    quantity = models.IntegerField(
        null=True,
        blank=True,
        help_text='Stock quantity. Refreshed on every sync.',
    )

    image = models.ImageField(
        upload_to='promall/products/',
        blank=True,
        null=True,
        help_text='Admin-uploaded image only. For synced products the image comes from external_image_paths. Recommended size: TBC.',
    )

    external_image_paths = models.TextField(
        blank=True,
        help_text='Comma-separated relative image paths received from the Promall API. Read-only ??? never edit manually.',
    )

    is_hot = models.BooleanField(
        default=False,
        help_text='Mark as Hot/Flash-sale product. Set automatically on first sync (tag=="hot"); editable by admin thereafter.',
    )

    is_special = models.BooleanField(
        default=False,
        help_text='Mark as Special/Featured product. Set automatically on first sync (tag=="special"); editable by admin thereafter.',
    )

    is_active = models.BooleanField(
        default=True,
        help_text='Uncheck to hide this product. Set to False automatically if show_on_promall != "yes" in the API.',
    )

    display_order = models.PositiveIntegerField(
        default=0,
        help_text='Lower numbers appear first.',
    )

    alternative_product_ids = models.TextField(
        blank=True,
        help_text='JSON string of alternative product external IDs, e.g. ["123","456"]. From API, read-only.',
    )

    complementary_product_ids = models.TextField(
        blank=True,
        help_text='JSON string of complementary product external IDs. From API, read-only.',
    )

    meta_title = models.CharField(
        max_length=300,
        blank=True,
        help_text='SEO meta title. Parsed from SKU on first sync.',
    )

    meta_description = models.TextField(
        blank=True,
        help_text='SEO meta description. Parsed from SKU on first sync.',
    )

    keywords = models.TextField(
        blank=True,
        help_text='SEO keywords. Parsed from SKU on first sync.',
    )

    entity = models.ForeignKey(
        Entity,
        on_delete=models.CASCADE,
        related_name='promall_products',
        help_text='Must be the Promallshop entity.',
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['display_order', 'name']
        verbose_name = 'Promall Product'
        verbose_name_plural = 'Promall Products'

    def __str__(self):
        return f'{self.name} ({self.external_id or "admin-created"})'


class PromallProductFAQ(models.Model):
    """
    A FAQ entry belonging to a PromallProduct.
    """

    product = models.ForeignKey(
        PromallProduct,
        related_name='faqs',
        on_delete=models.CASCADE,
        help_text='Product this FAQ belongs to.',
    )

    question = models.CharField(
        max_length=500,
        help_text='FAQ question text.',
    )

    answer = models.TextField(
        help_text='Rich text HTML answer. # TODO: replace with CKEditorField once django-ckeditor-5 is installed.',
    )

    display_order = models.PositiveIntegerField(
        default=0,
        help_text='Lower numbers appear first.',
    )

    is_active = models.BooleanField(
        default=True,
        help_text='Uncheck to hide this FAQ.',
    )

    entity = models.ForeignKey(
        Entity,
        on_delete=models.CASCADE,
        related_name='promall_product_faqs',
        help_text='Must be the Promallshop entity.',
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['display_order', 'created_at']
        verbose_name = 'Promall Product FAQ'

    def __str__(self):
        return f'{self.question[:80]} ({self.product.name})'


# ============================================================
# PROMALL SITE CONTENT
# ============================================================

class PromallBanner(models.Model):
    entity = models.ForeignKey(
        Entity,
        related_name="promall_banners",
        on_delete=models.CASCADE,
        help_text="Must be the Promallshop entity.",
    )
    title = models.CharField(
        max_length=300,
        help_text="Banner headline text displayed over the image.",
    )
    description = models.TextField(
        blank=True,
        help_text="Optional supporting text shown beneath the title.",
    )
    image = models.ImageField(
        upload_to="promall/banners/",
        help_text="Main banner image. 863x442px max 1mb",
    )
    display_order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["display_order", "-created_at"]
        verbose_name = "Promall Banner"
        verbose_name_plural = "Promall Banners"

    def __str__(self):
        return self.title


class PromallEventType(models.Model):
    entity = models.ForeignKey(
        Entity,
        related_name="promall_event_types",
        on_delete=models.CASCADE,
        help_text="Must be the Promallshop entity.",
    )
    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, db_index=True)
    display_order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["display_order", "name"]
        unique_together = [("entity", "slug")]
        verbose_name = "Promall Event Type"
        verbose_name_plural = "Promall Event Types"

    def __str__(self):
        return self.name


class PromallEvent(models.Model):
    entity = models.ForeignKey(
        Entity,
        related_name="promall_events",
        on_delete=models.CASCADE,
        help_text="Must be the Promallshop entity.",
    )
    event_type = models.ForeignKey(
        PromallEventType,
        related_name="events",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        help_text="Event category, such as Webinars or Training.",
    )
    name = models.CharField(max_length=300)
    description = models.TextField(blank=True)
    event_datetime = models.DateTimeField()
    location = models.CharField(max_length=300, blank=True)
    image = models.ImageField(
        upload_to="promall/events/",
        null=True,
        blank=True,
        help_text="Recommended size: 800 x 500 px (8:5 ratio). Upload an event or promotion image in JPEG, PNG, or WebP format.",
    )
    registration_link = models.URLField(blank=True)
    is_active = models.BooleanField(default=True)
    display_order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["event_datetime", "display_order"]
        verbose_name = "Promall Event"
        verbose_name_plural = "Promall Events"

    def __str__(self):
        return self.name


# ============================================================
# PROMALLSHOP CATEGORY GIFS
# ============================================================

def promall_category_gif_upload_path(instance, filename):
    return f"promall/category-gifs/{instance.category_id}.gif"


class PromallCategoryGIF(models.Model):
    category_id = models.PositiveIntegerField(
        unique=True,
        help_text="Category ID from the live Promall API.",
    )
    category_name = models.CharField(max_length=255)
    gif = models.FileField(
        upload_to=promall_category_gif_upload_path,
        storage=PromallCategoryGIFStorage(),
        help_text="Upload an optimized animated GIF for the PromallShop category display. Recommended size: 600 x 600 px (square).",
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Promall Category GIF"
        verbose_name_plural = "Promall Category GIFs"
        ordering = ["category_name"]

    def __str__(self):
        return f"{self.category_name} (ID {self.category_id})"



# ============================================================
# PROMALLSHOP SECTION 1
# One section per website entity
# ============================================================

class PromallSection1(models.Model):
    entity = models.OneToOneField(
        Entity,
        related_name="promall_section1",
        on_delete=models.CASCADE,
        help_text="Website that owns Section 1.",
    )
    title = models.CharField(max_length=300)
    subtitle = models.CharField(max_length=500, blank=True)
    description = models.TextField(blank=True)
    link = models.URLField(blank=True, help_text="Optional destination URL for Section 1.")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Promall Section 1"
        verbose_name_plural = "Promall Section 1"

    def __str__(self):
        return f"{self.entity.name} - Section 1"


# ============================================================
# PROMALLSHOP WEBSITE FAQ (separate from product/category FAQs)
# ============================================================

class PromallWebsiteFAQ(models.Model):
    entity = models.ForeignKey(
        Entity,
        related_name="promall_website_faqs",
        on_delete=models.CASCADE,
    )
    question = models.CharField(max_length=500)
    answer = models.TextField()
    display_order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["display_order", "id"]
        verbose_name = "Promall Website FAQ"
        verbose_name_plural = "Promall Website FAQs"

    def __str__(self):
        return self.question



# ============================================================
# PROMALLSHOP SECTION 1
# One section per website entity
# ============================================================

class PromallSection2(models.Model):
    entity = models.OneToOneField(
        Entity,
        related_name="promall_section2",
        on_delete=models.CASCADE,
        help_text="Website that owns Section 2.",
    )
    title = models.CharField(max_length=300)
    subtitle = models.CharField(max_length=500, blank=True)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Promall Section 2"
        verbose_name_plural = "Promall Section 2"

    def __str__(self):
        return f"{self.entity.name} - Section 2"


# ============================================================
# PROMALLSHOP SECTION 2 SUBSECTIONS
# Multiple subsections per Section 2
# ============================================================

class PromallSubsection(models.Model):
    section = models.ForeignKey(
        PromallSection2,
        related_name="subsections",
        on_delete=models.CASCADE,
    )
    title = models.CharField(max_length=300)
    description = models.TextField(
        help_text="Enter the full subsection content. Long descriptions are supported.",
    )
    display_order = models.PositiveIntegerField(
        default=0,
        help_text="Lower numbers appear first.",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["display_order", "id"]
        verbose_name = "Promall Subsection"
        verbose_name_plural = "Promall Subsections"

    def __str__(self):
        return self.title



# ============================================================
# CASDNET WEBSITE CATEGORIES
# ============================================================

class CasdnetCategory(models.Model):
    entity = models.ForeignKey("Entity", on_delete=models.CASCADE, related_name="casdnet_categories")
    title = models.CharField(max_length=300)
    image = models.ImageField(upload_to="casdnet/categories/")
    link = models.URLField(max_length=1000)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["id"]
        verbose_name = "CASDNET Category"
        verbose_name_plural = "CASDNET Categories"

    def __str__(self):
        return self.title


# ============================================================
# CASDNET WEBSITE BANNERS
# ============================================================

class CasdnetBanner(models.Model):
    entity = models.ForeignKey("Entity", on_delete=models.CASCADE, related_name="casdnet_banners")
    title = models.CharField(max_length=300)
    subtitle = models.CharField(max_length=500, blank=True)
    link = models.URLField(max_length=1000)
    image = models.ImageField(upload_to="casdnet/banners/")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["id"]
        verbose_name = "CASDNET Banner"
        verbose_name_plural = "CASDNET Banners"

    def __str__(self):
        return self.title




