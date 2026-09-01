from django.db import models
from django.utils.text import slugify
from django.conf import settings
from PIL import Image


class Entity(models.Model):
    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True, blank=True)
    url = models.URLField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            base = slugify(self.name)
            slug = base
            counter = 1
            while Entity.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base}-{counter}"
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)


def _image_size_from_file(image_field):
    try:
        image_field.open()
        img = Image.open(image_field)
        return img.width, img.height
    except Exception:
        return None, None


class Banner(models.Model):
    entity = models.ForeignKey(Entity, on_delete=models.CASCADE, related_name='banners')
    title = models.CharField(max_length=255, blank=True, null=True)
    image = models.ImageField(upload_to='banners/')
    text = models.TextField(blank=True, null=True)
    link = models.URLField(blank=True, null=True)
    width = models.PositiveIntegerField(blank=True, null=True)
    height = models.PositiveIntegerField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        # Attempt to detect image size
        if self.image:
            w, h = _image_size_from_file(self.image)
            if w and h:
                self.width = w
                self.height = h

        creating = self._state.adding
        super().save(*args, **kwargs)

        # Optionally deactivate previous banners for this entity
        if getattr(settings, 'BANNERCONTROL_AUTO_DEACTIVATE_PREVIOUS', False) and self.is_active:
            Banner.objects.filter(entity=self.entity, is_active=True).exclude(pk=self.pk).update(is_active=False)

    def aspect_ratio(self):
        if self.width and self.height and self.height != 0:
            return round(self.width / self.height, 6)
        return None

    def __str__(self):
        return f"Banner {self.pk} for {self.entity}"
