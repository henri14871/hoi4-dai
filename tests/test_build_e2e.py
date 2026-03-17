"""End-to-end build test for DAI."""

import shutil
import sys
import tempfile
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent.resolve()
sys.path.insert(0, str(PROJECT_ROOT))

from generator.config_loader import load_config, load_profile, merge_profile_into_config
from generator.renderer import render_all
from generator.validator import validate_output

CONFIG_DIR = PROJECT_ROOT / "config"
PROFILES_DIR = PROJECT_ROOT / "profiles"
TEMPLATE_DIR = PROJECT_ROOT / "generator" / "templates"


def test_full_build():
    """Test the complete build pipeline with vanilla profile."""
    # Use a temp directory so tests don't pollute the mod folder
    TEST_OUTPUT_DIR = Path(tempfile.mkdtemp(prefix="dai_test_"))

    # Load config
    config = load_config(CONFIG_DIR)
    profile = load_profile(PROFILES_DIR / "vanilla.yaml")
    merged = merge_profile_into_config(config, profile)

    # Render
    generated = render_all(merged, TEMPLATE_DIR, TEST_OUTPUT_DIR)
    print(f"Generated {len(generated)} files:")
    for f in generated:
        print(f"  {f}")

    # Verify expected files exist
    expected_files = [
        "descriptor.mod",
        "common/game_rules/dai_game_rules.txt",
        "common/scripted_triggers/dai_core_triggers.txt",
        "common/scripted_triggers/dai_research_triggers.txt",
        "common/scripted_triggers/dai_army_triggers.txt",
        "common/scripted_effects/dai_core_effects.txt",
        "common/scripted_effects/dai_research_effects.txt",
        "common/scripted_effects/dai_army_effects.txt",
        "common/on_actions/dai_on_actions.txt",
        "common/ai_strategy/dai_research_strategy.txt",
        "common/ai_strategy/dai_army_production.txt",
        "common/ai_strategy/dai_army_construction.txt",
        "common/ai_templates/dai_army_templates.txt",
        "common/ai_strategy/dai_warfare_land.txt",
        "common/ai_strategy/dai_warfare_naval.txt",
        "common/ai_strategy/dai_warfare_air.txt",
        "common/ai_strategy/dai_warfare_invasion.txt",
        "common/ai_strategy/dai_warfare_frontline.txt",
        "common/scripted_triggers/dai_warfare_triggers.txt",
        "common/scripted_effects/dai_warfare_effects.txt",
        "events/dai_core_events.txt",
        "events/dai_research_events.txt",
        "events/dai_army_events.txt",
        "events/dai_warfare_events.txt",
        "common/ai_strategy/dai_gs_diplomacy.txt",
        "common/ai_strategy/dai_gs_economy.txt",
        "common/ai_peace/dai_gs_peace.txt",
        "common/scripted_triggers/dai_gs_triggers.txt",
        "common/scripted_effects/dai_gs_effects.txt",
        "events/dai_gs_events.txt",
        "localisation/english/dai_l_english.yml",
    ]

    missing = []
    for expected in expected_files:
        if not (TEST_OUTPUT_DIR / expected).exists():
            missing.append(expected)

    if missing:
        print(f"\nMISSING FILES: {missing}")
        return False

    print("\nAll expected files generated.")

    # Validate
    errors, warnings = validate_output(TEST_OUTPUT_DIR)

    for w in warnings:
        print(f"  WARNING: {w}")
    for e in errors:
        print(f"  ERROR: {e}")

    if errors:
        print(f"\nVALIDATION FAILED: {len(errors)} error(s)")
        return False

    print(f"\nVALIDATION PASSED: 0 errors, {len(warnings)} warning(s)")

    # Clean up test output
    shutil.rmtree(TEST_OUTPUT_DIR)
    print("Test output cleaned up.")
    return True


if __name__ == "__main__":
    success = test_full_build()
    print("\n" + ("=" * 50))
    if success:
        print("E2E BUILD TEST: PASSED")
    else:
        print("E2E BUILD TEST: FAILED")
    sys.exit(0 if success else 1)
