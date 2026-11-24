#!/usr/bin/env python3
"""Re-encode JPEG assets to a conservative baseline format for Godot import."""

from pathlib import Path
import sys

from PIL import Image


def normalize_jpegs(asset_root: Path) -> int:
    converted = 0
    for path in sorted(asset_root.rglob("*")):
        if not path.is_file() or path.suffix.lower() not in (".jpg", ".jpeg"):
            continue
        try:
            with Image.open(path) as source:
                source.load()
                normalized = source.convert("RGB")
            normalized.save(
                path,
                format="JPEG",
                quality=94,
                optimize=True,
                progressive=False,
                subsampling=0,
            )
            with Image.open(path) as check:
                check.verify()
                if check.format != "JPEG":
                    raise ValueError("output is not JPEG")
            converted += 1
            print(f"Normalized JPEG: {path}")
        except Exception as exc:
            raise SystemExit(f"Cannot normalize JPEG asset {path}: {exc}") from exc
    return converted


if __name__ == "__main__":
    root = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("assets")
    if not root.is_dir():
        raise SystemExit(f"Asset directory does not exist: {root}")
    print(f"Normalized {normalize_jpegs(root)} JPEG assets.")
