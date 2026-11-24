from pathlib import Path
import cairosvg

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "tools" / "minigame_svg_source"
OUTPUT = ROOT / "assets" / "minigames"
OUTPUT.mkdir(parents=True, exist_ok=True)

SIZES = {
    "dirt_splatter": 768,
    "sponge": 768,
    "puzzle_overlay": 768,
    "paint_emblem": 768,
    "paintbrush": 768,
    "tool_wrench": 768,
    "tool_hammer": 768,
    "tool_gear": 768,
    "repair_crack": 768,
    "artifact_halo": 1024,
}

for name, size in SIZES.items():
    source = SOURCE / f"{name}.svg"
    if not source.is_file():
        raise SystemExit(f"Missing source illustration: {source}")
    target = OUTPUT / f"{name}.png"
    cairosvg.svg2png(
        url=str(source),
        write_to=str(target),
        output_width=size,
        output_height=size,
    )
    print(f"Generated {target.relative_to(ROOT)} ({size}x{size})")
