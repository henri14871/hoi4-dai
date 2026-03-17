"""
DAI Config Loader
Loads YAML configurations and ALL mod profiles, resolves abstract categories
per-profile for multi-profile output.
"""

from pathlib import Path
from typing import Any

import yaml


def load_yaml(path: Path) -> dict:
    """Load a single YAML file."""
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def load_config(config_dir: Path) -> dict:
    """
    Load all YAML configs from config/, config/presets/, config/modules/.
    Returns a merged dict with keys: core, presets (list), modules (list).
    """
    config: dict[str, Any] = {}

    core_path = config_dir / "core.yaml"
    if not core_path.exists():
        raise FileNotFoundError(f"Core config not found: {core_path}")
    config["core"] = load_yaml(core_path)

    presets_dir = config_dir / "presets"
    config["presets"] = []
    if presets_dir.exists():
        for p in sorted(presets_dir.glob("*.yaml")):
            config["presets"].append(load_yaml(p))

    modules_dir = config_dir / "modules"
    config["modules"] = []
    if modules_dir.exists():
        for m in sorted(modules_dir.glob("*.yaml")):
            config["modules"].append(load_yaml(m))

    # Load engine define overrides (optional)
    defines_path = config_dir / "defines.yaml"
    if defines_path.exists():
        config["defines"] = load_yaml(defines_path).get("defines", {})
    else:
        config["defines"] = {}

    return config


def load_profile(profile_path: Path) -> dict:
    """
    Load a mod compatibility profile.
    Validates that required mapping sections exist.
    """
    if not profile_path.exists():
        raise FileNotFoundError(f"Profile not found: {profile_path}")

    profile = load_yaml(profile_path)

    required_keys = ["profile_name", "tech_categories", "sub_units", "equipment", "ideologies"]
    missing = [k for k in required_keys if k not in profile]
    if missing:
        raise ValueError(f"Profile {profile_path.name} missing required keys: {missing}")

    return profile


def load_all_profiles(profiles_dir: Path) -> list[dict]:
    """
    Load every profile YAML from the profiles/ directory.
    Returns a list of profile dicts sorted by priority (lowest first = default).
    """
    profiles = []
    if profiles_dir.exists():
        for p in sorted(profiles_dir.glob("*.yaml")):
            try:
                profile = load_profile(p)
                profiles.append(profile)
            except ValueError as e:
                print(f"  WARNING: Skipping {p.name}: {e}")

    # Sort: default (is_default=true / priority=0) first, then by priority
    profiles.sort(key=lambda p: p.get("priority", 100))
    return profiles


def resolve_branches_for_profile(profile: dict, research_module: dict) -> list[dict]:
    """Resolve abstract branch categories to concrete tech IDs for one profile."""
    resolved = []
    for branch in research_module.get("branches", []):
        abstract_key = branch["abstract"]
        concrete_ids = profile.get("tech_categories", {}).get(abstract_key, [])
        resolved.append({
            **branch,
            "concrete_tech_categories": concrete_ids,
        })
    return resolved


def resolve_template_roles_for_profile(profile: dict, army_module: dict) -> list[dict]:
    """Resolve abstract unit roles in army templates to concrete sub-unit names."""
    sub_units = profile.get("sub_units", {})
    support_units = profile.get("support_units", {})
    resolved = []

    for role_def in army_module.get("template_roles", []):
        resolved_role = dict(role_def)
        resolved_templates = []

        for tmpl in role_def.get("templates", []):
            resolved_tmpl = dict(tmpl)

            # Resolve regiments: ROLE_LINE_INFANTRY -> infantry
            resolved_regiments = {}
            for abstract_role, count in tmpl.get("regiments", {}).items():
                concrete_units = sub_units.get(abstract_role, [])
                if concrete_units:
                    # Use first concrete unit as primary
                    resolved_regiments[concrete_units[0]] = count
            resolved_tmpl["resolved_regiments"] = resolved_regiments

            # Resolve support companies: abstract name -> profile-mapped name
            resolved_support = []
            for support_name in tmpl.get("support", []):
                mapped = support_units.get(support_name, support_name)
                resolved_support.append(mapped)
            resolved_tmpl["resolved_support"] = resolved_support

            resolved_templates.append(resolved_tmpl)

        resolved_role["templates"] = resolved_templates
        resolved.append(resolved_role)

    return resolved


def resolve_production_for_profile(profile: dict, army_module: dict) -> list[dict]:
    """Resolve abstract equipment categories to concrete archetypes for production."""
    equipment = profile.get("equipment", {})
    resolved = []

    for prod in army_module.get("production_strategies", []):
        abstract_key = prod["abstract_equip"]
        concrete_archetypes = equipment.get(abstract_key, [])
        resolved.append({
            **prod,
            "concrete_archetypes": concrete_archetypes,
        })

    return resolved


