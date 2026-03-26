import time
import httpx
from crewai.tools import tool


def geocode_location(location: str):
    """Geocode a location string to (lat, lon) using Nominatim. Returns None on failure."""
    time.sleep(1)
    url = "https://nominatim.openstreetmap.org/search"
    params = {"q": location, "format": "json", "limit": 1}
    headers = {"User-Agent": "HomeScout/1.0"}
    try:
        resp = httpx.get(url, params=params, headers=headers, timeout=10)
        resp.raise_for_status()
        results = resp.json()
        if not results:
            return None
        lat = float(results[0]["lat"])
        lon = float(results[0]["lon"])
        return (lat, lon)
    except Exception:
        return None


@tool("overpass_tool")
def overpass_tool(location: str) -> str:
    """Geocode a location and fetch nearby POI counts from OpenStreetMap via Overpass API.
    Returns counts and sample names for parks, gyms, restaurants, grocery stores,
    transit stops, and schools within 2km."""
    coords = geocode_location(location)
    if coords is None:
        return f"Could not geocode location: {location}"
    lat, lon = coords
    return _get_pois(lat, lon, radius_meters=2000)


def _get_pois(lat: float, lon: float, radius_meters: int = 2000) -> str:
    time.sleep(1)
    categories = {
        "parks": '[leisure="park"]',
        "gyms": '[leisure="fitness_centre"]',
        "restaurants": '[amenity="restaurant"]',
        "grocery_stores": '[shop="supermarket"]',
        "transit_stops": '[highway="bus_stop"]',
        "schools": '[amenity="school"]',
    }
    results = {}
    overpass_url = "https://overpass-api.de/api/interpreter"
    for category, selector in categories.items():
        query = (
            f"[out:json][timeout:25];"
            f"node{selector}(around:{radius_meters},{lat},{lon});"
            f"out body;"
        )
        try:
            resp = httpx.post(overpass_url, data={"data": query}, timeout=30)
            resp.raise_for_status()
            elements = resp.json().get("elements", [])
            names = [
                e.get("tags", {}).get("name", "")
                for e in elements
                if e.get("tags", {}).get("name")
            ][:5]
            results[category] = {"count": len(elements), "names": names}
        except Exception:
            results[category] = {"count": 0, "names": []}
    lines = [f"POI data within {radius_meters}m of ({lat:.4f}, {lon:.4f}):"]
    for cat, data in results.items():
        label = cat.replace("_", " ").title()
        count = data["count"]
        names = data["names"]
        name_str = ", ".join(names) if names else "none named"
        lines.append(f"  {label}: {count} found — {name_str}")
    return "\n".join(lines)
