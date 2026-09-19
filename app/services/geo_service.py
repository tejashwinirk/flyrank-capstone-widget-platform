import httpx

from app.config import GEO_PROVIDER_A_URL, GEO_PROVIDER_B_URL


def get_geo_data(ip_address: str | None):
    if not ip_address:
        return {
            "country": None,
            "region": None,
            "city": None,
        }

    # Provider A
    try:
        response = httpx.get(
            f"{GEO_PROVIDER_A_URL}/{ip_address}",
            timeout=3,
        )

        if response.status_code == 200:
            data = response.json()

            if data.get("status") != "fail":
                return {
                    "country": data.get("country"),
                    "region": data.get("regionName"),
                    "city": data.get("city"),
                }

    except Exception:
        pass

    # Provider B
    try:
        response = httpx.get(
            f"{GEO_PROVIDER_B_URL}/{ip_address}/json/",
            timeout=3,
        )

        if response.status_code == 200:
            data = response.json()

            return {
                "country": data.get("country_name"),
                "region": data.get("region"),
                "city": data.get("city"),
            }

    except Exception:
        pass

    # Both providers failed.
    return {
        "country": None,
        "region": None,
        "city": None,
    }