def merge_all_profiles_into_config(config: dict, profiles: list[dict]) -> dict:
    """
    Merge ALL profiles into config.  Each profile gets its branches resolved.

    Returns a dict with:
    - All original config data
    - profiles: list of profile dicts (with resolved_branches added to each)
    - profile: the default profile (first / is_default)
    - resolved_branches: default profile branches (backwards compat)
    """
    merged = dict(config)
    merged["profiles"] = profiles

    # Pass through defines for template rendering
    merged["defines"] = config.get("defines", {})

    # Find research module
    research_module = None
    for module in merged.get("modules", []):
        if module.get("module_name") == "research":
            research_module = module
            break

    # Find army module
    army_module = None
    for module in merged.get("modules", []):
        if module.get("module_name") == "army":
            army_module = module
            break

    # Resolve branches, templates, and equipment for each profile
    for profile in profiles:
        if research_module:
            profile["resolved_branches"] = resolve_branches_for_profile(profile, research_module)
        else:
            profile["resolved_branches"] = []

        # Resolve sub-units
        profile["resolved_sub_units"] = dict(profile.get("sub_units", {}))
        profile["resolved_equipment"] = dict(profile.get("equipment", {}))

        # Resolve army template roles — map abstract unit roles to concrete sub-unit names
        if army_module and army_module.get("template_roles"):
            profile["resolved_template_roles"] = resolve_template_roles_for_profile(
                profile, army_module
            )
        else:
            profile["resolved_template_roles"] = []

        # Resolve production strategies — map abstract equipment to concrete archetypes
        if army_module and army_module.get("production_strategies"):
            profile["resolved_production"] = resolve_production_for_profile(
                profile, army_module
            )
        else:
            profile["resolved_production"] = []

        # Profile flag name: DAI_PROFILE_VANILLA, DAI_PROFILE_KAISERREICH, etc.
        profile["flag_name"] = f"DAI_PROFILE_{profile['profile_name'].upper()}"

    # Find warfare module
    warfare_module = None
    for module in merged.get("modules", []):
        if module.get("module_name") == "warfare":
            warfare_module = module
            break

    # Warfare: land strategies are profile-independent, pass through
    if warfare_module:
        merged["land_strategies"] = warfare_module.get("land_strategies", [])
        merged["invasion_strategies"] = warfare_module.get("invasion_strategies", [])
        # Naval/air have some profile-independent entries (unit_ratio ids like
        # "screen_ship", "fighter" are universal) — pass through directly.
        # Equipment-gated production is already handled by army module.
        merged["naval_strategies"] = warfare_module.get("naval_strategies", [])
        merged["air_strategies"] = warfare_module.get("air_strategies", [])
        merged["frontline_strategies"] = warfare_module.get("frontline_strategies", {})
    else:
        merged["land_strategies"] = []
        merged["invasion_strategies"] = []
        merged["naval_strategies"] = []
        merged["air_strategies"] = []
        merged["frontline_strategies"] = {}

    # Compute union of all profiles' area_mappings for theatre strategies
    all_areas: set[str] = set()
    for profile in profiles:
        all_areas.update(profile.get("area_mappings", []))
    merged["valid_areas"] = sorted(all_areas)

    # Grand Strategy module — mostly profile-independent
    gs_module = None
    for module in merged.get("modules", []):
        if module.get("module_name") == "grand_strategy":
            gs_module = module
            break

    if gs_module:
        merged["diplomacy_strategies"] = gs_module.get("diplomacy_strategies", [])
        merged["economy_strategies"] = gs_module.get("economy_strategies", [])
        merged["economy_law_strategies"] = gs_module.get("economy_law_strategies", [])
        merged["peace_strategies"] = gs_module.get("peace_strategies", [])
    else:
        merged["diplomacy_strategies"] = []
        merged["economy_strategies"] = []
        merged["economy_law_strategies"] = []
        merged["peace_strategies"] = []

    # Construction strategies are profile-independent — pass through directly
    if army_module and army_module.get("construction_strategies"):
        merged["construction_strategies"] = army_module["construction_strategies"]
    else:
        merged["construction_strategies"] = []

    # Default profile = first one (lowest priority)
    default_profile = profiles[0] if profiles else {}
    merged["profile"] = default_profile
    merged["resolved_branches"] = default_profile.get("resolved_branches", [])
    merged["resolved_sub_units"] = default_profile.get("resolved_sub_units", {})
    merged["resolved_equipment"] = default_profile.get("resolved_equipment", {})

    return merged


# Keep old single-profile API for backwards compat with tests
def merge_profile_into_config(config: dict, profile: dict) -> dict:
    """Single-profile merge (wraps multi-profile API)."""
    return merge_all_profiles_into_config(config, [profile])
