#!/usr/bin/env python3
"""
DAI - Smarter AI: Build Pipeline
Reads YAML configs + ALL mod profiles, renders Jinja2 templates into HOI4 script files.
All profiles are shipped in a single mod — runtime game rules select which is active.

Usage:
    python build.py                          # Build with all profiles in profiles/
    python build.py --validate               # Validate output after building
    python build.py --clean                  # Clean generated files before building
"""

import argparse
import shutil
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.resolve()
CONFIG_DIR = PROJECT_ROOT / "config"
PROFILES_DIR = PROJECT_ROOT / "profiles"
TEMPLATE_DIR = PROJECT_ROOT / "generator" / "templates"
OUTPUT_DIR = PROJECT_ROOT

sys.path.insert(0, str(PROJECT_ROOT))

from generator.config_loader import load_config, load_all_profiles, merge_all_profiles_into_config
from generator.renderer import render_all, copy_static_files
from generator.validator import validate_output


def main():
    parser = argparse.ArgumentParser(description="DAI - Smarter AI Build Pipeline")
    parser.add_argument(
        "--validate", action="store_true",
        help="Validate generated output after building"
    )
    parser.add_argument(
        "--clean", action="store_true",
        help="Remove generated HOI4 files before building"
    )
    parser.add_argument(
        "--output", type=Path, default=None,
        help="Override output directory"
    )
    args = parser.parse_args()

    output_dir = args.output or OUTPUT_DIR

    print("DAI Build Pipeline v1.0")
    print(f"  Output: {output_dir}")
    print()

    # Clean if requested
    if args.clean:
        generated_dirs = [
            output_dir / "common",
            output_dir / "events",
            output_dir / "localisation",
        ]
        generated_files = [
            output_dir / "descriptor.mod",
        ]
        print("Cleaning generated files...")
        for d in generated_dirs:
            if d.exists():
                shutil.rmtree(d)
                print(f"  Removed {d.relative_to(output_dir)}/")
        for f in generated_files:
            if f.exists():
                f.unlink()
                print(f"  Removed {f.relative_to(output_dir)}")

    # Load config
    print("Loading configuration...")
    try:
        config = load_config(CONFIG_DIR)
        print(f"  Core config loaded")
        print(f"  {len(config['presets'])} presets loaded")
        print(f"  {len(config['modules'])} modules loaded")
    except Exception as e:
        print(f"  ERROR: {e}")
        return 1

    # Load ALL profiles
    print("Loading profiles...")
    try:
        profiles = load_all_profiles(PROFILES_DIR)
        for p in profiles:
            default_marker = " (default)" if p.get("is_default") else ""
            print(f"  {p['profile_name']}{default_marker}")
        print(f"  {len(profiles)} profile(s) loaded")
    except Exception as e:
        print(f"  ERROR: {e}")
        return 1

    # Merge all profiles
    print("Merging profiles into config...")
    merged = merge_all_profiles_into_config(config, profiles)

    # Render
    print("Rendering templates...")
    try:
        generated = render_all(merged, TEMPLATE_DIR, output_dir)
        print(f"  Generated {len(generated)} files:")
        for f in generated:
            print(f"    {f}")
    except Exception as e:
        print(f"  ERROR: {e}")
        import traceback
        traceback.print_exc()
        return 1

    # Copy static files
    static_files = ["thumbnail.png"]
    copy_static_files(PROJECT_ROOT, output_dir, static_files)

    # Validate
    if args.validate:
        print()
        print("Validating output...")
        errors, warnings = validate_output(output_dir)

        for w in warnings:
            print(f"  WARNING: {w}")
        for e in errors:
            print(f"  ERROR: {e}")

        if errors:
            print(f"\n  VALIDATION FAILED: {len(errors)} error(s), {len(warnings)} warning(s)")
            return 1
        else:
            print(f"  VALIDATION PASSED: 0 errors, {len(warnings)} warning(s)")

    print()
    print(f"Build complete. Output at: {output_dir}")
    return 0


if __name__ == "__main__":
    try:
        import jinja2
    except ImportError:
        print("ERROR: jinja2 not installed. Run: pip install -r requirements.txt")
        sys.exit(1)

    sys.exit(main())
