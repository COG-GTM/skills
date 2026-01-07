#!/usr/bin/env python3
"""
Skill Integrator - Integrate parsed skills into Devin's knowledge system

This script takes a parsed skill (in JSON format) and integrates it into
Devin's knowledge system, making it available for use in conversations.

Usage:
    integrate_skill.py <knowledge-entry.json>
    integrate_skill.py <knowledge-entry.json> --dry-run

Examples:
    integrate_skill.py ./parsed_skill.json
    integrate_skill.py ./parsed_skill.json --dry-run
"""

import argparse
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path


KNOWLEDGE_STORE_PATH = Path.home() / '.devin' / 'knowledge' / 'skills'


def validate_knowledge_entry(entry: dict) -> list[str]:
    """
    Validate that a knowledge entry has all required fields.
    
    Args:
        entry: The knowledge entry dictionary to validate
        
    Returns:
        List of validation error messages (empty if valid)
    """
    errors = []
    required_fields = ['name', 'description', 'content']
    
    for field in required_fields:
        if field not in entry:
            errors.append(f"Missing required field: {field}")
        elif not entry[field]:
            errors.append(f"Field '{field}' cannot be empty")
    
    if 'name' in entry:
        name = entry['name']
        if not isinstance(name, str):
            errors.append("Field 'name' must be a string")
        elif len(name) > 40:
            errors.append("Field 'name' must be 40 characters or less")
    
    if 'resources' in entry:
        if not isinstance(entry['resources'], dict):
            errors.append("Field 'resources' must be a dictionary")
        else:
            for key in ['scripts', 'references', 'assets']:
                if key in entry['resources'] and not isinstance(entry['resources'][key], list):
                    errors.append(f"Field 'resources.{key}' must be a list")
    
    return errors


def load_knowledge_entry(file_path: str) -> dict:
    """
    Load a knowledge entry from a JSON file.
    
    Args:
        file_path: Path to the JSON file
        
    Returns:
        Dictionary containing the knowledge entry
    """
    path = Path(file_path).resolve()
    
    if not path.exists():
        raise FileNotFoundError(f"Knowledge entry file not found: {path}")
    
    if not path.is_file():
        raise ValueError(f"Path is not a file: {path}")
    
    try:
        content = path.read_text(encoding='utf-8')
        entry = json.loads(content)
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON in knowledge entry file: {e}")
    
    return entry


def ensure_knowledge_store() -> Path:
    """
    Ensure the knowledge store directory exists.
    
    Returns:
        Path to the knowledge store directory
    """
    KNOWLEDGE_STORE_PATH.mkdir(parents=True, exist_ok=True)
    return KNOWLEDGE_STORE_PATH


def integrate_skill(entry: dict, dry_run: bool = False) -> dict:
    """
    Integrate a skill into Devin's knowledge system.
    
    Args:
        entry: The knowledge entry to integrate
        dry_run: If True, don't actually write to the knowledge store
        
    Returns:
        Dictionary with integration result details
    """
    errors = validate_knowledge_entry(entry)
    if errors:
        raise ValueError(f"Invalid knowledge entry:\n" + "\n".join(f"  - {e}" for e in errors))
    
    skill_name = entry['name']
    
    integration_entry = {
        **entry,
        'integrated_at': datetime.now(timezone.utc).isoformat(),
        'status': 'active'
    }
    
    if not dry_run:
        store_path = ensure_knowledge_store()
        skill_file = store_path / f"{skill_name}.json"
        
        skill_file.write_text(
            json.dumps(integration_entry, indent=2),
            encoding='utf-8'
        )
        
        result = {
            'success': True,
            'skill_name': skill_name,
            'stored_at': str(skill_file),
            'integrated_at': integration_entry['integrated_at']
        }
    else:
        result = {
            'success': True,
            'skill_name': skill_name,
            'stored_at': str(KNOWLEDGE_STORE_PATH / f"{skill_name}.json"),
            'integrated_at': integration_entry['integrated_at'],
            'dry_run': True
        }
    
    return result


def list_integrated_skills() -> list[dict]:
    """
    List all skills currently integrated in the knowledge store.
    
    Returns:
        List of skill summary dictionaries
    """
    if not KNOWLEDGE_STORE_PATH.exists():
        return []
    
    skills = []
    for skill_file in KNOWLEDGE_STORE_PATH.glob('*.json'):
        try:
            content = skill_file.read_text(encoding='utf-8')
            entry = json.loads(content)
            skills.append({
                'name': entry.get('name', skill_file.stem),
                'description': entry.get('description', '')[:100],
                'integrated_at': entry.get('integrated_at', 'unknown'),
                'status': entry.get('status', 'unknown')
            })
        except Exception:
            continue
    
    return skills


def main():
    parser = argparse.ArgumentParser(
        description='Integrate parsed skills into Devin\'s knowledge system'
    )
    parser.add_argument(
        'knowledge_entry',
        nargs='?',
        help='Path to the knowledge entry JSON file'
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Validate and show what would be done without actually integrating'
    )
    parser.add_argument(
        '--list',
        action='store_true',
        help='List all currently integrated skills'
    )
    
    args = parser.parse_args()
    
    if args.list:
        skills = list_integrated_skills()
        if not skills:
            print("No skills currently integrated.")
        else:
            print(f"Integrated skills ({len(skills)}):")
            for skill in skills:
                print(f"  - {skill['name']}: {skill['description'][:50]}...")
        return 0
    
    if not args.knowledge_entry:
        parser.print_help()
        return 1
    
    try:
        entry = load_knowledge_entry(args.knowledge_entry)
        
        result = integrate_skill(entry, dry_run=args.dry_run)
        
        if args.dry_run:
            print("Dry run - no changes made")
            print()
        
        print(f"Successfully integrated skill: {result['skill_name']}")
        print(f"  - Stored at: {result['stored_at']}")
        print(f"  - Integrated at: {result['integrated_at']}")
        print()
        print("Skill has been added to Devin's knowledge system.")
        print("You can now use this skill by mentioning it in your requests.")
        
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
