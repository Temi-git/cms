from django import forms


class LiveCategoryForm(forms.Form):
    name = forms.CharField(
        label="Category Name",
        max_length=255,
        widget=forms.TextInput(attrs={"style": "width:100%;"}),
    )

    title = forms.CharField(
        label="SEO / Display Title",
        required=False,
        widget=forms.TextInput(attrs={"style": "width:100%;"}),
    )

    slug = forms.SlugField(
        label="Category Slug",
        required=False,
        widget=forms.TextInput(attrs={"style": "width:100%;"}),
    )

    description = forms.CharField(
        label="Category Description",
        required=False,
        widget=forms.Textarea(attrs={"rows": 8, "class": "rich-editor"}),
    )

    post = forms.CharField(
        label="Page Content",
        required=False,
        widget=forms.Textarea(attrs={"rows": 10, "class": "rich-editor"}),
    )

    faq = forms.CharField(
        label="FAQs",
        required=False,
        widget=forms.Textarea(attrs={"rows": 8, "class": "rich-editor"}),
    )

    priority = forms.IntegerField(
        label="Display Priority",
        required=False,
    )

    online_discount = forms.IntegerField(
        label="Online Discount (%)",
        required=False,
        min_value=0,
        max_value=100,
    )

    active = forms.TypedChoiceField(
        label="Category Status",
        choices=[
            (1, "Active"),
            (0, "Inactive"),
        ],
        coerce=int,
    )
