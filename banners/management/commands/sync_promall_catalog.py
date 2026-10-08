"""
Management command: sync_promall_catalog

Usage:
    python manage.py sync_promall_catalog [--entity-slug promallshop]

Fetches both Promall API endpoints and upserts categories, subcategories,
and products into the database.

First-import vs later-sync rules:
  CREATE: fill every field; set is_hot/is_special from tag; parse FAQs and SKU.
  UPDATE: refresh only price, end_user_price, discount, quantity,
          external_image_paths, warranty, model_number (if blank),
          part_number (if blank).
          NEVER overwrite name, description, is_hot, is_special, is_active,
          display_order, meta_*, keywords, FAQs.
"""

from decimal import Decimal, InvalidOperation

import requests
from django.core.management.base import BaseCommand, CommandError
from django.utils.text import slugify

SUBCATEGORIES_URL = 'https://protrackapi.casdnet.com/promall/api/subcategories/grouped'
PRODUCTS_URL = 'https://protrackapi.casdnet.com/promall/api/products/grouped'
TIMEOUT = 30


def _to_decimal(val):
    """Convert a value to Decimal, returning None for empty/null values."""
    try:
        return Decimal(str(val)) if val not in (None, '', 'null') else None
    except InvalidOperation:
        return None


def _to_int(val):
    """Convert a value to int, returning None for empty/null values."""
    try:
        return int(val) if val not in (None, '', 'null') else None
    except (ValueError, TypeError):
        return None


def _parse_category_faq_fixed(entity, cat, faq_html):
    """
    Parse category FAQ content and create PromallCategoryFAQ rows.

    Tries to split on '***' (same delimiter as product FAQs).
    If that yields >= 2 non-empty chunks, creates individual Q&A rows.
    Otherwise stores the whole HTML as a single FAQ entry.
    Only called on first import (create path).
    """
    from banners.models import PromallCategoryFAQ

    if not faq_html or not faq_html.strip():
        return

    chunks = [c.strip() for c in faq_html.split('***') if c.strip()]
    if len(chunks) >= 2:
        for idx, chunk in enumerate(chunks):
            lines = chunk.strip().splitlines()
            question = lines[0].strip() if lines else ''
            answer = '\n'.join(lines[1:]).strip() if len(lines) > 1 else ''
            if not question:
                continue
            PromallCategoryFAQ.objects.get_or_create(
                category=cat,
                question=question,
                defaults={
                    'entity': entity,
                    'answer': answer,
                    'display_order': idx,
                    'is_active': True,
                },
            )
    else:
        # Store the whole HTML as a single FAQ
        PromallCategoryFAQ.objects.get_or_create(
            category=cat,
            question='Overview',
            defaults={
                'entity': entity,
                'answer': faq_html,
                'display_order': 0,
                'is_active': True,
            },
        )


def _parse_product_faq(entity, product, faq_text):
    """
    Parse product FAQ plain text and create PromallProductFAQ rows.

    Format: "Q\nA\n***\nQ\nA..."
    Splits on '***', first line of each chunk = question, rest = answer.
    Only called on first import (create path).

    Uses get_or_create keyed on (product, question) so that if a product row
    is ever deleted and re-created with the same external_id, re-running the
    sync will not produce duplicate FAQ rows.
    """
    from banners.models import PromallProductFAQ

    if not faq_text or not faq_text.strip():
        return

    chunks = [c.strip() for c in faq_text.split('***') if c.strip()]
    for idx, chunk in enumerate(chunks):
        lines = chunk.strip().splitlines()
        question = lines[0].strip() if lines else ''
        answer = '\n'.join(lines[1:]).strip() if len(lines) > 1 else ''
        if not question:
            continue
        PromallProductFAQ.objects.get_or_create(
            product=product,
            question=question,
            defaults={
                'entity': entity,
                'answer': answer,
                'display_order': idx,
                'is_active': True,
            },
        )


