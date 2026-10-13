from .promall_live_taxonomy_api import fetch_live_categories, fetch_live_subcategories
from django.contrib import admin, messages
from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import render
from django.http import HttpResponseServerError

from .promall_live_api import fetch_live_products


@staff_member_required
def live_products_admin(request):
    try:
        products = fetch_live_products()
    except Exception as error:
        products = []
        messages.error(request, f"Could not fetch live products: {error}")

    query = request.GET.get("q", "").strip()

    if query:
        products = [
            product for product in products
            if query.lower() in str(product.get("name", "")).lower()
            or query.lower() in str(product.get("id", "")).lower()
            or query.lower() in str(product.get("sku", "")).lower()
        ]

    context = {
        **admin.site.each_context(request),
        "title": "Live Promall Products",
        "products": products,
        "query": query,
    }

    return render(request, "admin/promall_live/products.html", context)

from django import forms
from django.shortcuts import redirect
from django.urls import reverse
from django.views.decorators.http import require_http_methods
import requests


class LiveProductDescriptionForm(forms.Form):

    category_id = forms.ChoiceField(
        label="Product Category",
        choices=[],
    )

    subcategory_id = forms.ChoiceField(
        label="Product Subcategory",
        choices=[],
        required=False,
    )


    sku_meta_title = forms.CharField(
        required=False,
        label="SKU  Meta Title",
        widget=forms.TextInput(attrs={"style": "width:100%;"}),
    )
    sku_meta_description = forms.CharField(
        required=False,
        label="SKU  Meta Description",
        widget=forms.Textarea(attrs={"rows": 3, "style": "width:100%;"}),
    )
    sku_keywords = forms.CharField(
        required=False,
        label="SKU  SEO Keywords",
        widget=forms.Textarea(attrs={"rows": 4, "style": "width:100%;"}),
    )
    priority = forms.IntegerField(
        required=False,
        label="Product Priority",
    )
    video_url = forms.URLField(
        required=False,
        label="Product Video URL",
        widget=forms.URLInput(attrs={"style": "width:100%;"}),
    )
    tag = forms.ChoiceField(
        required=False,
        label="Product Tag",
        choices=[
            ("", "Normal Product"),
            ("hot", "Hot Product"),
            ("special", "Special Product"),
        ],
    )
    alternative_products = forms.MultipleChoiceField(
        required=False,
        label="Alternative Products",
        choices=[],
        widget=forms.SelectMultiple(attrs={"size": 10, "style": "width:100%;"}),
    )
    complementary_products = forms.MultipleChoiceField(
        required=False,
        label="Complementary Products",
        choices=[],
        widget=forms.SelectMultiple(attrs={"size": 10, "style": "width:100%;"}),
    )

    def __init__(self, *args, product_choices=None, categories=None, subcategories=None, **kwargs):
        super().__init__(*args, **kwargs)
        choices = product_choices or []
        self.fields["alternative_products"].choices = choices
        self.fields["complementary_products"].choices = choices

        self.fields["category_id"].choices = [
            (str(category["id"]), category.get("name", "Unnamed Category"))
            for category in (categories or [])
        ]

        self.fields["subcategory_id"].choices = [
            ("", "No Subcategory"),
        ] + [
            (
                str(subcategory["id"]),
                subcategory.get("name", "Unnamed Subcategory"),
            )
            for subcategory in (subcategories or [])
        ]

        self.subcategory_parent_map = {
            str(subcategory["id"]): str(subcategory.get("category_id") or "")
            for subcategory in (subcategories or [])
        }

        self.subcategory_options = [
            {
                "id": str(subcategory["id"]),
                "name": subcategory.get("name", "Unnamed Subcategory"),
                "category_id": str(subcategory.get("category_id") or ""),
            }
            for subcategory in (subcategories or [])
        ]

    def clean(self):
        cleaned_data = super().clean()

        category_id = cleaned_data.get("category_id")
        subcategory_id = cleaned_data.get("subcategory_id")

        if subcategory_id:
            parent_id = self.subcategory_parent_map.get(subcategory_id)

            if parent_id != category_id:
                self.add_error(
                    "subcategory_id",
                    "This subcategory does not belong to the selected category.",
                )

        return cleaned_data


    description = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={"rows": 12, "style": "width:100%;"}),
        label="Full description (HTML supported)",
    )
    short_description = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={"rows": 5, "style": "width:100%;"}),
    )
    more_information = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={"rows": 10, "style": "width:100%;"}),
        label="More information (HTML supported)",
    )


