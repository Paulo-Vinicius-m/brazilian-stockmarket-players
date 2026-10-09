#!/usr/bin/env python3
"""
CVM Data Downloader and Organizer
---------------------------------
Downloads Brazilian Securities and Exchange Commission (CVM) open data
for Publicly Traded Companies (CIA_ABERTA) Reference Forms (FRE).

Data sources:
- Annual FRE data (2010 - 2026):
  https://dados.cvm.gov.br/dados/CIA_ABERTA/DOC/FRE/DADOS/fre_cia_aberta_20**.zip
- Documentation / Metadata:
  https://dados.cvm.gov.br/dados/CIA_ABERTA/DOC/FRE/META/meta_fre_cia_aberta.zip
"""

import argparse
import os
import shutil
import ssl
import sys
import urllib.request
import zipfile
from pathlib import Path

BASE_DATA_URL = "https://dados.cvm.gov.br/dados/CIA_ABERTA/DOC/FRE/DADOS/fre_cia_aberta_{year}.zip"
META_URL = "https://dados.cvm.gov.br/dados/CIA_ABERTA/DOC/FRE/META/meta_fre_cia_aberta.zip"
DEFAULT_YEAR_START = 10  # 2010
DEFAULT_YEAR_END = 26    # 2026
USER_AGENT = "Mozilla/5.0 (compatible; CVMDataDownloader/1.0)"


def parse_year_input(year_args):
    """Normalize user-specified years into full 4-digit year strings (e.g., '2025')."""
    years = []
    for item in year_args:
        item = str(item).strip()
        if "-" in item:
            parts = item.split("-", 1)
            y_start = int(parts[0])
            y_end = int(parts[1])
            if y_start < 100:
                y_start += 2000
            if y_end < 100:
                y_end += 2000
            for y in range(y_start, y_end + 1):
                years.append(str(y))
        else:
            y = int(item)
            if y < 100:
                y += 2000
            years.append(str(y))
    return sorted(list(dict.fromkeys(years)))


def download_file(url, destination_path, dry_run=False):
    """Download a file with progress reporting."""
    if dry_run:
        print(f"[DRY-RUN] Would download: {url} -> {destination_path}")
        return True

    print(f"Downloading: {url}")
    ctx = ssl.create_default_context()
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})

    try:
        with urllib.request.urlopen(req, context=ctx, timeout=60) as response, \
             open(destination_path, "wb") as out_file:
            total_size = response.getheader("Content-Length")
            total_size = int(total_size) if total_size else None
            downloaded = 0
            block_size = 1024 * 64  # 64 KB

            while True:
                buffer = response.read(block_size)
                if not buffer:
                    break
                downloaded += len(buffer)
                out_file.write(buffer)

                if total_size:
                    pct = (downloaded / total_size) * 100
                    mb_down = downloaded / (1024 * 1024)
                    mb_total = total_size / (1024 * 1024)
                    sys.stdout.write(f"\r  -> Progress: {pct:5.1f}% ({mb_down:6.2f}/{mb_total:6.2f} MB)")
                    sys.stdout.flush()
                else:
                    mb_down = downloaded / (1024 * 1024)
                    sys.stdout.write(f"\r  -> Downloaded: {mb_down:6.2f} MB")
                    sys.stdout.flush()
            print()
        return True
    except Exception as e:
        print(f"\n  [ERROR] Failed to download {url}: {e}")
        if os.path.exists(destination_path):
            os.remove(destination_path)
        return False


def extract_zip(zip_path, extract_dir, dry_run=False):
    """Extract zip archive into destination directory."""
    if dry_run:
        print(f"[DRY-RUN] Would extract {zip_path} -> {extract_dir}")
        return True

    print(f"Extracting to: {extract_dir}")
    os.makedirs(extract_dir, exist_ok=True)
    try:
        with zipfile.ZipFile(zip_path, "r") as zip_ref:
            zip_ref.extractall(extract_dir)
        return True
    except Exception as e:
        print(f"  [ERROR] Failed to extract {zip_path}: {e}")
        return False


def move_existing_legacy_dirs(root_dir, output_dir, dry_run=False):
    """
    Move existing data directories from the project root into output_dir
    to keep the repository clean.
    """
    root_path = Path(root_dir).resolve()
    out_path = Path(output_dir).resolve()

    if root_path == out_path:
        return

    items_to_check = [
        p for p in root_path.glob("fre_cia_aberta_*") if p.is_dir() and p != out_path
    ]
    meta_path = root_path / "meta_fre_cia_aberta"
    if meta_path.is_dir() and meta_path != out_path:
        items_to_check.append(meta_path)

    for item in items_to_check:
        target = out_path / item.name
        if target.exists():
            print(f"[SKIP] Target already exists in data directory: {target}")
            continue

        if dry_run:
            print(f"[DRY-RUN] Would move existing directory: {item} -> {target}")
        else:
            print(f"Moving legacy directory to data/: {item.name} -> {target}")
            out_path.mkdir(parents=True, exist_ok=True)
            shutil.move(str(item), str(target))


