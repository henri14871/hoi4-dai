#!/usr/bin/env python3
"""
DAI Profile Generator
Scans a HOI4 mod directory and generates a draft compatibility profile YAML.

Usage:
    python profile_generator.py --scan /path/to/mod
    python profile_generator.py --scan /path/to/mod --base vanilla
    python profile_generator.py --validate profiles/mymod.yaml --mod /path/to/mod
"""

import argparse
import re
import sys
from pathlib import Path

import yaml

# Keyword heuristics for auto-mapping
TECH_CATEGORY_MAP = {
    "BRANCH_INFANTRY": ["infantry", "small_arms", "rifle", "infantry_weapons"],
    "BRANCH_ARMOUR": ["armor", "armour", "tank", "panzer", "armored", "armoured"],
    "BRANCH_AIR": ["air", "fighter", "bomber", "cas", "aviation", "light_air", "medium_air", "heavy_air", "naval_air"],
    "BRANCH_NAVAL": ["naval", "navy", "ship", "submarine", "torpedo", "dd_tech", "cl_tech", "bb_tech", "ss_tech"],
    "BRANCH_INDUSTRY": ["industry", "industrial", "construction", "factory", "synth", "resource"],
    "BRANCH_ELECTRONICS": ["electronics", "electronic", "radar", "encryption", "computing", "radio"],
    "BRANCH_DOCTRINE": ["doctrine", "land_doctrine", "naval_doctrine", "air_doctrine"],
}

SUB_UNIT_MAP = {
    "ROLE_LINE_INFANTRY": ["infantry", "militia", "foot_infantry"],
    "ROLE_BREAKTHROUGH": ["medium_armor", "heavy_armor", "modern_armor", "super_heavy_armor", "tank", "panzer"],
    "ROLE_MOBILE": ["motorized", "mechanized", "motorised", "mechanised", "mot_", "mech_"],
    "ROLE_GARRISON": ["cavalry", "military_police", "garrison", "camelry"],
    "ROLE_SPECIAL": ["marine", "mountaineers", "paratrooper", "ranger", "commando", "amphibious"],
}

EQUIPMENT_MAP = {
    "EQUIP_INFANTRY": ["infantry_equipment", "rifle", "small_arms"],
    "EQUIP_ARMOUR": ["tank_chassis", "light_tank", "medium_tank", "heavy_tank", "modern_tank"],
    "EQUIP_FIGHTER": ["fighter", "single_engine_airframe"],
    "EQUIP_CAS": ["cas", "close_air"],
    "EQUIP_BOMBER": ["bomber", "twin_engine_airframe", "quad_engine_airframe", "strategic_bomber"],
    "EQUIP_CAPITAL_SHIP": ["battleship", "heavy_cruiser", "ship_hull_heavy", "ship_hull_carrier", "carrier"],
    "EQUIP_SCREEN": ["destroyer", "light_cruiser", "ship_hull_light", "ship_hull_cruiser"],
    "EQUIP_SUBMARINE": ["submarine", "ship_hull_submarine"],
    "EQUIP_CONVOY": ["convoy"],
    "EQUIP_SUPPORT": ["support_equipment"],
    "EQUIP_ARTILLERY": ["artillery_equipment", "rocket_artillery"],
    "EQUIP_ANTI_TANK": ["anti_tank_equipment"],
    "EQUIP_ANTI_AIR": ["anti_air_equipment"],
    "EQUIP_MOTORIZED": ["motorized_equipment", "mechanized_equipment", "truck"],
}


def scan_directory_tokens(directory: Path, pattern: str = "*.txt") -> list[str]:
    """Scan .txt files for top-level token definitions (TOKEN = { ... })."""
    tokens = []
    if not directory.exists():
        return tokens

    for filepath in directory.glob(pattern):
        try:
            content = filepath.read_text(encoding="utf-8-sig", errors="replace")
        except Exception:
            continue

        # Match top-level tokens: word = {
        for match in re.finditer(r"^\s*(\w+)\s*=\s*\{", content, re.MULTILINE):
            token = match.group(1)
            if token not in ("if", "else", "else_if", "limit", "NOT", "OR", "AND", "modifier"):
                tokens.append(token)

    return list(set(tokens))


def scan_tech_categories(mod_dir: Path) -> list[str]:
    """Scan common/technology_tags/ for tech category tokens."""
    tech_dir = mod_dir / "common" / "technology_tags"
    if not tech_dir.exists():
        return []

    categories = []
    for filepath in tech_dir.glob("*.txt"):
        try:
            content = filepath.read_text(encoding="utf-8-sig", errors="replace")
        except Exception:
            continue

        # Tech categories are listed inside technology_categories = { ... }
        cat_match = re.search(r"technology_categories\s*=\s*\{([^}]+)\}", content, re.DOTALL)
        if cat_match:
            block = cat_match.group(1)
            for token in re.findall(r"\b(\w+)\b", block):
                if token not in ("technology_categories",):
                    categories.append(token)

    return list(set(categories))


def scan_sub_units(mod_dir: Path) -> list[str]:
    """Scan common/units/ (or common/sub_units/) for sub-unit type tokens."""
    units = []
    for subdir_name in ["units", "sub_units"]:
        units_dir = mod_dir / "common" / subdir_name
        if units_dir.exists():
            units.extend(scan_directory_tokens(units_dir))
    return list(set(units))


