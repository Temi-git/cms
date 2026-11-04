import os
import requests

from django import forms
from django.contrib import admin, messages
from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import redirect, render
from django.urls import reverse
from django.views.decorators.http import require_http_methods


CDN_API_BASE_URL = os.getenv(
    "CDN_API_BASE_URL",
    "https://protrackapi.casdnet.com/promall",
).rstrip("/")

CDN_API_TOKEN = os.getenv("CDN_API_TOKEN", "")
CDN_COMPANY_ID = "1"
CDN_TIMEOUT = 30

# Only these four product fields may be edited.
PRODUCT_FIELDS = (
    "name",
    "description",
    "short_description",
    "more_information",
)

# Keep the existing remote category editing fields.
CATEGORY_FIELDS = (
    "name",
    "description",
    "icon",
    "active",
    "slug",
    "banner",
    "priority",
    "delivery_type",
)


def _cdn_request(method, endpoint, params=None, payload=None):
    headers = {"Accept": "application/json"}

    if method.upper() == "PUT":
        token = os.getenv("CDN_API_TOKEN", "").strip()

        if not token:
            raise RuntimeError(
                "CDN_API_TOKEN is missing from the server environment."
            )

        headers["Authorization"] = f"Bearer {token}"
        headers["Content-Type"] = "application/json"

    response = requests.request(
        method=method.upper(),
        url=f"{CDN_API_BASE_URL}{endpoint}",
        headers=headers,
        params=params,
        json=payload,
        timeout=CDN_TIMEOUT,
    )

    try:
        body = response.json()
    except ValueError:
        body = {}

    if not response.ok:
        message = (
            body.get("message")
            or body.get("error")
            or response.text
        )
        raise RuntimeError(
            f"CDN API returned HTTP {response.status_code}: {message}"
        )

    if isinstance(body, dict) and body.get("success") is False:
        raise RuntimeError(
            body.get("message") or "CDN API request failed."
        )

    return body


def _cdn_data(body):
    if isinstance(body, dict):
        return body.get("data", body.get("results", body))
    return body


def _cdn_list(endpoint, search=""):
    params = {"company_id": CDN_COMPANY_ID}

    if search:
        params["search"] = search

    data = _cdn_data(
        _cdn_request("GET", endpoint, params=params)
    )

    if isinstance(data, dict):
        for key in ("products", "categories", "items", "results"):
            if isinstance(data.get(key), list):
                return data[key]

        return [data] if data.get("id") is not None else []

    return data if isinstance(data, list) else []


def _cdn_detail(endpoint, record_id):
    data = _cdn_data(
        _cdn_request("GET", f"{endpoint}/{record_id}")
    )

    if isinstance(data, list):
        return next(
            (
                item for item in data
                if str(item.get("id")) == str(record_id)
            ),
            None,
        )

    return data if isinstance(data, dict) else None


class CDNProductDescriptionForm(forms.Form):
    def __init__(self, *args, categories=None, **kwargs):
        super().__init__(*args, **kwargs)

        choices = [("", "---------")]
        for category in categories or []:
            category_id = category.get("id")
            category_name = category.get("name")
            if category_id is not None:
                choices.append((str(category_id), str(category_name or f"Category {category_id}")))

        self.fields["name"] = forms.CharField(
            required=False,
            label="Product Name",
            widget=forms.TextInput(attrs={"style": "width:100%;"}),
        )

        self.fields["category_id"] = forms.ChoiceField(
            required=False,
            label="Product Category",
            choices=choices,
        )

        self.fields["description"] = forms.CharField(
            required=False,
            label="Full Description",
            widget=forms.Textarea(attrs={"class": "cdn-rte-source", "rows": 12}),
        )

        self.fields["short_description"] = forms.CharField(
            required=False,
            label="Short Description",
            widget=forms.Textarea(attrs={"rows": 5, "style": "width:100%;"}),
        )

        self.fields["more_information"] = forms.CharField(
            required=False,
            label="More Information",
            widget=forms.Textarea(attrs={"class": "cdn-rte-source", "rows": 10}),
        )

    def changed_payload(self):
        return {
            name: self.cleaned_data.get(name)
            for name in self.changed_data
        }


class CDNCategoryForm(forms.Form):
    def __init__(self, *args, record=None, **kwargs):
        super().__init__(*args, **kwargs)
        record = record or {}

        for name in CATEGORY_FIELDS:
            value = record.get(name)

            if name == "description":
                field = forms.CharField(
                    required=False,
                    initial=value or "",
                    widget=forms.Textarea(
                        attrs={
                            "rows": 5,
                            "style": "width:100%;",
                        }
                    ),
                )
            elif name in ("banner", "icon"):
                field = forms.CharField(
                    required=False,
                    initial="" if value is None else str(value),
                    widget=forms.TextInput(
                        attrs={"style": "width:100%;"}
                    ),
                )
            elif name == "priority":
                field = forms.IntegerField(
                    required=False,
                    initial=value,
                )
            else:
                field = forms.CharField(
                    required=False,
                    initial="" if value is None else str(value),
                    widget=forms.TextInput(
                        attrs={"style": "width:100%;"}
                    ),
                )

            field.label = name.replace("_", " ").title()
            self.fields[name] = field

    def changed_payload(self):
        return {
            name: self.cleaned_data.get(name)
            for name in self.changed_data
        }


