#!/usr/bin/env python3
"""
Skills Parser - Parse Anthropic Skills files and generate Devin playbooks/knowledge

This script parses skill directories following the Anthropic Agent Skills format
and generates Devin-compatible playbooks (markdown) and knowledge entries (markdown).

Usage:
    parse_skill.py <skill-directory> [--output-dir <output-directory>]

Examples:
    parse_skill.py ./my-skill
    parse_skill.py ./my-skill --output-dir ./devin-output
"""

import argparse
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path


def extract_frontmatter(content: str) -> tuple[dict, str]:
    """
    Extract YAML frontmatter and markdown body from SKILL.md content.
    
    Args:
        content: Full content of SKILL.md file
        
    Returns:
        Tuple of (frontmatter_dict, markdown_body)
    """
    frontmatter_pattern = r'^---\s*\n(.*?)\n---\s*\n(.*)$'
    match = re.match(frontmatter_pattern, content, re.DOTALL)
    
    if not match:
        raise ValueError("Invalid SKILL.md format: Missing or malformed YAML frontmatter")
    
    frontmatter_text = match.group(1)
    body = match.group(2)
    
    frontmatter = {}
    current_key = None
    current_value = []
    
    for line in frontmatter_text.strip().split('\n'):
        if ':' in line and not line.startswith(' ') and not line.startswith('\t'):
            if current_key:
                frontmatter[current_key] = ' '.join(current_value).strip()
            key, value = line.split(':', 1)
            current_key = key.strip()
            current_value = [value.strip()] if value.strip() else []
        elif current_key:
            current_value.append(line.strip())
    
    if current_key:
        frontmatter[current_key] = ' '.join(current_value).strip()
    
    return frontmatter, body


def validate_frontmatter(frontmatter: dict) -> list[str]:
    """
    Validate that frontmatter contains required fields.
    
    Args:
        frontmatter: Dictionary of frontmatter fields
        
    Returns:
        List of validation error messages (empty if valid)
    """
    errors = []
    
    if 'name' not in frontmatter:
        errors.append("Missing required field: name")
    elif not re.match(r'^[a-z0-9-]+$', frontmatter['name']):
        errors.append("Invalid skill name format: must be lowercase letters, numbers, and hyphens only")
    elif len(frontmatter['name']) > 40:
        errors.append("Invalid skill name: must be 40 characters or less")
    
    if 'description' not in frontmatter:
        errors.append("Missing required field: description")
    elif len(frontmatter['description'].strip()) == 0:
        errors.append("Description cannot be empty")
    
    return errors


def discover_resources(skill_dir: Path) -> dict:
    """
    Discover bundled resources in the skill directory.
    
    Args:
        skill_dir: Path to the skill directory
        
    Returns:
        Dictionary with lists of scripts, references, and assets (with paths)
    """
    resources = {
        'scripts': [],
        'references': [],
        'assets': []
    }
    
    scripts_dir = skill_dir / 'scripts'
    if scripts_dir.exists() and scripts_dir.is_dir():
        resources['scripts'] = [
            {'name': f.name, 'path': str(f)}
            for f in scripts_dir.iterdir() 
            if f.is_file() and not f.name.startswith('.')
        ]
    
    references_dir = skill_dir / 'references'
    if references_dir.exists() and references_dir.is_dir():
        resources['references'] = [
            {'name': f.name, 'path': str(f)}
            for f in references_dir.iterdir() 
            if f.is_file() and not f.name.startswith('.')
        ]
    
    assets_dir = skill_dir / 'assets'
    if assets_dir.exists() and assets_dir.is_dir():
        resources['assets'] = [
            {'name': f.name, 'path': str(f)}
            for f in assets_dir.iterdir() 
            if f.is_file() and not f.name.startswith('.')
        ]
    
    return resources


def parse_skill(skill_dir: str) -> dict:
    """
    Parse a skill directory and extract all components.
    
    Args:
        skill_dir: Path to the skill directory
        
    Returns:
        Dictionary containing parsed skill data
    """
    skill_path = Path(skill_dir).resolve()
    
    if not skill_path.exists():
        raise FileNotFoundError(f"Skill directory not found: {skill_path}")
    
    if not skill_path.is_dir():
        raise ValueError(f"Path is not a directory: {skill_path}")
    
    skill_md_path = skill_path / 'SKILL.md'
    if not skill_md_path.exists():
        raise FileNotFoundError(f"SKILL.md not found in {skill_path}")
    
    content = skill_md_path.read_text(encoding='utf-8')
    
    frontmatter, body = extract_frontmatter(content)
    
    errors = validate_frontmatter(frontmatter)
    if errors:
        raise ValueError(f"Validation errors:\n" + "\n".join(f"  - {e}" for e in errors))
    
    resources = discover_resources(skill_path)
    
    parsed_skill = {
        'name': frontmatter['name'],
        'description': frontmatter['description'],
        'content': body.strip(),
        'resources': resources,
        'source': 'anthropic-skills',
        'source_path': str(skill_path),
        'parsed_at': datetime.now(timezone.utc).isoformat()
    }
    
    return parsed_skill