def scan_equipment(mod_dir: Path) -> list[str]:
    """Scan common/units/equipment/ for equipment archetype tokens."""
    equip_dir = mod_dir / "common" / "units" / "equipment"
    if not equip_dir.exists():
        return []

    archetypes = []
    for filepath in equip_dir.rglob("*.txt"):
        try:
            content = filepath.read_text(encoding="utf-8-sig", errors="replace")
        except Exception:
            continue

        # Find tokens with is_archetype = yes
        for match in re.finditer(
            r"(\w+)\s*=\s*\{[^}]*?is_archetype\s*=\s*yes", content, re.DOTALL
        ):
            archetypes.append(match.group(1))

        # Also grab top-level equipment definitions
        for match in re.finditer(r"^(\w+)\s*=\s*\{", content, re.MULTILINE):
            token = match.group(1)
            if token not in archetypes and "_equipment" in token or "chassis" in token:
                archetypes.append(token)

    return list(set(archetypes))


def scan_ideologies(mod_dir: Path) -> list[str]:
    """Scan common/ideologies/ for ideology tokens."""
    ideo_dir = mod_dir / "common" / "ideologies"
    return scan_directory_tokens(ideo_dir) if ideo_dir.exists() else []


def auto_map(tokens: list[str], keyword_map: dict[str, list[str]]) -> dict[str, list[str]]:
    """Map scanned tokens to abstract categories using keyword heuristics."""
    mapping: dict[str, list[str]] = {cat: [] for cat in keyword_map}
    unmapped = []

    for token in tokens:
        token_lower = token.lower()
        matched = False
        for category, keywords in keyword_map.items():
            for keyword in keywords:
                if keyword in token_lower:
                    if token not in mapping[category]:
                        mapping[category].append(token)
                    matched = True
                    break
            if matched:
                break
        if not matched:
            unmapped.append(token)

    return mapping, unmapped


def generate_profile(mod_dir: Path, profile_name: str, base_profile: dict = None) -> dict:
    """Generate a draft profile by scanning a mod directory."""
    print(f"Scanning: {mod_dir}")

    # Scan all content types
    tech_cats = scan_tech_categories(mod_dir)
    sub_units = scan_sub_units(mod_dir)
    equipment = scan_equipment(mod_dir)
    ideologies = scan_ideologies(mod_dir)

    print(f"  Found {len(tech_cats)} tech categories")
    print(f"  Found {len(sub_units)} sub-unit types")
    print(f"  Found {len(equipment)} equipment archetypes")
    print(f"  Found {len(ideologies)} ideologies")

    # Auto-map
    tech_mapping, tech_unmapped = auto_map(tech_cats, TECH_CATEGORY_MAP)
    unit_mapping, unit_unmapped = auto_map(sub_units, SUB_UNIT_MAP)
    equip_mapping, equip_unmapped = auto_map(equipment, EQUIPMENT_MAP)

    if tech_unmapped:
        print(f"  Unmapped tech categories: {tech_unmapped}")
    if unit_unmapped:
        print(f"  Unmapped sub-units: {unit_unmapped}")
    if equip_unmapped:
        print(f"  Unmapped equipment: {equip_unmapped}")

    # Build profile
    profile = {
        "profile_name": profile_name,
        "game_version": "1.15.*",
        "description": f"Auto-generated profile for {profile_name}",
        "tech_categories": tech_mapping,
        "sub_units": unit_mapping,
        "equipment": equip_mapping,
        "ideologies": ideologies,
    }

    return profile


def main():
    parser = argparse.ArgumentParser(description="DAI Profile Generator")
    parser.add_argument("--scan", type=Path, help="Path to mod directory to scan")
    parser.add_argument("--base", default=None, help="Base profile name (e.g., vanilla)")
    parser.add_argument("--output", type=Path, default=None, help="Output YAML path")
    parser.add_argument("--name", default=None, help="Profile name")
    parser.add_argument("--validate", type=Path, default=None, help="Validate existing profile")
    parser.add_argument("--mod", type=Path, default=None, help="Mod directory for validation")
    args = parser.parse_args()

    if args.scan:
        mod_dir = args.scan.resolve()
        if not mod_dir.exists():
            print(f"ERROR: Directory not found: {mod_dir}")
            return 1

        profile_name = args.name or mod_dir.name.lower().replace(" ", "_")
        profile = generate_profile(mod_dir, profile_name)

        if args.output:
            output_path = args.output
        else:
            output_path = Path(f"profiles/{profile_name}.yaml")

        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(f"# Auto-generated DAI profile for {profile_name}\n")
            f.write(f"# Review and adjust mappings before use\n\n")
            yaml.dump(profile, f, default_flow_style=False, sort_keys=False)

        print(f"\nProfile written to: {output_path}")
        print("Review the output and fix any UNMAPPED categories before building.")
        return 0

    elif args.validate:
        if not args.mod:
            print("ERROR: --mod required with --validate")
            return 1

        profile = yaml.safe_load(args.validate.read_text(encoding="utf-8"))
        # TODO: validate profile against mod content
        print(f"Profile {args.validate.name} loaded successfully")
        print(f"  Tech categories: {len(profile.get('tech_categories', {}))}")
        print(f"  Sub-units: {len(profile.get('sub_units', {}))}")
        print(f"  Equipment: {len(profile.get('equipment', {}))}")
        return 0

    else:
        parser.print_help()
        return 1


if __name__ == "__main__":
    sys.exit(main())
