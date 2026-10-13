import requests

API_BASE = "https://protrackapi.casdnet.com/promall/api"


def fetch_live_categories():
    response = requests.get(
        f"{API_BASE}/categories",
        headers={"Accept": "application/json"},
        timeout=30,
    )
    response.raise_for_status()

    payload = response.json()

    if not isinstance(payload, dict) or payload.get("success") is not True:
        raise ValueError("Categories API returned an unsuccessful response.")

    categories = payload.get("data", [])

    if not isinstance(categories, list):
        raise ValueError("Unexpected categories response format.")

    return categories


def fetch_live_subcategories():
    response = requests.get(
        f"{API_BASE}/subcategories",
        headers={"Accept": "application/json"},
        timeout=30,
    )
    response.raise_for_status()

    payload = response.json()

    if not isinstance(payload, dict) or payload.get("success") is not True:
        raise ValueError("Subcategories API returned an unsuccessful response.")

    subcategories = payload.get("data", [])

    if not isinstance(subcategories, list):
        raise ValueError("Unexpected subcategories response format.")

    return subcategories


def update_live_category(category_id, payload):
    """Send validated category changes to the Promall API."""
    import requests

    url = (
        "https://protrackapi.casdnet.com/promall/api"
        f"/categories/update/{int(category_id)}"
    )

    response = requests.post(
        url,
        json=payload,
        timeout=30,
    )

    response.raise_for_status()

    try:
        return response.json()
    except ValueError:
        raise ValueError(
            "Promall returned a non-JSON response. "
            "The update result could not be verified."
        )


def update_live_subcategory(subcategory_id, payload):
    import requests

    url = (
        "https://protrackapi.casdnet.com/promall/api"
        f"/subcategories/update/{int(subcategory_id)}"
    )

    response = requests.post(url, json=payload, timeout=30)
    response.raise_for_status()

    try:
        result = response.json()
    except ValueError:
        raise ValueError("Promall returned a non-JSON response.")

    if isinstance(result, dict) and (
        result.get("success") is False
        or result.get("status") is False
    ):
        raise ValueError(f"Promall rejected the update: {result}")

    return result