@staff_member_required
@require_http_methods(["GET", "POST"])
def edit_live_product(request, product_id):
    try:
        products = fetch_live_products()
        product = next(
            (p for p in products if str(p.get("id")) == str(product_id)),
            None,
        )
    except (requests.RequestException, ValueError) as error:
        messages.error(request, f"Could not fetch product: {error}")
        return redirect("promall_live_products")

    if product is None:
        messages.error(request, "Product not found in the live API.")
        return redirect("promall_live_products")

    try:
        categories = fetch_live_categories()
        subcategories = fetch_live_subcategories()
    except (requests.RequestException, ValueError) as error:
        messages.error(request, f"Could not fetch product categories: {error}")
        return redirect("promall_live_products")

    fields = (
        "description",
        "short_description",
        "more_information",
    )

    sku_parts = split_promall_sku(product.get("sku"))

    product_choices = sorted(
        [
            (str(p["id"]), p.get("name") or str(p["id"]))
            for p in products
            if str(p.get("id")) != str(product_id)
        ],
        key=lambda item: item[1].lower(),
    )

    if request.method == "POST":
        form = LiveProductDescriptionForm(
            request.POST,
            product_choices=product_choices,
            categories=categories,
            subcategories=subcategories,
        )

        if form.is_valid():
            payload = build_live_product_update_payload(
                product,
                form.cleaned_data,
            )

            if not payload:
                messages.info(request, "No product changes detected.")
            else:
                from .promall_live_api import update_live_product

                try:
                    update_live_product(product_id, payload)

                    refreshed_products = fetch_live_products()

                    updated = next(
                        (
                            p for p in refreshed_products
                            if str(p.get("id")) == str(product_id)
                        ),
                        None,
                    )

                    if updated is None:
                        messages.warning(
                            request,
                            "Update sent, but the product could not be reloaded."
                        )
                    else:
                        remaining = build_live_product_update_payload(
                            updated,
                            form.cleaned_data,
                        )

                        if remaining:
                            messages.warning(
                                request,
                                "Promall responded, but these changes "
                                "were not confirmed: "
                                + ", ".join(remaining.keys())
                            )
                        else:
                            messages.success(
                                request,
                                "Product updated successfully on Promall."
                            )

                    return redirect(
                        "promall_live_edit_product",
                        product_id=product_id,
                    )

                except Exception as error:
                    messages.error(
                        request,
                        f"Could not save product: {error}"
                    )

    else:
        initial_values = {
            field: product.get(field) or ""
            for field in fields
        }

        initial_values.update({
            "sku_meta_title": sku_parts[0],
            "sku_meta_description": sku_parts[1],
            "sku_keywords": sku_parts[2],
            "category_id": str(product.get("category_id") or ""),
            "subcategory_id": str(product.get("subcategory_id") or ""),
            "priority": product.get("priority"),
            "video_url": product.get("video_url") or "",
            "tag": product.get("tag") or "",
            "alternative_products": parse_promall_product_ids(
                product.get("alternative_products")
            ),
            "complementary_products": parse_promall_product_ids(
                product.get("complementary_products")
            ),
        })

        form = LiveProductDescriptionForm(
            initial=initial_values,
            product_choices=product_choices,
            categories=categories,
            subcategories=subcategories,
        )

    if request.method == "POST":
        faq_count = min(
            max(int(request.POST.get("faq_count", "0")), 0),
            100,
        )
        faqs = [
            {
                "question": request.POST.get(f"faq_question_{i}", ""),
                "answer": request.POST.get(f"faq_answer_{i}", ""),
            }
            for i in range(faq_count)
        ]
    else:
        faqs = parse_promall_faqs(product.get("faq"))

    context = {
        **admin.site.each_context(request),
        "title": f"Edit Product #{product_id}",
        "product": product,
        "form": form,
        "faqs": faqs,
        "subcategory_options": form.subcategory_options,
    }

    return render(
        request,
        "admin/promall_live/edit_product.html",
        context,
    )


def parse_promall_faqs(raw_faq):
    """Convert API FAQ text into question-and-answer pairs."""
    if not raw_faq:
        return []

    result = []

    for block in str(raw_faq).split("***"):
        block = block.strip()
        if not block:
            continue

        question, separator, answer = block.partition("\n")

        result.append({
            "question": question.strip(),
            "answer": answer.strip() if separator else "",
        })

    return result


def serialize_promall_faqs(faqs):
    """Convert edited FAQ pairs into the API format."""
    blocks = []

    for faq in faqs:
        question = faq["question"].strip()
        answer = faq["answer"].strip()

        if question and answer:
            blocks.append(f"{question}\n{answer}")

    return "\n***\n".join(blocks)



def split_promall_sku(value):
    parts = str(value or "").split("***", 2)
    parts += [""] * (3 - len(parts))
    return parts[:3]


def join_promall_sku(title, description, keywords):
    return "***".join([
        title.strip(),
        description.strip(),
        keywords.strip(),
    ])


def parse_promall_product_ids(value):
    import json

    if not value:
        return []

    if isinstance(value, list):
        items = value
    else:
        try:
            items = json.loads(value)
        except (TypeError, ValueError):
            return []

    if not isinstance(items, list):
        return []

    return [str(item) for item in items]


def build_live_product_update_payload(product, cleaned_data):
    """Build a partial product update without modifying unchanged fields."""
    import json

    payload = {}

    def normalized(value):
        return "" if value is None else str(value)

    simple_fields = [
        "description",
        "short_description",
        "more_information",
        "category_id",
        "subcategory_id",
        "priority",
        "video_url",
        "tag",
    ]

    for field in simple_fields:
        new_value = cleaned_data.get(field)
        old_value = product.get(field)

        if normalized(new_value) != normalized(old_value):
            payload[field] = new_value

    # SKU is stored as three sections separated by ***
    old_sku = normalized(product.get("sku"))
    old_parts = split_promall_sku(old_sku)

    new_parts = [
        normalized(cleaned_data.get("sku_meta_title")),
        normalized(cleaned_data.get("sku_meta_description")),
        normalized(cleaned_data.get("sku_keywords")),
    ]

    if new_parts != old_parts:
        payload["sku"] = "***".join(new_parts)

    # Related products are stored as JSON strings.
    for field in (
        "alternative_products",
        "complementary_products",
    ):
        old_ids = parse_promall_product_ids(product.get(field))
        new_ids = [
            str(item)
            for item in cleaned_data.get(field, [])
        ]

        if new_ids != old_ids:
            payload[field] = json.dumps(new_ids)

    # FAQ updates are intentionally excluded until the
    # existing API FAQ format is fully verified.

    return payload
