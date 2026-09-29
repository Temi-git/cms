"""
banners/services.py

External product synchronization service.

Usage (e.g. from a management command or scheduled task):
    from banners.services import sync_external_products
    results = sync_external_products()
"""

import logging
import requests
from decimal import Decimal, InvalidOperation

from django.conf import settings

logger = logging.getLogger(__name__)

# Override in settings.py if needed
EXTERNAL_PRODUCTS_URL = getattr(
    settings,
    "PROMALLSHOP_PRODUCTS_URL",
    "https://api.promallshop.com/api/v1/products/",
)

# Fields that belong to the admin and must NEVER be overwritten by sync
ADMIN_ONLY_FIELDS = frozenset({
    "is_special",
    "is_hot",
    "is_active",
    "display_order",
    "slug",
})


def _safe_decimal(value):
    """Convert a value to Decimal or return None."""
    if value is None:
        return None
    try:
        return Decimal(str(value))
    except (InvalidOperation, TypeError, ValueError):
        return None


def _map_external_product(raw):
    """
    Map one record from the external API response to our Product fields.

    Adjust the key names below to match whatever the real API returns.
    Common patterns are snake_case and camelCase — inspect the response
    and update accordingly.

    Returns a dict of ONLY the fields that come from the external source.
    Admin-controlled fields (is_special, is_hot, etc.) are NOT included.
    """
    # --- Adjust these keys to match the actual external API fields ---
    external_id = (
        raw.get("id")
        or raw.get("product_id")
        or raw.get("_id")
    )
    name = (
        raw.get("name")
        or raw.get("title")
        or raw.get("product_name")
        or ""
    )
    description = (
        raw.get("description")
        or raw.get("short_description")
        or raw.get("details")
        or ""
    )
    image_url = (
        raw.get("image")
        or raw.get("image_url")
        or raw.get("thumbnail")
        or ""
    )
    price_raw = (
        raw.get("price")
        or raw.get("amount")
        or raw.get("selling_price")
    )
    product_url = (
        raw.get("url")
        or raw.get("product_url")
        or raw.get("link")
        or ""
    )

    return {
        "external_product_id": str(external_id) if external_id else None,
        "name": str(name).strip(),
        "description": str(description).strip(),
        "price": _safe_decimal(price_raw),
        "product_url": str(product_url).strip(),
        # image is handled separately (URL → we store the URL string, not upload)
        "_image_url": str(image_url).strip(),
    }


def sync_external_products(url=None, timeout=30):
    """
    Fetch products from the external Promallshop API and synchronise
    them with the local Product table.

    Rules:
    - Match by external_product_id.
    - Create new Product records for new external products.
    - Update name / description / price / product_url for existing ones.
    - NEVER overwrite admin-controlled fields: is_special, is_hot,
      is_active, display_order, slug.
    - If the external API is unreachable, log the error and return gracefully.
    - Does NOT delete local products that disappear from the API.

    Returns a dict: {"created": int, "updated": int, "skipped": int, "errors": list}
    """
    # Lazy import to avoid circular dependency at module load time
    from .models import Product  # noqa: PLC0415

    endpoint = url or EXTERNAL_PRODUCTS_URL
    result = {"created": 0, "updated": 0, "skipped": 0, "errors": []}

    # ── Fetch ─────────────────────────────────────────────────
    try:
        response = requests.get(endpoint, timeout=timeout)
        response.raise_for_status()
    except requests.exceptions.Timeout:
        msg = f"sync_external_products: request to {endpoint} timed out."
        logger.error(msg)
        result["errors"].append(msg)
        return result
    except requests.exceptions.RequestException as exc:
        msg = f"sync_external_products: request failed — {exc}"
        logger.error(msg)
        result["errors"].append(msg)
        return result

    # ── Parse ─────────────────────────────────────────────────
    try:
        payload = response.json()
    except ValueError as exc:
        msg = f"sync_external_products: invalid JSON — {exc}"
        logger.error(msg)
        result["errors"].append(msg)
        return result

    # The external response may be a list or wrapped: {"results": [...]}
    if isinstance(payload, list):
        items = payload
    elif isinstance(payload, dict):
        items = (
            payload.get("results")
            or payload.get("data")
            or payload.get("products")
            or []
        )
    else:
        msg = "sync_external_products: unexpected response shape."
        logger.error(msg)
        result["errors"].append(msg)
        return result

    # ── Sync ──────────────────────────────────────────────────
    for raw in items:
        try:
            mapped = _map_external_product(raw)
        except Exception as exc:
            msg = f"sync_external_products: mapping error for {raw!r} — {exc}"
            logger.warning(msg)
            result["errors"].append(msg)
            result["skipped"] += 1
            continue

        ext_id = mapped.get("external_product_id")
        if not ext_id:
            logger.warning(
                "sync_external_products: skipping record with no external_product_id: %r",
                raw,
            )
            result["skipped"] += 1
            continue

        if not mapped.get("name"):
            logger.warning(
                "sync_external_products: skipping record %s with empty name.", ext_id
            )
            result["skipped"] += 1
            continue

        # External-source fields only — do NOT include admin fields
        sync_fields = {
            "name": mapped["name"],
            "description": mapped["description"],
            "price": mapped["price"],
            "product_url": mapped["product_url"],
        }

        try:
            product, created = Product.objects.get_or_create(
                external_product_id=ext_id,
                defaults={
                    **sync_fields,
                    # Safe defaults for a brand-new record
                    "is_active": True,
                    "is_special": False,
                    "is_hot": False,
                    "display_order": 0,
                },
            )

            if created:
                result["created"] += 1
                logger.info(
                    "sync_external_products: created Product id=%s name=%r ext=%s",
                    product.pk, product.name, ext_id,
                )
            else:
                # Update only the external-source fields
                changed = False
                for field, value in sync_fields.items():
                    if getattr(product, field) != value:
                        setattr(product, field, value)
                        changed = True
                if changed:
                    product.save(update_fields=list(sync_fields.keys()) + ["updated_at"])
                    result["updated"] += 1
                    logger.info(
                        "sync_external_products: updated Product id=%s ext=%s",
                        product.pk, ext_id,
                    )

        except Exception as exc:
            msg = f"sync_external_products: DB error for ext_id={ext_id} — {exc}"
            logger.error(msg)
            result["errors"].append(msg)
            result["skipped"] += 1

    logger.info(
        "sync_external_products complete: created=%d updated=%d skipped=%d errors=%d",
        result["created"], result["updated"], result["skipped"], len(result["errors"]),
    )
    return result
