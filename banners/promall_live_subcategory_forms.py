from django import forms


class LiveSubcategoryForm(forms.Form):
    name = forms.CharField(
        label="Subcategory Name",
        max_length=255,
        widget=forms.TextInput(attrs={"style": "width:100%;max-width:650px;"}),
    )

    category_id = forms.ChoiceField(
        label="Parent Category",
        choices=[],
        help_text="Select the category this subcategory belongs to.",
    )

    slug = forms.SlugField(
        label="Subcategory Slug",
        required=False,
        widget=forms.TextInput(attrs={"style": "width:100%;max-width:650px;"}),
    )

    active = forms.TypedChoiceField(
        label="Subcategory Status",
        choices=[
            (1, "Active"),
            (0, "Inactive"),
        ],
        coerce=int,
    )

    online_discount = forms.IntegerField(
        label="Online Discount (%)",
        required=False,
        min_value=0,
        max_value=100,
    )

    commission_rate = forms.DecimalField(
        label="Commission Rate",
        required=False,
        max_digits=12,
        decimal_places=2,
    )

    cdn_only = forms.TypedChoiceField(
        label="CDN Only",
        choices=[
            ("", "Not set"),
            ("1", "Yes"),
            ("0", "No"),
        ],
        required=False,
        coerce=lambda value: None if value == "" else int(value),
    )

    company_id = forms.CharField(
        label="Company ID",
        required=False,
        max_length=32,
    )

    def __init__(self, *args, categories=None, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["category_id"].choices = [
            (str(category["id"]), category.get("name", "Unnamed Category"))
            for category in (categories or [])
        ]
