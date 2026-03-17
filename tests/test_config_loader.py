"""Tests for the DAI config loader."""

import sys
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent.resolve()
sys.path.insert(0, str(PROJECT_ROOT))

from generator.config_loader import load_config, load_profile, merge_profile_into_config

CONFIG_DIR = PROJECT_ROOT / "config"
PROFILES_DIR = PROJECT_ROOT / "profiles"


def test_load_config():
    """Test that config loads core, presets, and modules."""
    config = load_config(CONFIG_DIR)

    assert "core" in config, "Missing 'core' in config"
    assert "presets" in config, "Missing 'presets' in config"
    assert "modules" in config, "Missing 'modules' in config"

    # Core
    assert "gps_formula" in config["core"], "Missing GPS formula"
    assert "competence_mapping" in config["core"], "Missing competence mapping"
    assert "evaluation" in config["core"], "Missing evaluation config"

    # Presets
    assert len(config["presets"]) >= 4, f"Expected at least 4 presets, got {len(config['presets'])}"
    preset_names = [p["preset_name"] for p in config["presets"]]
    assert "balanced" in preset_names, "Missing 'balanced' preset"
    assert "competitive" in preset_names, "Missing 'competitive' preset"

    # Modules
    assert len(config["modules"]) >= 4, f"Expected at least 4 modules, got {len(config['modules'])}"
    module_names = [m["module_name"] for m in config["modules"]]
    assert "research" in module_names, "Missing 'research' module"
    assert "army" in module_names, "Missing 'army' module"
    assert "warfare" in module_names, "Missing 'warfare' module"
    assert "grand_strategy" in module_names, "Missing 'grand_strategy' module"

    print("PASS: test_load_config")


def test_load_profile():
    """Test that vanilla profile loads with required keys."""
    profile = load_profile(PROFILES_DIR / "vanilla.yaml")

    assert profile["profile_name"] == "vanilla"
    assert "tech_categories" in profile
    assert "sub_units" in profile
    assert "equipment" in profile
    assert "ideologies" in profile

    # Check tech categories have content
    assert len(profile["tech_categories"]["BRANCH_INFANTRY"]) > 0, "Empty BRANCH_INFANTRY"
    assert len(profile["tech_categories"]["BRANCH_ARMOUR"]) > 0, "Empty BRANCH_ARMOUR"

    # Check sub-units
    assert "infantry" in profile["sub_units"]["ROLE_LINE_INFANTRY"]

    print("PASS: test_load_profile")


def test_merge_profile():
    """Test that merging resolves abstract categories."""
    config = load_config(CONFIG_DIR)
    profile = load_profile(PROFILES_DIR / "vanilla.yaml")
    merged = merge_profile_into_config(config, profile)

    assert "profile" in merged
    assert "resolved_branches" in merged
    assert len(merged["resolved_branches"]) > 0

    # Check that branches have concrete tech categories
    for branch in merged["resolved_branches"]:
        assert "concrete_tech_categories" in branch, f"Missing concrete IDs for {branch['abstract']}"
        assert len(branch["concrete_tech_categories"]) > 0, f"Empty concrete IDs for {branch['abstract']}"

    # Check resolved sub-units
    assert "ROLE_LINE_INFANTRY" in merged["resolved_sub_units"]

    print("PASS: test_merge_profile")


if __name__ == "__main__":
    test_load_config()
    test_load_profile()
    test_merge_profile()
    print("\nAll config loader tests passed!")
