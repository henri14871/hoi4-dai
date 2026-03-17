"""Semantic tests for the dynamic theatre allocation model."""

import copy
import re
import sys
import tempfile
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent.resolve()
sys.path.insert(0, str(PROJECT_ROOT))

from generator.config_loader import load_config, load_profile, merge_profile_into_config
from generator.renderer import render_all

CONFIG_DIR = PROJECT_ROOT / "config"
PROFILES_DIR = PROJECT_ROOT / "profiles"
TEMPLATE_DIR = PROJECT_ROOT / "generator" / "templates"


def _render_profile(valid_areas=None):
    config = load_config(CONFIG_DIR)
    profile = load_profile(PROFILES_DIR / "vanilla.yaml")
    merged = copy.deepcopy(merge_profile_into_config(config, profile))
    if valid_areas is not None:
        merged["valid_areas"] = list(valid_areas)

    tempdir = tempfile.TemporaryDirectory(prefix="dai_dynamic_theatre_")
    output_dir = Path(tempdir.name)
    render_all(merged, TEMPLATE_DIR, output_dir)
    return tempdir, output_dir, merged


def _extract_area_factor_values(content: str, area_name: str) -> list[int]:
    pattern = re.compile(
        rf"dai_theatre_{re.escape(area_name)}_f\d+\s*=\s*\{{.*?value = (-?\d+)\s*\n\t\}}",
        re.S,
    )
    return [int(match.group(1)) for match in pattern.finditer(content)]


def test_area_priority_policy_is_symmetric():
    tempdir, output_dir, merged = _render_profile()
    try:
        frontline = (output_dir / "common/ai_strategy/dai_warfare_frontline.txt").read_text(
            encoding="utf-8"
        )
    finally:
        tempdir.cleanup()

    expected_values = [35, 20, 15, 15, 15, 10, 10]

    assert "_intel =" not in frontline
    assert "European theatre" not in frontline

    for area_name in merged["valid_areas"]:
        assert f"dai_theatre_{area_name} = {{" in frontline
        assert re.search(
            rf"dai_theatre_{re.escape(area_name)}\s*=\s*\{{.*?value = 0\s*\n\t\}}",
            frontline,
            re.S,
        )
        assert _extract_area_factor_values(frontline, area_name) == expected_values


def test_owned_theatre_count_generation_uses_valid_areas():
    tempdir, output_dir, _merged = _render_profile(valid_areas=["europe", "asia", "pacific"])
    try:
        core_effects = (output_dir / "common/scripted_effects/dai_core_effects.txt").read_text(
            encoding="utf-8"
        )
    finally:
        tempdir.cleanup()

    assert "set_variable = { dai_owned_theatre_count = 0 }" in core_effects
    assert "dai_t_continent_count" not in core_effects
    assert "check_variable = { dai_owned_theatre_count > 1 }" in core_effects

    for expected in ("europe", "asia", "oceania"):
        assert f"is_on_continent = {expected}" in core_effects

    for unexpected in ("africa", "north_america", "south_america", "middle_east"):
        assert f"is_on_continent = {unexpected}" not in core_effects


def test_offensive_front_control_is_gated_by_crisis_signals():
    tempdir, output_dir, _merged = _render_profile()
    try:
        frontline = (output_dir / "common/ai_strategy/dai_warfare_frontline.txt").read_text(
            encoding="utf-8"
        )
    finally:
        tempdir.cleanup()

    for strategy in (
        "dai_front_ctrl_pocket_closure",
        "dai_front_ctrl_opportunity_exploit",
        "dai_front_ctrl_full_offensive",
        "dai_front_ctrl_offensive_push",
    ):
        block_match = re.search(rf"{strategy}\s*=\s*\{{.*?\n\}}", frontline, re.S)
        assert block_match, f"Missing strategy block: {strategy}"
        block = block_match.group(0)
        assert "dai_capital_threatened < 0.5" in block
        assert "dai_supply_strain <" in block

    assert "dai_fuel_status > 0.4" in frontline
    assert "dai_fuel_status > 0.5" in frontline
