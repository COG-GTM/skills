#!/usr/bin/env python3
"""
Skill Validator - Validate Anthropic Skills directory structure and content

This script validates that a skill directory follows the Anthropic Agent Skills
format and contains all required components.

Usage:
    validate_skill.py <skill-directory>

Examples:
    validate_skill.py ./my-skill
"""

import argparse
import re
import sys
from pathlib import Path


def validate_skill_name(name: str) -> list[str]:
    """
    Validate skill name follows conventions.
    
    Args:
        name: The skill name to validate
        
    Returns:
        List of validation error messages (empty if valid)
    """
    errors = []
    
    if not name:
        errors.append("Skill name cannot be empty")
        return errors
    
    if not re.match(r'^[a-z0-9-]+$', name):
        errors.append("Skill name must contain only lowercase letters, numbers, and hyphens")
    
    if len(name) > 40:
        errors.append("Skill name must be 40 characters or less")
    
    if name.startswith('-') or name.endswith('-'):
        errors.append("Skill name cannot start or end with a hyphen")
    
    if '--' in name:
        errors.append("Skill name cannot contain consecutive hyphens")
    
    return errors


def validate_frontmatter(content: str) -> tuple[dict, list[str]]:
    """
    Validate and extract YAML frontmatter from SKILL.md content.
    
    Args:
        content: Full content of SKILL.md file
        
    Returns:
        Tuple of (frontmatter_dict, list of error messages)
    """
    errors = []
    frontmatter = {}
    
    frontmatter_pattern = r'^---\s*\n(.*?)\n---\s*\n'
    match = re.match(frontmatter_pattern, content, re.DOTALL)
    
    if not match:
        errors.append("Missing or malformed YAML frontmatter (must start with --- and end with ---)")
        return frontmatter, errors
    
    frontmatter_text = match.group(1)
    
    for line in frontmatter_text.strip().split('\n'):
        line = line.strip()
        if not line:
            continue
        if ':' not in line:
            errors.append(f"Invalid frontmatter line (missing colon): {line}")
            continue
        key, value = line.split(':', 1)
        frontmatter[key.strip()] = value.strip()
    
    if 'name' not in frontmatter:
        errors.append("Missing required frontmatter field: name")
    else:
        name_errors = validate_skill_name(frontmatter['name'])
        errors.extend(name_errors)
    
    if 'description' not in frontmatter:
        errors.append("Missing required frontmatter field: description")
    elif len(frontmatter.get('description', '').strip()) == 0:
        errors.append("Description cannot be empty")
    elif len(frontmatter.get('description', '')) < 20:
        errors.append("Description should be at least 20 characters for clarity")
    
    return frontmatter, errors


def validate_directory_structure(skill_path: Path) -> list[str]:
    """
    Validate the skill directory structure.
    
    Args:
        skill_path: Path to the skill directory
        
    Returns:
        List of validation error messages (empty if valid)
    """
    errors = []
    warnings = []
    
    skill_md = skill_path / 'SKILL.md'
    if not skill_md.exists():
        errors.append("SKILL.md not found in skill directory")
    elif not skill_md.is_file():
        errors.append("SKILL.md exists but is not a file")
    
    for resource_dir in ['scripts', 'references', 'assets']:
        dir_path = skill_path / resource_dir
        if dir_path.exists() and not dir_path.is_dir():
            errors.append(f"{resource_dir}/ exists but is not a directory")
    
    dir_name = skill_path.name
    name_errors = validate_skill_name(dir_name)
    if name_errors:
        warnings.append(f"Directory name '{dir_name}' may not follow skill naming conventions")
    
    return errors


def validate_skill(skill_dir: str) -> tuple[bool, list[str], list[str]]:
    """
    Perform full validation of a skill directory.
    
    Args:
        skill_dir: Path to the skill directory
        
    Returns:
        Tuple of (is_valid, list of errors, list of warnings)
    """
    errors = []
    warnings = []
    
    skill_path = Path(skill_dir).resolve()
    
    if not skill_path.exists():
        return False, [f"Skill directory not found: {skill_path}"], []
    
    if not skill_path.is_dir():
        return False, [f"Path is not a directory: {skill_path}"], []
    
    structure_errors = validate_directory_structure(skill_path)
    errors.extend(structure_errors)
    
    if errors:
        return False, errors, warnings
    
    skill_md_path = skill_path / 'SKILL.md'
    try:
        content = skill_md_path.read_text(encoding='utf-8')
    except Exception as e:
        return False, [f"Failed to read SKILL.md: {e}"], warnings
    
    frontmatter, fm_errors = validate_frontmatter(content)
    errors.extend(fm_errors)
    
    if frontmatter.get('name') and frontmatter['name'] != skill_path.name:
        warnings.append(
            f"Skill name '{frontmatter['name']}' does not match directory name '{skill_path.name}'"
        )
    
    body_pattern = r'^---\s*\n.*?\n---\s*\n(.*)$'
    body_match = re.match(body_pattern, content, re.DOTALL)
    if body_match:
        body = body_match.group(1).strip()
        if len(body) < 50:
            warnings.append("SKILL.md body content is very short (less than 50 characters)")
    
    scripts_dir = skill_path / 'scripts'
    if scripts_dir.exists():
        for script in scripts_dir.iterdir():
            if script.is_file() and script.suffix == '.py':
                try:
                    script_content = script.read_text(encoding='utf-8')
                    compile(script_content, str(script), 'exec')
                except SyntaxError as e:
                    errors.append(f"Python syntax error in {script.name}: {e}")
                except Exception:
                    pass
    
    is_valid = len(errors) == 0
    return is_valid, errors, warnings


def main():
    parser = argparse.ArgumentParser(
        description='Validate Anthropic Skills directory structure and content'
    )
    parser.add_argument(
        'skill_directory',
        help='Path to the skill directory to validate'
    )
    parser.add_argument(
        '--strict',
        action='store_true',
        help='Treat warnings as errors'
    )
    
    args = parser.parse_args()
    
    print(f"Validating skill: {args.skill_directory}")
    print()
    
    is_valid, errors, warnings = validate_skill(args.skill_directory)
    
    if args.strict:
        errors.extend(warnings)
        warnings = []
        is_valid = len(errors) == 0
    
    if errors:
        print("Errors:")
        for error in errors:
            print(f"  - {error}")
        print()
    
    if warnings:
        print("Warnings:")
        for warning in warnings:
            print(f"  - {warning}")
        print()
    
    if is_valid:
        print("Validation PASSED")
        if warnings:
            print(f"  ({len(warnings)} warning(s))")
        return 0
    else:
        print("Validation FAILED")
        print(f"  {len(errors)} error(s) found")
        return 1


if __name__ == "__main__":
    sys.exit(main())