def process_year(year, output_dir, keep_zips=False, force=False, dry_run=False):
    """Download and extract annual FRE data for a given year."""
    target_extract_dir = os.path.join(output_dir, f"fre_cia_aberta_{year}")
    zip_dest = os.path.join(output_dir, f"fre_cia_aberta_{year}.zip")

    if os.path.exists(target_extract_dir) and not force:
        print(f"[SKIP] Directory already exists: {target_extract_dir} (use --force to overwrite)")
        return True

    url = BASE_DATA_URL.format(year=year)
    if not download_file(url, zip_dest, dry_run=dry_run):
        return False

    success = extract_zip(zip_dest, target_extract_dir, dry_run=dry_run)

    if not keep_zips and not dry_run and os.path.exists(zip_dest):
        os.remove(zip_dest)

    return success


def process_metadata(output_dir, keep_zips=False, force=False, dry_run=False):
    """Download and extract metadata documentation."""
    target_extract_dir = os.path.join(output_dir, "meta_fre_cia_aberta")
    zip_dest = os.path.join(output_dir, "meta_fre_cia_aberta.zip")

    if os.path.exists(target_extract_dir) and not force:
        print(f"[SKIP] Directory already exists: {target_extract_dir} (use --force to overwrite)")
        return True

    if not download_file(META_URL, zip_dest, dry_run=dry_run):
        return False

    success = extract_zip(zip_dest, target_extract_dir, dry_run=dry_run)

    if not keep_zips and not dry_run and os.path.exists(zip_dest):
        os.remove(zip_dest)

    return success


def main():
    parser = argparse.ArgumentParser(
        description="Download and organize CVM FRE CIA_ABERTA open data into a local data directory."
    )
    parser.add_argument(
        "--output-dir",
        default="data",
        help="Target directory for downloaded data (default: 'data').",
    )
    parser.add_argument(
        "--years",
        nargs="+",
        help=(
            "Specific year(s) or ranges to download (e.g. '--years 2025 2026' or '--years 10-26'). "
            f"Defaults to all years from 20{DEFAULT_YEAR_START} to 20{DEFAULT_YEAR_END}."
        ),
    )
    parser.add_argument(
        "--skip-meta",
        action="store_true",
        help="Skip downloading metadata / documentation.",
    )
    parser.add_argument(
        "--meta-only",
        action="store_true",
        help="Download only metadata / documentation and exit.",
    )
    parser.add_argument(
        "--keep-zips",
        action="store_true",
        help="Keep downloaded .zip files after extraction.",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Re-download and overwrite existing files.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be downloaded without actually fetching files.",
    )
    parser.add_argument(
        "--move-existing",
        action="store_true",
        default=True,
        help="Move existing data folders from root into the data directory (default: True).",
    )
    parser.add_argument(
        "--no-move-existing",
        dest="move_existing",
        action="store_false",
        help="Do not move existing root data folders.",
    )

    args = parser.parse_args()

    output_dir = os.path.abspath(args.output_dir)
    if not args.dry_run:
        os.makedirs(output_dir, exist_ok=True)
    project_root = os.path.abspath(os.path.dirname(__file__) or ".")

    print("=" * 60)
    print(" CVM FRE Data Downloader & Organizer")
    print(f" Target Directory: {output_dir}")
    print("=" * 60)

    # Move existing legacy directories if present in root
    if args.move_existing:
        move_existing_legacy_dirs(project_root, output_dir, dry_run=args.dry_run)

    # Process metadata
    if not args.skip_meta:
        print("\n--- Metadata & Documentation ---")
        process_metadata(
            output_dir,
            keep_zips=args.keep_zips,
            force=args.force,
            dry_run=args.dry_run,
        )

    if args.meta_only:
        print("\nDone! Metadata fetched.")
        return

    # Determine years to process
    if args.years:
        years = parse_year_input(args.years)
    else:
        years = [f"20{y:02d}" for y in range(DEFAULT_YEAR_START, DEFAULT_YEAR_END + 1)]

    print(f"\n--- Annual FRE Datasets ({len(years)} years: {', '.join(years)}) ---")
    for year in years:
        process_year(
            year,
            output_dir,
            keep_zips=args.keep_zips,
            force=args.force,
            dry_run=args.dry_run,
        )

    print("\n" + "=" * 60)
    print("Data download and organization process finished!")
    print(f"All data files are stored in: {output_dir}")
    print("=" * 60)


if __name__ == "__main__":
    main()
