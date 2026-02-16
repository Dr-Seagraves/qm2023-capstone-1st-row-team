from __future__ import annotations

import argparse
import hashlib
import os
from pathlib import Path
from urllib.parse import urlparse
from urllib.request import urlopen, urlretrieve


def read_sources(sources_file: Path) -> list[str]:
    if not sources_file.exists():
        raise FileNotFoundError(f"Sources file not found: {sources_file}")

    urls: list[str] = []
    for line in sources_file.read_text(encoding="utf-8").splitlines():
        cleaned = line.strip()
        if not cleaned or cleaned.startswith("#"):
            continue
        urls.append(cleaned)
    return urls


def filename_from_url(url: str, fallback_index: int) -> str:
    parsed = urlparse(url)
    name = os.path.basename(parsed.path)
    if name:
        return name
    digest = hashlib.sha256(url.encode("utf-8")).hexdigest()[:10]
    return f"source_{fallback_index:02d}_{digest}.bin"


def fetch_url(url: str, dest_dir: Path, index: int) -> Path:
    dest_dir.mkdir(parents=True, exist_ok=True)
    filename = filename_from_url(url, index)
    dest_path = dest_dir / filename

    # Use a streamed open first to validate reachability for non-file URLs.
    try:
        with urlopen(url) as response:
            content_type = response.headers.get("Content-Type", "")
            if "text/html" in content_type and not filename.endswith(".html"):
                filename = f"{filename}.html"
                dest_path = dest_dir / filename
    except Exception:
        # Fall back to a direct download attempt; urlretrieve will raise on failure.
        pass

    urlretrieve(url, dest_path)
    return dest_path


def main() -> int:
    parser = argparse.ArgumentParser(description="Fetch datasets from a list of URLs.")
    parser.add_argument(
        "--sources",
        default=str(Path(__file__).resolve().parents[1] / "config" / "dataset_sources.txt"),
        help="Path to dataset_sources.txt",
    )
    parser.add_argument(
        "--output",
        default=str(Path(__file__).resolve().parents[1] / "data"),
        help="Base data directory; downloads are saved under the raw subfolder",
    )

    args = parser.parse_args()
    sources_file = Path(args.sources).resolve()
    output_dir = Path(args.output).resolve()
    if output_dir.name != "raw":
        output_dir = output_dir / "raw"

    urls = read_sources(sources_file)
    if not urls:
        raise ValueError(f"No URLs found in {sources_file}")

    print(f"Found {len(urls)} source URLs.")
    for index, url in enumerate(urls, start=1):
        print(f"Downloading {url}...")
        saved_path = fetch_url(url, output_dir, index)
        print(f"Saved to {saved_path}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
