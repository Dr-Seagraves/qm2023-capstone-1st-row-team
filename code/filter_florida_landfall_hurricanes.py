"""
Filter hurricane economic impacts to Florida landfall hurricanes only.

Landfalls are derived from NHC HURDAT2 records (record identifier "L") and
matched to Florida using a US states GeoJSON boundary.
"""

from __future__ import annotations

import csv
import json
import re
from datetime import datetime
from typing import Iterable, Iterator, Tuple
from urllib.request import urlopen

from config_paths import PROCESSED_DATA_DIR

HURDAT_INDEX_URL = "https://www.nhc.noaa.gov/data/hurdat/"
FLORIDA_GEOJSON_URL = (
    "https://raw.githubusercontent.com/glynnbird/usstatesgeojson/master/florida.geojson"
)

INPUT_CSV = PROCESSED_DATA_DIR / "hurricane_economic_impacts_1980_2024.csv"
OUTPUT_CSV = (
    PROCESSED_DATA_DIR / "hurricane_economic_impacts_1980_2024_florida_landfall.csv"
)


def fetch_text(url: str) -> str:
    with urlopen(url) as response:
        return response.read().decode("utf-8", errors="replace")


def parse_hurdat_date(code: str) -> datetime:
    if len(code) == 8:
        return datetime.strptime(code, "%m%d%Y")
    if len(code) == 6:
        return datetime.strptime(code, "%m%d%y")
    raise ValueError(f"Unexpected HURDAT date code: {code}")


def latest_hurdat_url() -> str:
    index_html = fetch_text(HURDAT_INDEX_URL)
    pattern = re.compile(r"hurdat2-1851-\d{4}-(\d{6,8})\.txt")
    candidates = []
    for match in pattern.finditer(index_html):
        filename = match.group(0)
        date_code = match.group(1)
        try:
            date_value = parse_hurdat_date(date_code)
        except ValueError:
            continue
        candidates.append((date_value, filename))
    if not candidates:
        raise RuntimeError("Could not locate a HURDAT2 data file in the index.")
    candidates.sort(key=lambda item: item[0], reverse=True)
    latest_filename = candidates[0][1]
    return f"{HURDAT_INDEX_URL}{latest_filename}"


def parse_latlon(value: str) -> float:
    value = value.strip()
    if value.endswith("N"):
        return float(value[:-1])
    if value.endswith("S"):
        return -float(value[:-1])
    if value.endswith("E"):
        return float(value[:-1])
    if value.endswith("W"):
        return -float(value[:-1])
    raise ValueError(f"Unexpected coordinate: {value}")


def point_in_ring(x: float, y: float, ring: Iterable[Tuple[float, float]]) -> bool:
    inside = False
    points = list(ring)
    if not points:
        return False
    for i in range(len(points)):
        x1, y1 = points[i]
        x2, y2 = points[(i + 1) % len(points)]
        intersects = (y1 > y) != (y2 > y) and (
            x < (x2 - x1) * (y - y1) / (y2 - y1 + 1e-12) + x1
        )
        if intersects:
            inside = not inside
    return inside


def point_in_polygon(x: float, y: float, rings: list[list[list[float]]]) -> bool:
    if not rings:
        return False
    if not point_in_ring(x, y, rings[0]):
        return False
    for hole in rings[1:]:
        if point_in_ring(x, y, hole):
            return False
    return True


def point_in_geometry(x: float, y: float, geometry: dict) -> bool:
    geom_type = geometry.get("type")
    coords = geometry.get("coordinates", [])
    if geom_type == "Polygon":
        return point_in_polygon(x, y, coords)
    if geom_type == "MultiPolygon":
        return any(point_in_polygon(x, y, polygon) for polygon in coords)
    return False


def florida_geometry() -> dict:
    geojson_text = fetch_text(FLORIDA_GEOJSON_URL)
    geojson = json.loads(geojson_text)
    if geojson.get("type") == "Feature":
        return geojson.get("geometry", {})
    if geojson.get("type") == "FeatureCollection":
        for feature in geojson.get("features", []):
            if feature.get("properties", {}).get("name") == "Florida":
                return feature.get("geometry", {})
    raise RuntimeError("Florida geometry not found in Florida GeoJSON.")


def hurdat_florida_landfalls() -> set[Tuple[str, int]]:
    hurdat_url = latest_hurdat_url()
    hurdat_text = fetch_text(hurdat_url)
    fl_geom = florida_geometry()

    try:
        from shapely.geometry import Point, shape

        # Buffer the coastline slightly to capture landfall points just offshore.
        florida_shape = shape(fl_geom).buffer(0.05)

        def in_florida(lon: float, lat: float) -> bool:
            return florida_shape.covers(Point(lon, lat))

    except Exception:

        def in_florida(lon: float, lat: float) -> bool:
            return point_in_geometry(lon, lat, fl_geom)

    landfall_names = set()
    lines = hurdat_text.splitlines()
    idx = 0
    while idx < len(lines):
        header = [part.strip() for part in lines[idx].split(",")]
        storm_id = header[0]
        name = header[1].strip().upper()
        entries = int(header[2])
        year = int(storm_id[4:8])
        idx += 1
        for _ in range(entries):
            record = [part.strip() for part in lines[idx].split(",")]
            record_id = record[2]
            if record_id == "L":
                lat = parse_latlon(record[4])
                lon = parse_latlon(record[5])
                if in_florida(lon, lat):
                    landfall_names.add((name, year))
            idx += 1
    return landfall_names


def iter_filtered_rows(landfall_names: set[Tuple[str, int]]) -> Iterator[dict]:
    with INPUT_CSV.open("r", newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            event_name = row.get("event_name", "")
            if not (event_name.startswith("Hurricane ") or event_name.startswith("Tropical Storm ")):
                continue
            year = int(row.get("data_year", 0))
            storm_name = (
                event_name.replace("Hurricane ", "", 1)
                .replace("Tropical Storm ", "", 1)
                .strip()
                .upper()
            )
            if (storm_name, year) in landfall_names:
                yield row


def main() -> None:
    landfall_names = hurdat_florida_landfalls()
    with INPUT_CSV.open("r", newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        fieldnames = reader.fieldnames or []

    rows = list(iter_filtered_rows(landfall_names))

    with OUTPUT_CSV.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    print(f"Wrote {len(rows)} rows to {OUTPUT_CSV}")


if __name__ == "__main__":
    main()