def _product_create_defaults(entity, cat, subcategory, p, is_active_val, ext_images):
    """
    Build the defaults dict for PromallProduct.objects.get_or_create on first import.
    """
    # Parse SKU: 'title***meta_desc***keywords'
    sku = (p.get('sku') or '').strip()
    sku_parts = sku.split('***') if sku else []
    meta_title = sku_parts[0].strip() if len(sku_parts) > 0 else ''
    meta_description = sku_parts[1].strip() if len(sku_parts) > 1 else ''
    keywords = sku_parts[2].strip() if len(sku_parts) > 2 else ''

    tag = (p.get('tag') or '').strip()
    is_hot = (tag == 'hot')
    is_special = (tag == 'special')

    name = (p.get('name') or '').strip()
    product_slug = slugify(name) if name else ''

    # Parse alternative/complementary product IDs
    alt_ids = p.get('alternative_products') or ''
    comp_ids = p.get('complementary_products') or ''
    if alt_ids == 'null':
        alt_ids = ''
    if comp_ids == 'null':
        comp_ids = ''

    return {
        'entity': entity,
        'category': cat,
        'subcategory': subcategory,
        'name': name,
        'slug': product_slug,
        'short_description': (p.get('short_description') or '').strip(),
        'description': (p.get('description') or '').strip(),
        'model_number': (p.get('model') or '').strip(),
        'part_number': (p.get('part_number') or '').strip(),
        'warranty': (p.get('warranty') or '').strip(),
        'video_url': (p.get('video_url') or '').strip(),
        'price': _to_decimal(p.get('price')),
        'end_user_price': _to_decimal(p.get('end_user_price')),
        'discount': _to_decimal(p.get('discount')),
        'quantity': _to_int(p.get('qty')),
        'external_image_paths': ext_images,
        'is_hot': is_hot,
        'is_special': is_special,
        'is_active': is_active_val,
        'display_order': _to_int(p.get('priority')) or 0,
        'alternative_product_ids': str(alt_ids) if alt_ids else '',
        'complementary_product_ids': str(comp_ids) if comp_ids else '',
        'meta_title': meta_title,
        'meta_description': meta_description,
        'keywords': keywords,
    }


def _upsert_product(entity, cat, p):
    """
    Upsert a single product. Returns 'created', 'updated', or 'skipped'.
    """
    from banners.models import PromallSubcategory, PromallProduct

    ext_id = str(p['id'])

    # Skip deleted products
    if str(p.get('is_deleted', '0')) == '1':
        return 'skipped'

    show_on = (p.get('show_on_promall') or '').strip().lower()
    is_active_val = (show_on == 'yes')

    # Resolve subcategory by external_id
    sub_ext_id = str(p.get('subcategory_id') or '').strip()
    subcategory = None
    if sub_ext_id and sub_ext_id != 'None':
        try:
            subcategory = PromallSubcategory.objects.get(external_id=sub_ext_id)
        except PromallSubcategory.DoesNotExist:
            pass

    # External image paths
    ext_images = (p.get('image') or '').strip()

    product, created = PromallProduct.objects.get_or_create(
        external_id=ext_id,
        defaults=_product_create_defaults(entity, cat, subcategory, p, is_active_val, ext_images),
    )

    if created:
        # Parse product FAQ text on first import
        _parse_product_faq(entity, product, p.get('faq') or '')
        return 'created'
    else:
        # UPDATE: refresh only the external-owned fields
        changed = False
        for field, val in [
            ('price', _to_decimal(p.get('price'))),
            ('end_user_price', _to_decimal(p.get('end_user_price'))),
            ('discount', _to_decimal(p.get('discount'))),
            ('quantity', _to_int(p.get('qty'))),
            ('external_image_paths', ext_images),
            ('warranty', (p.get('warranty') or '').strip()),
        ]:
            if getattr(product, field) != val:
                setattr(product, field, val)
                changed = True

        # model_number / part_number: only if currently blank
        mn = (p.get('model') or '').strip()
        pn = (p.get('part_number') or '').strip()
        if mn and not product.model_number:
            product.model_number = mn
            changed = True
        if pn and not product.part_number:
            product.part_number = pn
            changed = True

        # Mark inactive if show_on_promall != 'yes', but NEVER re-activate
        if not is_active_val and product.is_active:
            product.is_active = False
            changed = True

        if changed:
            product.save()
        return 'updated'


