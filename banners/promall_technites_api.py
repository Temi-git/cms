import os
import requests
from urllib.parse import quote

PRICING_API_URL = "https://protrackapi.casdnet.com/api/pricing"


def pricing_api_headers():
    token = os.environ.get("TECHNITES_API_TOKEN")

    if not token:
        raise RuntimeError(
            "TECHNITES_API_TOKEN environment variable is not configured."
        )

    return {
        "Authorization": f"Bearer {token}",
        "Accept": "application/json",
        "Content-Type": "application/json",
    }


def fetch_technites_pricing():
    response = requests.get(
        PRICING_API_URL,
        headers=pricing_api_headers(),
        timeout=30,
    )
    response.raise_for_status()

    payload = response.json()

    if not isinstance(payload, dict) or payload.get("success") is not True:
        raise ValueError("Pricing API returned an unsuccessful response.")

    data = payload.get("data")

    if not isinstance(data, dict):
        raise ValueError("Unexpected pricing API response format.")

    for product, tiers in data.items():
        if not isinstance(tiers, list):
            raise ValueError(f"Invalid pricing records for {product}.")

        for record in tiers:
            if not isinstance(record, dict):
                raise ValueError(f"Invalid pricing record for {product}.")

            if not isinstance(record.get("features"), list):
                raise ValueError(f"Invalid features for {product}.")

    return data


def update_technites_pricing(product, tier, price, features):
    product_path = quote(str(product), safe="")
    tier_path = quote(str(tier), safe="")

    url = f"{PRICING_API_URL}/{product_path}/{tier_path}"

    response = requests.put(
        url,
        json={
            "price": str(price),
            "features": features,
        },
        headers=pricing_api_headers(),
        timeout=30,
    )

    try:
        response.raise_for_status()
    except requests.HTTPError as exc:
        raise RuntimeError(
            f"Pricing API returned HTTP {response.status_code}: "
            f"{response.text[:1000]}"
        ) from exc

    try:
        payload = response.json() if response.content else {}
    except ValueError as exc:
        raise RuntimeError(
            f"Pricing API returned invalid JSON: {response.text[:1000]}"
        ) from exc

    if isinstance(payload, dict) and payload.get("success") is False:
        raise RuntimeError(f"Pricing API rejected the update: {payload}")

    return payload
