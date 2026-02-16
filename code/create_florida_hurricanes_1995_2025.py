"""
Create a CSV of Florida hurricanes (1995-2025) using NOAA Historical Hurricane Tracks API.
"""

from __future__ import annotations

import csv
import json
from urllib.request import Request, urlopen

from shapely.geometry import shape

from config_paths import PROCESSED_DATA_DIR

FLORIDA_GEOJSON_URL = "https://raw.githubusercontent.com/glynnbird/usstatesgeojson/master/florida.geojson"
API_URL = "https://coast.noaa.gov/hurricanes/api/v1/search/stormsByAOI"

BUFFER_NMI = 60
METERS_PER_NMI = 1852
YEAR_START = 1995
YEAR_END = 2025

OUTPUT_CSV = PROCESSED_DATA_DIR / "florida_hurricanes_1995_2025_noaa.csv"

HURRICANE_CATEGORIES = {"H1", "H2", "H3", "H4", "H5"}


def fetch_json(url: str) -> dict:
    with urlopen(url) as resp:
        return json.loads(resp.read().decode("utf-8"))


def build_aoi_wkt() -> str:
    florida_geo = fetch_json(FLORIDA_GEOJSON_URL)
    florida_shape = shape(florida_geo["geometry"])
    return f"SRID=4326;{florida_shape.wkt}"


def fetch_storms(aoi_wkt: str, buffer_nmi: int) -> list[dict]:
    payload = json.dumps(
        {"aoi": aoi_wkt, "buffer": round(buffer_nmi * METERS_PER_NMI)}
    ).encode("utf-8")
    request = Request(
        API_URL,
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urlopen(request) as resp:
        data = json.loads(resp.read().decode("utf-8"))
    return data.get("data", {}).get("storms", [])


def storm_in_year_range(storm: dict) -> bool:
    years = storm.get("yearsInAOI", [])
    return any(YEAR_START <= year <= YEAR_END for year in years)


def storm_is_hurricane(storm: dict) -> bool:
    categories = set(storm.get("categoriesInAOI", []))
    return bool(categories & HURRICANE_CATEGORIES)


def format_list(values: list) -> str:
    return ";".join(str(value) for value in sorted(values))


def main() -> None:
    aoi_wkt = build_aoi_wkt()
    storms = fetch_storms(aoi_wkt, BUFFER_NMI)

    rows = []
    for storm in storms:
        if not storm_in_year_range(storm):
            continue
        if not storm_is_hurricane(storm):
            continue
        rows.append(
            {
                "storm_id": storm.get("stormID"),
                "name": storm.get("name"),
                "date_range": storm.get("dateRange"),
                "max_category": storm.get("category"),
                "max_wind_speed": storm.get("maxWindSpeed"),
                "min_pressure": storm.get("minPressure"),
                "categories_in_aoi": format_list(storm.get("categoriesInAOI", [])),
                "years_in_aoi": format_list(storm.get("yearsInAOI", [])),
                "months_in_aoi": format_list(storm.get("monthsinAOI", [])),
                "details_url": storm.get("detailsURL"),
                "report_url": storm.get("reportURL"),
            }
        )

    fieldnames = [
        "storm_id",
        "name",
        "date_range",
        "max_category",
        "max_wind_speed",
        "min_pressure",
        "categories_in_aoi",
        "years_in_aoi",
        "months_in_aoi",
        "details_url",
        "report_url",
    ]

    with OUTPUT_CSV.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    print(f"Wrote {len(rows)} rows to {OUTPUT_CSV}")


if __name__ == "__main__":
    main()