class Command(BaseCommand):
    help = 'Sync Promallshop catalog from external API'

    def add_arguments(self, parser):
        parser.add_argument(
            '--entity-slug',
            default='promallshop',
            help='Slug of the Entity record to associate all Promall content with.',
        )

    def handle(self, *args, **options):
        from banners.models import (
            Entity,
            PromallCategory,
            PromallSubcategory,
        )

        entity_slug = options['entity_slug']

        # 1. Resolve entity
        try:
            entity = Entity.objects.get(slug=entity_slug)
        except Entity.DoesNotExist:
            raise CommandError(
                f"Entity with slug '{entity_slug}' does not exist. "
                "Create it in the admin first or pass --entity-slug <correct-slug>."
            )

        # 2. Fetch subcategories endpoint
        self.stdout.write(f"Fetching subcategories from {SUBCATEGORIES_URL} ...")
        try:
            sub_response = requests.get(SUBCATEGORIES_URL, timeout=TIMEOUT)
            if sub_response.status_code != 200:
                raise CommandError(
                    f"Subcategories endpoint returned HTTP {sub_response.status_code}"
                )
            subcat_data = sub_response.json()
        except requests.exceptions.RequestException as exc:
            raise CommandError(f"Failed to fetch subcategories: {exc}")

        # 3. Fetch products endpoint
        self.stdout.write(f"Fetching products from {PRODUCTS_URL} ...")
        try:
            prod_response = requests.get(PRODUCTS_URL, timeout=TIMEOUT)
            if prod_response.status_code != 200:
                raise CommandError(
                    f"Products endpoint returned HTTP {prod_response.status_code}"
                )
            products_data = prod_response.json()
        except requests.exceptions.RequestException as exc:
            raise CommandError(f"Failed to fetch products: {exc}")

        # 4. Build subcat_map keyed by external id
        subcat_map = {}
        for group in subcat_data.get('data', []):
            cat_id = str(group.get('category_id', ''))
            for sub in group.get('subcategories', []):
                sub_copy = dict(sub)
                sub_copy['category_id'] = cat_id
                subcat_map[str(sub['id'])] = sub_copy

        # 5. Counters
        cat_created = cat_updated = 0
        sub_created = sub_updated = sub_skipped = 0
        prod_created = prod_updated = prod_skipped = 0

        # 6. Upsert categories (from products grouped data)
        self.stdout.write("Upserting categories ...")
        for group in products_data.get('data', []):
            ext_id = str(group['category_id'])
            name = (group.get('category_name') or '').strip()
            slug_val = (group.get('category_slug') or '').strip()
            desc = (group.get('category_description') or '').strip()
            faq_html = (group.get('faq') or '').strip()

            cat, created = PromallCategory.objects.get_or_create(
                external_id=ext_id,
                defaults={
                    'entity': entity,
                    'name': name,
                    'slug': slug_val,
                    'description': desc,
                    'display_order': _to_int(group.get('category_priority')) or 0,
                    'is_active': True,
                },
            )
            if created:
                cat_created += 1
                # Parse category FAQ on first import only
                _parse_category_faq_fixed(entity, cat, faq_html)
            else:
                cat_updated += 1

        # 7. Upsert subcategories
        self.stdout.write("Upserting subcategories ...")
        for sub_data in subcat_map.values():
            ext_id = str(sub_data['id'])
            cat_ext = str(sub_data['category_id'])
            try:
                cat = PromallCategory.objects.get(external_id=cat_ext)
            except PromallCategory.DoesNotExist:
                sub_skipped += 1
                continue

            sub, created = PromallSubcategory.objects.get_or_create(
                external_id=ext_id,
                defaults={
                    'entity': entity,
                    'category': cat,
                    'name': (sub_data.get('name') or '').strip(),
                    'slug': (sub_data.get('slug') or '').strip(),
                    'is_active': bool(sub_data.get('active', True)),
                    'display_order': 0,
                },
            )
            if created:
                sub_created += 1
            else:
                sub_updated += 1

        # 8. Upsert products
        self.stdout.write("Upserting products ...")
        for group in products_data.get('data', []):
            cat_ext = str(group['category_id'])
            try:
                cat = PromallCategory.objects.get(external_id=cat_ext)
            except PromallCategory.DoesNotExist:
                continue

            for p in group.get('products', []):
                try:
                    result = _upsert_product(entity, cat, p)
                    if result == 'created':
                        prod_created += 1
                    elif result == 'updated':
                        prod_updated += 1
                    else:
                        prod_skipped += 1
                except Exception as exc:
                    self.stderr.write(f"  ERROR product id={p.get('id')}: {exc}")

        # 9. Summary
        self.stdout.write(self.style.SUCCESS(
            f"Sync complete.\n"
            f"  Categories:    created={cat_created}, updated={cat_updated}\n"
            f"  Subcategories: created={sub_created}, updated={sub_updated}, skipped={sub_skipped}\n"
            f"  Products:      created={prod_created}, updated={prod_updated}, skipped={prod_skipped}\n"
        ))