def _cdn_list_page(request, endpoint, title, kind, edit_route):
    query = request.GET.get("q", "").strip()

    try:
        records = _cdn_list(endpoint, query)
        api_error = None
    except Exception as exc:
        records = []
        api_error = str(exc)
        messages.error(
            request,
            f"Could not fetch {title.lower()}: {exc}",
        )

    context = {
        **admin.site.each_context(request),
        "title": title,
        "records": records,
        "query": query,
        "kind": kind,
        "edit_route": edit_route,
        "api_error": api_error,
    }

    return render(
        request,
        "admin/casdnet_cdn/list.html",
        context,
    )


@staff_member_required
def cdn_products_admin(request):
    return _cdn_list_page(
        request,
        "/api/cdn-products",
        "CDN Products",
        "products",
        "casdnet_cdn_edit_product",
    )


@staff_member_required
def cdn_categories_admin(request):
    return _cdn_list_page(
        request,
        "/api/cdn-categories",
        "CDN Categories",
        "categories",
        "casdnet_cdn_edit_category",
    )


@staff_member_required
@require_http_methods(["GET", "POST"])
def edit_cdn_product(request, product_id):
    return _cdn_edit_record(
        request,
        product_id,
        "/api/cdn-products",
        "CDN Product",
        "products",
        "casdnet_cdn_products",
    )


@staff_member_required
@require_http_methods(["GET", "POST"])
def edit_cdn_category(request, category_id):
    return _cdn_edit_record(
        request,
        category_id,
        "/api/cdn-categories",
        "CDN Category",
        "categories",
        "casdnet_cdn_categories",
    )


def _cdn_edit_record(
    request,
    record_id,
    endpoint,
    title,
    kind,
    list_route,
):
    try:
        record = _cdn_detail(endpoint, record_id)
    except Exception as exc:
        messages.error(request, f"Could not fetch remote record: {exc}")
        return redirect(list_route)

    if not record:
        messages.error(request, "Remote record not found.")
        return redirect(list_route)

    if str(record.get("company_id", CDN_COMPANY_ID)) != CDN_COMPANY_ID:
        messages.error(request, "This record does not belong to company_id 1.")
        return redirect(list_route)

    categories = []
    if kind == "products":
        try:
            categories = _cdn_list("/api/cdn-categories")
        except Exception as exc:
            messages.error(request, f"Could not load CDN categories: {exc}")

        current_category = record.get("category_id")
        if current_category is not None and not any(
            str(item.get("id")) == str(current_category)
            for item in categories
        ):
            categories.append({
                "id": current_category,
                "name": f"Current category (ID {current_category})",
            })

        form_class = CDNProductDescriptionForm
        allowed_fields = PRODUCT_FIELDS
    else:
        form_class = CDNCategoryForm
        allowed_fields = CATEGORY_FIELDS

    if request.method == "POST":
        if kind == "products":
            initial = {
                name: record.get(name) if record.get(name) is not None else ""
                for name in PRODUCT_FIELDS
            }
            initial["category_id"] = (
                str(record.get("category_id"))
                if record.get("category_id") is not None else ""
            )
            form = form_class(
                request.POST,
                initial=initial,
                categories=categories,
            )
        else:
            form = form_class(request.POST, record=record)

        if form.is_valid():
            payload = form.changed_payload()

            if not payload:
                messages.info(request, "No changes detected.")
                return redirect(request.path)

            try:
                _cdn_request(
                    "PUT",
                    f"{endpoint}/{record_id}",
                    payload=payload,
                )

                refreshed = _cdn_detail(endpoint, record_id)

                if refreshed is None:
                    messages.warning(
                        request,
                        "Update sent, but the record could not be reloaded.",
                    )
                else:
                    messages.success(
                        request,
                        "Remote record updated and refreshed successfully.",
                    )

                return redirect(request.path)

            except Exception as exc:
                messages.error(
                    request,
                    f"Could not update remote record: {exc}",
                )
    else:
        if kind == "products":
            initial = {
                name: record.get(name) if record.get(name) is not None else ""
                for name in PRODUCT_FIELDS
            }
            initial["category_id"] = (
                str(record.get("category_id"))
                if record.get("category_id") is not None else ""
            )
            form = form_class(initial=initial, categories=categories)
        else:
            form = form_class(record=record)

    context = {
        **admin.site.each_context(request),
        "title": f"{title} #{record_id}",
        "record": record,
        "form": form,
        "kind": kind,
        "list_url": reverse(list_route),
    }

    return render(
        request,
        "admin/casdnet_cdn/edit.html",
        context,
    )

