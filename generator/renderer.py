"""
DAI Renderer
Jinja2-based template engine that generates HOI4 script files from
YAML config + profile data.
"""

import os
import shutil
from pathlib import Path

import jinja2


def hoi4_value(value) -> str:
    """Format a value for HOI4 script output.
    - Floats: no trailing zeros, 0.01 instead of 0
    - Strings: pass through
    - Booleans: yes/no
    """
    if isinstance(value, bool):
        return "yes" if value else "no"
    if isinstance(value, float):
        if value == 0.0:
            return "0.01"
        # Remove trailing zeros but keep at least one decimal
        formatted = f"{value:.4f}".rstrip("0")
        if formatted.endswith("."):
            formatted += "0"
        return formatted
    if isinstance(value, int):
        if value == 0:
            return "0"
        return str(value)
    return str(value)


def indent_block(text: str, level: int = 1, indent_char: str = "\t") -> str:
    """Indent a multi-line HOI4 block by the given number of levels."""
    prefix = indent_char * level
    lines = text.split("\n")
    return "\n".join(prefix + line if line.strip() else line for line in lines)


def create_jinja_env(template_dir: Path) -> jinja2.Environment:
    """Create a Jinja2 environment with HOI4-specific filters."""
    env = jinja2.Environment(
        loader=jinja2.FileSystemLoader(str(template_dir)),
        keep_trailing_newline=True,
        trim_blocks=True,
        lstrip_blocks=True,
        undefined=jinja2.StrictUndefined,
    )
    env.filters["hoi4_value"] = hoi4_value
    env.filters["indent_block"] = indent_block
    env.filters["upper"] = str.upper
    env.filters["lower"] = str.lower
    return env


def render_all(config: dict, template_dir: Path, output_dir: Path) -> list[str]:
    """
    Render all .j2 templates into the output directory.
    Returns a list of generated file paths (relative to output_dir).
    """
    env = create_jinja_env(template_dir)
    generated_files = []

    for root, _dirs, files in os.walk(str(template_dir)):
        for filename in files:
            if not filename.endswith(".j2"):
                continue

            template_path = Path(root) / filename
            rel_path = template_path.relative_to(template_dir)
            # Strip .j2 extension for output
            output_rel = str(rel_path).replace(".j2", "")
            output_path = output_dir / output_rel

            # Ensure output directory exists
            output_path.parent.mkdir(parents=True, exist_ok=True)

            # Render template
            template_rel_posix = rel_path.as_posix()
            template = env.get_template(template_rel_posix)
            rendered = template.render(**config)

            # Handle UTF-8 BOM for localisation files
            encoding = "utf-8"
            write_bom = False
            if "localisation" in output_rel and output_rel.endswith(".yml"):
                write_bom = True

            with open(output_path, "w", encoding=encoding, newline="\n") as f:
                if write_bom:
                    f.write("\ufeff")
                f.write(rendered)

            generated_files.append(output_rel)

    return sorted(generated_files)


def copy_static_files(source_dir: Path, output_dir: Path, files: list[str]) -> None:
    """Copy static files (thumbnail, etc.) to output directory."""
    for filename in files:
        src = source_dir / filename
        if src.exists():
            dst = output_dir / filename
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, dst)
