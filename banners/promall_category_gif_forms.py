from django import forms
from django.core.exceptions import ValidationError

from .models import PromallCategoryGIF
from .promall_live_taxonomy_api import fetch_live_categories


class PromallCategoryGIFForm(forms.ModelForm):
    category_id = forms.TypedChoiceField(
        label="Live Category",
        coerce=int,
        choices=[],
    )

    class Meta:
        model = PromallCategoryGIF
        fields = [
            "category_id",
            "gif",
            "is_active",
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        try:
            categories = fetch_live_categories()
        except Exception as exc:
            raise ValidationError(
                "Unable to load live categories. Please try again."
            ) from exc

        choices = [("", "Select a live category")]

        for category in categories:
            if category.get("id") is None or not category.get("name"):
                continue

            choices.append((
                int(category["id"]),
                f'{category["name"]} (ID {category["id"]})',
            ))

        self.fields["category_id"].choices = choices

        self.live_category_names = {
            int(category["id"]): str(category["name"])
            for category in categories
            if category.get("id") is not None and category.get("name")
        }

    def clean_gif(self):
        gif = self.cleaned_data.get("gif")

        if not gif:
            return gif

        # Existing files are already validated when uploaded.
        if not hasattr(gif, "read"):
            return gif

        position = gif.tell()

        try:
            gif.seek(0)
            header = gif.read(6)
        finally:
            gif.seek(position)

        if header not in (b"GIF87a", b"GIF89a"):
            raise ValidationError("Please upload a valid GIF file.")

        if not gif.name.lower().endswith(".gif"):
            raise ValidationError("File must have a .gif extension.")

        return gif

    def clean_category_id(self):
        category_id = self.cleaned_data["category_id"]

        existing = PromallCategoryGIF.objects.filter(
            category_id=category_id
        )

        if self.instance.pk:
            existing = existing.exclude(pk=self.instance.pk)

        if existing.exists():
            raise ValidationError(
                "This category already has a GIF. Edit the existing GIF instead."
            )

        return category_id

    def save(self, commit=True):
        instance = super().save(commit=False)

        instance.category_name = self.live_category_names[
            instance.category_id
        ]

        if commit:
            instance.save()
            self.save_m2m()

        return instance
