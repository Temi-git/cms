from .promall_category_faq_parser import parse_category_faqs
from .promall_category_faq import extract_category_faq_sections
from django.contrib import admin, messages
from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import render, redirect

from .promall_live_taxonomy_api import (
    fetch_live_categories,
    fetch_live_subcategories,
)


@staff_member_required
def live_categories_admin(request):
    try:
        categories = fetch_live_categories()
    except Exception as error:
        categories = []
        messages.error(request, f"Could not fetch categories: {error}")

    query = request.GET.get("q", "").strip().lower()

    if query:
        categories = [
            category for category in categories
            if query in str(category.get("name", "")).lower()
            or query in str(category.get("id", "")).lower()
        ]

    context = {
        **admin.site.each_context(request),
        "title": "Live Promall Categories",
        "categories": categories,
        "query": query,
    }

    return render(
        request,
        "admin/promall_live/categories.html",
        context,
    )


@staff_member_required
def live_subcategories_admin(request):
    try:
        categories = fetch_live_categories()
        subcategories = fetch_live_subcategories()

        category_names = {
            str(category["id"]): category.get("name", "")
            for category in categories
        }

        for subcategory in subcategories:
            subcategory["parent_category_name"] = category_names.get(
                str(subcategory.get("category_id")),
                "Unknown category",
            )

    except Exception as error:
        subcategories = []
        messages.error(request, f"Could not fetch subcategories: {error}")

    query = request.GET.get("q", "").strip().lower()

    if query:
        subcategories = [
            subcategory for subcategory in subcategories
            if query in str(subcategory.get("name", "")).lower()
            or query in str(subcategory.get("id", "")).lower()
            or query in str(subcategory.get("parent_category_name", "")).lower()
        ]

    context = {
        **admin.site.each_context(request),
        "title": "Live Promall Subcategories",
        "subcategories": subcategories,
        "query": query,
    }

    return render(
        request,
        "admin/promall_live/subcategories.html",
        context,
    )


from django.shortcuts import get_object_or_404
from .promall_live_category_forms import LiveCategoryForm


@staff_member_required
def edit_live_category(request, category_id):
    from .promall_live_taxonomy_api import update_live_category

    try:
        categories = fetch_live_categories()

        category = next(
            (
                item for item in categories
                if str(item.get("id")) == str(category_id)
            ),
            None,
        )

        if category is None:
            messages.error(request, "Category not found.")
            return redirect("promall_live_categories")

    except Exception as error:
        messages.error(request, f"Could not fetch category: {error}")
        return redirect("promall_live_categories")

    if request.method == "POST":
        form = LiveCategoryForm(request.POST)

        if form.is_valid():
            fields = [
                "name",
                "title",
                "slug",
                "description",
                "post",
                "priority",
                "online_discount",
                "active",
            ]

            payload = {}

            for field in fields:
                new_value = form.cleaned_data[field]
                old_value = category.get(field)

                if str(new_value if new_value is not None else "") != str(
                    old_value if old_value is not None else ""
                ):
                    payload[field] = new_value

            if not payload:
                messages.info(request, "No category changes detected.")

            else:
                try:
                    update_live_category(category_id, payload)

                    refreshed_categories = fetch_live_categories()
                    updated_category = next(
                        (
                            item for item in refreshed_categories
                            if str(item.get("id")) == str(category_id)
                        ),
                        None,
                    )

                    if updated_category is None:
                        messages.warning(
                            request,
                            "Update request completed, but the category "
                            "could not be reloaded from Promall."
                        )
                    else:
                        mismatched = [
                            field
                            for field, value in payload.items()
                            if str(
                                updated_category.get(field)
                                if updated_category.get(field) is not None
                                else ""
                            ) != str(value if value is not None else "")
                        ]

                        if mismatched:
                            messages.warning(
                                request,
                                "Promall responded, but these fields were "
                                "not confirmed after refresh: "
                                + ", ".join(mismatched)
                            )
                        else:
                            messages.success(
                                request,
                                "Category updated successfully on Promall."
                            )

                    return redirect(
                        "promall_live_edit_category",
                        category_id=category_id,
                    )

                except Exception as error:
                    messages.error(
                        request,
                        f"Could not update category: {error}"
                    )
    else:
        form = LiveCategoryForm(initial=category)

    context = {
        **admin.site.each_context(request),
        "title": f"Edit Category: {category.get('name', '')}",
        "category": category,
        "form": form,
        "faqs": parse_category_faqs(category.get("faq")),
    }

    return render(
        request,
        "admin/promall_live/edit_category.html",
        context,
    )


from django.shortcuts import redirect
from .promall_live_subcategory_forms import LiveSubcategoryForm


@staff_member_required
def edit_live_subcategory(request, subcategory_id):
    from decimal import Decimal
    from .promall_live_taxonomy_api import update_live_subcategory

    try:
        subcategories = fetch_live_subcategories()
        categories = fetch_live_categories()

        subcategory = next(
            (item for item in subcategories
             if str(item.get("id")) == str(subcategory_id)),
            None,
        )

        if subcategory is None:
            messages.error(request, "Subcategory not found.")
            return redirect("promall_live_subcategories")

    except Exception as error:
        messages.error(request, f"Could not fetch subcategory: {error}")
        return redirect("promall_live_subcategories")

    if request.method == "POST":
        form = LiveSubcategoryForm(
            request.POST,
            categories=categories,
        )

        if form.is_valid():
            fields = [
                "name", "category_id", "slug", "active",
                "online_discount", "commission_rate",
                "cdn_only", "company_id",
            ]

            payload = {}

            def normalize(value):
                if value is None:
                    return ""
                return str(value)

            for field in fields:
                new_value = form.cleaned_data[field]
                old_value = subcategory.get(field)

                if field == "commission_rate":
                    if new_value is not None:
                        new_value = float(new_value)
                    if old_value not in (None, ""):
                        try:
                            old_value = float(old_value)
                        except (ValueError, TypeError):
                            pass

                if normalize(new_value) != normalize(old_value):
                    payload[field] = new_value

            if not payload:
                messages.info(request, "No subcategory changes detected.")
            else:
                try:
                    result = update_live_subcategory(
                        subcategory_id, payload
                    )

                    refreshed = fetch_live_subcategories()
                    updated = next(
                        (item for item in refreshed
                         if str(item.get("id")) == str(subcategory_id)),
                        None,
                    )

                    if updated is None:
                        messages.warning(
                            request,
                            "Update sent, but subcategory could not be reloaded."
                        )
                    else:
                        mismatched = [
                            field for field, value in payload.items()
                            if normalize(updated.get(field))
                            != normalize(value)
                        ]

                        if mismatched:
                            messages.warning(
                                request,
                                "Update not confirmed for: "
                                + ", ".join(mismatched)
                            )
                        else:
                            messages.success(
                                request,
                                "Subcategory updated successfully on Promall."
                            )

                    return redirect(
                        "promall_live_edit_subcategory",
                        subcategory_id=subcategory_id,
                    )

                except Exception as error:
                    messages.error(
                        request,
                        f"Could not save subcategory: {error}"
                    )
    else:
        form = LiveSubcategoryForm(
            initial=subcategory,
            categories=categories,
        )

    context = {
        **admin.site.each_context(request),
        "title": f"Edit Subcategory: {subcategory.get('name', '')}",
        "subcategory": subcategory,
        "form": form,
    }

    return render(
        request,
        "admin/promall_live/edit_subcategory.html",
        context,
    )
