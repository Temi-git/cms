import logging
logger = logging.getLogger(__name__)
from decimal import Decimal, InvalidOperation

from django import forms
from django.contrib import admin, messages
from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import render, redirect
from django.urls import reverse
from django.views.decorators.http import require_http_methods

from .promall_technites_api import (
    fetch_technites_pricing,
    update_technites_pricing,
)


class TechnitesPricingForm(forms.Form):
    price = forms.CharField(
        label="Price",
        max_length=30,
        help_text="Enter the price as a number, for example 15000.00.",
    )
    features = forms.CharField(
        label="Features",
        widget=forms.Textarea(attrs={"rows": 12}),
        help_text="Enter one feature per line.",
    )

    def clean_price(self):
        value = self.cleaned_data["price"].strip()
        try:
            amount = Decimal(value)
        except InvalidOperation:
            raise forms.ValidationError("Enter a valid price.")

        if not amount.is_finite() or amount < 0:
            raise forms.ValidationError("Price must be a non-negative number.")

        if amount.as_tuple().exponent < -2:
            raise forms.ValidationError("Price can have at most two decimal places.")

        return format(amount, ".2f")

    def clean_features(self):
        value = self.cleaned_data["features"]
        features = [line.strip() for line in value.splitlines() if line.strip()]
        if not features:
            raise forms.ValidationError("Enter at least one feature.")
        return features


@staff_member_required
@require_http_methods(["GET"])
def technites_pricing_admin(request):
    import os

    try:
        logger.warning(
            "Technites pricing request: token_available=%s",
            bool(os.environ.get("TECHNITES_API_TOKEN")),
        )

        pricing = fetch_technites_pricing()

        logger.warning(
            "Technites pricing loaded successfully: products=%s",
            len(pricing),
        )

    except Exception:
        logger.exception("Technites pricing page failed to load.")
        messages.error(
            request,
            "Unable to load live Technites pricing. Check the server log.",
        )
        pricing = {}

    context = {
        **admin.site.each_context(request),
        "title": "Technites Pricing",
        "pricing": pricing,
    }

    return render(
        request,
        "admin/promall_technites/pricing.html",
        context,
    )

@staff_member_required
@require_http_methods(["GET", "POST"])
def edit_technites_pricing(request, product, tier):
    try:
        pricing = fetch_technites_pricing()
        records = pricing.get(product)

        if not isinstance(records, list):
            messages.error(request, "That product was not found in the live pricing API.")
            return redirect("promall_technites_pricing")

        record = next(
            (item for item in records if item.get("tier") == tier),
            None,
        )
        if record is None:
            messages.error(request, "That pricing tier was not found.")
            return redirect("promall_technites_pricing")

    except Exception:
        messages.error(request, "Unable to load the selected live pricing record.")
        return redirect("promall_technites_pricing")

    initial = {
        "price": record.get("price", ""),
        "features": "\n".join(record.get("features", [])),
    }

    if request.method == "POST":
        form = TechnitesPricingForm(request.POST)
        if form.is_valid():
            try:
                update_technites_pricing(
                    product,
                    tier,
                    form.cleaned_data["price"],
                    form.cleaned_data["features"],
                )

                # Verify the displayed values against a fresh GET.
                refreshed = fetch_technites_pricing()
                updated_record = next(
                    (
                        item for item in refreshed.get(product, [])
                        if item.get("tier") == tier
                    ),
                    None,
                )

                if (
                    updated_record is None
                    or str(updated_record.get("price")) != form.cleaned_data["price"]
                    or updated_record.get("features") != form.cleaned_data["features"]
                ):
                    messages.warning(
                        request,
                        "The API accepted the update, but the refreshed values differ. "
                        "Review the live record before editing again.",
                    )
                else:
                    messages.success(request, "Technites pricing updated and verified.")

                return redirect("promall_technites_pricing")

            except Exception as exc:
                messages.error(
                    request,
                    f"Pricing update/verification error: {exc}",
                )
    else:
        form = TechnitesPricingForm(initial=initial)

    context = {
        **admin.site.each_context(request),
        "title": f"Edit {product} â€” {tier}",
        "product": product,
        "tier": tier,
        "record": record,
        "form": form,
    }
    return render(request, "admin/promall_technites/edit_pricing.html", context)


