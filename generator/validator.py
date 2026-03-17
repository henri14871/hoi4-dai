"""
DAI Validator
Validates generated HOI4 script files for common errors.
"""

import re
from pathlib import Path


def validate_output(output_dir: Path) -> tuple[list[str], list[str]]:
    """
    Validate all generated .txt files in the output directory.
    Returns (errors, warnings) as lists of strings.
    """
    errors = []
    warnings = []

    txt_files = list(output_dir.rglob("*.txt"))
    yml_files = list(output_dir.rglob("*.yml"))

    for filepath in txt_files:
        rel = filepath.relative_to(output_dir)
        content = filepath.read_text(encoding="utf-8")

        # Check balanced braces
        brace_errs = check_balanced_braces(content, str(rel))
        errors.extend(brace_errs)

        # Check for factor = 0 (should be 0.01)
        factor_warns = check_factor_zero(content, str(rel))
        warnings.extend(factor_warns)

        # Check max factors per ai_strategy block
        if "ai_strategy" in str(rel):
            factor_count_warns = check_max_factors(content, str(rel), max_factors=8)
            warnings.extend(factor_count_warns)

        # Check for empty blocks
        empty_warns = check_empty_blocks(content, str(rel))
        warnings.extend(empty_warns)

    for filepath in yml_files:
        rel = filepath.relative_to(output_dir)
        content = filepath.read_text(encoding="utf-8-sig")

        # Check localisation format
        if "localisation" in str(rel):
            loc_errs = check_localisation_format(content, str(rel))
            errors.extend(loc_errs)

    return errors, warnings


def check_balanced_braces(content: str, filename: str) -> list[str]:
    """Check that every { has a matching }."""
    errors = []
    depth = 0
    line_num = 0

    for line in content.split("\n"):
        line_num += 1
        # Skip comments
        stripped = line.split("#")[0]
        for char in stripped:
            if char == "{":
                depth += 1
            elif char == "}":
                depth -= 1
                if depth < 0:
                    errors.append(f"{filename}:{line_num}: Extra closing brace")
                    depth = 0

    if depth > 0:
        errors.append(f"{filename}: {depth} unclosed brace(s) at end of file")

    return errors


def check_factor_zero(content: str, filename: str) -> list[str]:
    """Check for factor = 0 which should be 0.01 in ai_strategy."""
    warnings = []
    line_num = 0

    for line in content.split("\n"):
        line_num += 1
        stripped = line.strip()
        # Match "factor = 0" but not "factor = 0.01" or "factor = 0.5" etc.
        if re.match(r"^factor\s*=\s*0\s*$", stripped):
            warnings.append(
                f"{filename}:{line_num}: factor = 0 found (use 0.01 to avoid re-evaluation loops)"
            )

    return warnings


def check_max_factors(content: str, filename: str, max_factors: int = 8) -> list[str]:
    """Check that no ai_strategy block has more than max_factors modifier blocks."""
    warnings = []
    # Count modifier blocks within top-level strategy blocks
    in_strategy = False
    strategy_name = ""
    modifier_count = 0
    depth = 0

    for line in content.split("\n"):
        stripped = line.strip()

        if not in_strategy and "= {" in stripped and not stripped.startswith("#"):
            # Start of a top-level block
            in_strategy = True
            strategy_name = stripped.split("=")[0].strip()
            modifier_count = 0
            depth = 1
            continue

        if in_strategy:
            depth += stripped.count("{") - stripped.count("}")

            if stripped.startswith("modifier") and "=" in stripped:
                modifier_count += 1

            if depth <= 0:
                if modifier_count > max_factors:
                    warnings.append(
                        f"{filename}: Strategy '{strategy_name}' has {modifier_count} modifiers "
                        f"(max recommended: {max_factors})"
                    )
                in_strategy = False

    return warnings


def check_empty_blocks(content: str, filename: str) -> list[str]:
    """Check for empty { } blocks that might indicate template issues."""
    warnings = []
    # Pattern: something = { } on same line or { \n } with only whitespace
    matches = re.finditer(r"(\w+)\s*=\s*\{\s*\}", content)
    for match in matches:
        line_num = content[:match.start()].count("\n") + 1
        block_name = match.group(1)
        warnings.append(f"{filename}:{line_num}: Empty block '{block_name}'")

    return warnings


def check_localisation_format(content: str, filename: str) -> list[str]:
    """Validate localisation file format."""
    errors = []
    lines = content.split("\n")

    if not lines:
        errors.append(f"{filename}: Empty localisation file")
        return errors

    # First non-empty line should be language header
    first_line = lines[0].strip()
    if first_line and not first_line.startswith("l_"):
        errors.append(f"{filename}: First line should be language header (e.g., l_english:)")

    return errors