def generate_devin_playbook(parsed_skill: dict) -> str:
    """
    Generate a Devin playbook (markdown) from parsed skill data.
    
    Args:
        parsed_skill: Dictionary containing parsed skill data
        
    Returns:
        Markdown string for the Devin playbook
    """
    name = parsed_skill['name']
    description = parsed_skill['description']
    content = parsed_skill['content']
    resources = parsed_skill['resources']
    
    playbook = f"""# {name.replace('-', ' ').title()} Playbook

## Description

{description}

## When to Use

Use this playbook when you need to {description.lower().rstrip('.')}

## Instructions

{content}
"""
    
    if resources['scripts']:
        playbook += "\n## Available Scripts\n\n"
        for script in resources['scripts']:
            playbook += f"- `{script['name']}` - Located at `{script['path']}`\n"
    
    if resources['references']:
        playbook += "\n## Reference Documentation\n\n"
        for ref in resources['references']:
            playbook += f"- `{ref['name']}` - See `{ref['path']}`\n"
    
    if resources['assets']:
        playbook += "\n## Assets\n\n"
        for asset in resources['assets']:
            playbook += f"- `{asset['name']}` - Located at `{asset['path']}`\n"
    
    playbook += f"""
---
*Generated from Anthropic Skill: {parsed_skill['name']}*
*Source: {parsed_skill['source_path']}*
*Generated at: {parsed_skill['parsed_at']}*
"""
    
    return playbook


def generate_devin_knowledge(parsed_skill: dict) -> str:
    """
    Generate a Devin knowledge entry (markdown) from parsed skill data.
    
    Args:
        parsed_skill: Dictionary containing parsed skill data
        
    Returns:
        Markdown string for the Devin knowledge entry
    """
    name = parsed_skill['name']
    description = parsed_skill['description']
    content = parsed_skill['content']
    resources = parsed_skill['resources']
    
    knowledge = f"""# {name.replace('-', ' ').title()}

## Overview

{description}

## Details

{content}
"""
    
    if resources['scripts']:
        knowledge += "\n## Scripts\n\n"
        knowledge += "The following scripts are available for this skill:\n\n"
        for script in resources['scripts']:
            knowledge += f"- **{script['name']}**: `{script['path']}`\n"
    
    if resources['references']:
        knowledge += "\n## References\n\n"
        knowledge += "Additional documentation:\n\n"
        for ref in resources['references']:
            knowledge += f"- **{ref['name']}**: `{ref['path']}`\n"
    
    if resources['assets']:
        knowledge += "\n## Assets\n\n"
        knowledge += "Available assets:\n\n"
        for asset in resources['assets']:
            knowledge += f"- **{asset['name']}**: `{asset['path']}`\n"
    
    knowledge += f"""
---
*Source: Anthropic Skill ({parsed_skill['name']})*
*Original location: {parsed_skill['source_path']}*
"""
    
    return knowledge


def print_summary(parsed_skill: dict, playbook_path: str, knowledge_path: str) -> None:
    """Print a summary of the generated files."""
    desc_preview = parsed_skill['description'][:100]
    if len(parsed_skill['description']) > 100:
        desc_preview += "..."
    
    print(f"\nSuccessfully parsed skill: {parsed_skill['name']}")
    print(f"  - Description: {desc_preview}")
    print(f"  - Scripts: {len(parsed_skill['resources']['scripts'])} files")
    print(f"  - References: {len(parsed_skill['resources']['references'])} files")
    print(f"  - Assets: {len(parsed_skill['resources']['assets'])} files")
    print()
    print("Generated Devin files:")
    print(f"  - Playbook: {playbook_path}")
    print(f"  - Knowledge: {knowledge_path}")


def main():
    parser = argparse.ArgumentParser(
        description='Parse Anthropic Skills and generate Devin playbooks/knowledge (markdown)'
    )
    parser.add_argument(
        'skill_directory',
        help='Path to the skill directory containing SKILL.md'
    )
    parser.add_argument(
        '--output-dir', '-o',
        help='Output directory for generated markdown files (default: current directory)'
    )
    parser.add_argument(
        '--quiet', '-q',
        action='store_true',
        help='Suppress output except for errors'
    )
    
    args = parser.parse_args()
    
    try:
        parsed_skill = parse_skill(args.skill_directory)
        
        playbook_md = generate_devin_playbook(parsed_skill)
        knowledge_md = generate_devin_knowledge(parsed_skill)
        
        output_dir = Path(args.output_dir) if args.output_dir else Path.cwd()
        output_dir.mkdir(parents=True, exist_ok=True)
        
        skill_name = parsed_skill['name']
        playbook_path = output_dir / f"{skill_name}-playbook.md"
        knowledge_path = output_dir / f"{skill_name}-knowledge.md"
        
        playbook_path.write_text(playbook_md, encoding='utf-8')
        knowledge_path.write_text(knowledge_md, encoding='utf-8')
        
        if not args.quiet:
            print_summary(parsed_skill, str(playbook_path), str(knowledge_path))
            print()
            print("You can now add these files to Devin:")
            print(f"  - Add {playbook_path} as a Devin playbook")
            print(f"  - Add {knowledge_path} as Devin knowledge")
        
        return 0
        
    except FileNotFoundError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"Unexpected error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
