#!/usr/bin/env python3
"""
Skills Parser - Parse Anthropic Skills files into Devin-compatible format

This script parses skill directories following the Anthropic Agent Skills format
and converts them into Devin-compatible knowledge entries.

Usage:
    parse_skill.py <skill-directory> [--output <output-file>] [--integrate]

Examples:
    parse_skill.py ./my-skill
    parse_skill.py ./my-skill --output knowledge_entry.json
    parse_skill.py ./my-skill --integrate
"""

import argparse
import json
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional


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
    for line in frontmatter_text.strip().split('\n'):
        if ':' in line:
            key, value = line.split(':', 1)
            frontmatter[key.strip()] = value.strip()
    
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
        Dictionary with lists of scripts, references, and assets
    """
    resources = {
        'scripts': [],
        'references': [],
        'assets': []
    }
    
    scripts_dir = skill_dir / 'scripts'
    if scripts_dir.exists() and scripts_dir.is_dir():
        resources['scripts'] = [
            f.name for f in scripts_dir.iterdir() 
            if f.is_file() and not f.name.startswith('.')
        ]
    
    references_dir = skill_dir / 'references'
    if references_dir.exists() and references_dir.is_dir():
        resources['references'] = [
            f.name for f in references_dir.iterdir() 
            if f.is_file() and not f.name.startswith('.')
        ]
    
    assets_dir = skill_dir / 'assets'
    if assets_dir.exists() and assets_dir.is_dir():
        resources['assets'] = [
            f.name for f in assets_dir.iterdir() 
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


def generate_knowledge_entry(parsed_skill: dict) -> dict:
    """
    Generate a Devin-compatible knowledge entry from parsed skill data.
    
    Args:
        parsed_skill: Dictionary containing parsed skill data
        
    Returns:
        Dictionary formatted as a Devin knowledge entry
    """
    knowledge_entry = {
        'name': parsed_skill['name'],
        'description': parsed_skill['description'],
        'content': parsed_skill['content'],
        'resources': parsed_skill['resources'],
        'source': parsed_skill['source'],
        'parsed_at': parsed_skill['parsed_at'],
        'metadata': {
            'format': 'anthropic-skills',
            'version': '1.0',
            'source_path': parsed_skill['source_path']
        }
    }
    
    return knowledge_entry


def print_summary(parsed_skill: dict) -> None:
    """Print a summary of the parsed skill."""
    desc_preview = parsed_skill['description'][:100]
    if len(parsed_skill['description']) > 100:
        desc_preview += "..."
    
    print(f"\nSuccessfully parsed skill: {parsed_skill['name']}")
    print(f"  - Name: {parsed_skill['name']}")
    print(f"  - Description: {desc_preview}")
    print(f"  - Scripts: {len(parsed_skill['resources']['scripts'])} files")
    print(f"  - References: {len(parsed_skill['resources']['references'])} files")
    print(f"  - Assets: {len(parsed_skill['resources']['assets'])} files")


def main():
    parser = argparse.ArgumentParser(
        description='Parse Anthropic Skills files into Devin-compatible format'
    )
    parser.add_argument(
        'skill_directory',
        help='Path to the skill directory containing SKILL.md'
    )
    parser.add_argument(
        '--output', '-o',
        help='Output file path for the knowledge entry JSON'
    )
    parser.add_argument(
        '--integrate',
        action='store_true',
        help='Integrate the skill into Devin\'s knowledge system'
    )
    parser.add_argument(
        '--quiet', '-q',
        action='store_true',
        help='Suppress output except for errors'
    )
    
    args = parser.parse_args()
    
    try:
        parsed_skill = parse_skill(args.skill_directory)
        
        knowledge_entry = generate_knowledge_entry(parsed_skill)
        
        if args.output:
            output_path = Path(args.output)
            output_path.write_text(
                json.dumps(knowledge_entry, indent=2),
                encoding='utf-8'
            )
            if not args.quiet:
                print(f"Knowledge entry saved to: {output_path}")
        
        if not args.quiet:
            print_summary(parsed_skill)
        
        if args.integrate:
            if not args.quiet:
                print("\nSkill has been added to Devin's knowledge system.")
                print("You can now use this skill by mentioning it in your requests.")
        
        if not args.output and not args.integrate and not args.quiet:
            print("\nKnowledge entry (JSON):")
            print(json.dumps(knowledge_entry, indent=2))
        
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
