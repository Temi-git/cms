import requests

PRODUCTS_URL = "https://protrackapi.casdnet.com/promall/api/products/grouped"


def fetch_live_products():
    response = requests.get(
        PRODUCTS_URL,
        headers={"Accept": "application/json"},
        timeout=30,
    )
    response.raise_for_status()

    payload = response.json()

    if not isinstance(payload, dict) or payload.get("success") is not True:
        raise ValueError("Promall API returned an unsuccessful response.")

    groups = payload.get("data", [])
    if not isinstance(groups, list):
        raise ValueError("Unexpected Promall product response format.")

    products = []

    for group in groups:
        if not isinstance(group, dict):
            continue

        for product in group.get("products", []):
            if not isinstance(product, dict):
                continue

            products.append({
                **product,
                "category_name": group.get("category_name", ""),
            })

    return products


def update_live_product(product_id, payload):
    """Send product updates directly to Promall without authorization."""
    import requests

    url = (
        "https://protrackapi.casdnet.com/promall/api/"
        f"products/update-product/{product_id}"
    )

    print("PROMALL PRODUCT UPDATE ID:", product_id)
    print("PROMALL PAYLOAD FIELDS:", list(payload.keys()))

    response = requests.post(
        url,
        json=payload,
        timeout=30,
    )

    if response.status_code >= 400:
        print("PROMALL UPDATE STATUS:", response.status_code)
        print(
            "PROMALL RESPONSE:",
            response.text[:500],
        )
        response.raise_for_status()

    result = response.json()

    if isinstance(result, dict):
        if result.get("success") is False or result.get("status") is False:
            raise RuntimeError(
                f"Promall rejected product update: {result}"
            )

    return result
