#!/usr/bin/env python3
"""
Batch Skills Parser - Parse multiple Anthropic Skills directories at once

This script processes multiple skill directories and generates knowledge entries
for each, optionally integrating them all into Devin's knowledge system.

Usage:
    batch_parse.py <skills-directory> [--output <output-directory>] [--integrate]

Examples:
    batch_parse.py ./my-skills
    batch_parse.py ./my-skills --output ./parsed-skills
    batch_parse.py ./my-skills --integrate
"""

import argparse
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

from parse_skill import parse_skill, generate_knowledge_entry
from integrate_skill import integrate_skill


def discover_skills(skills_dir: str) -> list[Path]:
    """
    Discover all skill directories in a parent directory.
    
    A directory is considered a skill if it contains a SKILL.md file.
    
    Args:
        skills_dir: Path to the parent directory containing skills
        
    Returns:
        List of paths to skill directories
    """
    skills_path = Path(skills_dir).resolve()
    
    if not skills_path.exists():
        raise FileNotFoundError(f"Skills directory not found: {skills_path}")
    
    if not skills_path.is_dir():
        raise ValueError(f"Path is not a directory: {skills_path}")
    
    skill_dirs = []
    
    for item in skills_path.iterdir():
        if item.is_dir():
            skill_md = item / 'SKILL.md'
            if skill_md.exists() and skill_md.is_file():
                skill_dirs.append(item)
    
    return sorted(skill_dirs, key=lambda p: p.name)


def batch_parse(
    skills_dir: str,
    output_dir: str = None,
    integrate: bool = False,
    continue_on_error: bool = True
) -> dict:
    """
    Parse multiple skills from a directory.
    
    Args:
        skills_dir: Path to the directory containing skill subdirectories
        output_dir: Optional path to save parsed knowledge entries
        integrate: If True, integrate skills into Devin's knowledge system
        continue_on_error: If True, continue processing after errors
        
    Returns:
        Dictionary with batch processing results
    """
    skill_dirs = discover_skills(skills_dir)
    
    if not skill_dirs:
        return {
            'success': True,
            'total': 0,
            'parsed': 0,
            'failed': 0,
            'skills': [],
            'errors': []
        }
    
    if output_dir:
        output_path = Path(output_dir).resolve()
        output_path.mkdir(parents=True, exist_ok=True)
    else:
        output_path = None
    
    results = {
        'success': True,
        'total': len(skill_dirs),
        'parsed': 0,
        'failed': 0,
        'skills': [],
        'errors': []
    }
    
    for skill_dir in skill_dirs:
        skill_name = skill_dir.name
        
        try:
            parsed_skill = parse_skill(str(skill_dir))
            knowledge_entry = generate_knowledge_entry(parsed_skill)
            
            if output_path:
                entry_file = output_path / f"{skill_name}.json"
                entry_file.write_text(
                    json.dumps(knowledge_entry, indent=2),
                    encoding='utf-8'
                )
            
            if integrate:
                integrate_skill(knowledge_entry)
            
            results['parsed'] += 1
            results['skills'].append({
                'name': skill_name,
                'status': 'success',
                'description': parsed_skill['description'][:100]
            })
            
        except Exception as e:
            results['failed'] += 1
            results['errors'].append({
                'skill': skill_name,
                'error': str(e)
            })
            
            if not continue_on_error:
                results['success'] = False
                break
    
    if results['failed'] > 0:
        results['success'] = False
    
    return results


def print_results(results: dict) -> None:
    """Print batch processing results."""
    print(f"\nBatch Processing Complete")
    print(f"{'=' * 40}")
    print(f"Total skills found: {results['total']}")
    print(f"Successfully parsed: {results['parsed']}")
    print(f"Failed: {results['failed']}")
    print()
    
    if results['skills']:
        print("Parsed skills:")
        for skill in results['skills']:
            print(f"  - {skill['name']}: {skill['description'][:50]}...")
        print()
    
    if results['errors']:
        print("Errors:")
        for error in results['errors']:
            print(f"  - {error['skill']}: {error['error']}")
        print()


def main():
    parser = argparse.ArgumentParser(
        description='Parse multiple Anthropic Skills directories at once'
    )
    parser.add_argument(
        'skills_directory',
        help='Path to the directory containing skill subdirectories'
    )
    parser.add_argument(
        '--output', '-o',
        help='Output directory for parsed knowledge entries'
    )
    parser.add_argument(
        '--integrate',
        action='store_true',
        help='Integrate all skills into Devin\'s knowledge system'
    )
    parser.add_argument(
        '--stop-on-error',
        action='store_true',
        help='Stop processing if any skill fails to parse'
    )
    parser.add_argument(
        '--quiet', '-q',
        action='store_true',
        help='Suppress detailed output'
    )
    
    args = parser.parse_args()
    
    try:
        if not args.quiet:
            print(f"Discovering skills in: {args.skills_directory}")
        
        results = batch_parse(
            args.skills_directory,
            output_dir=args.output,
            integrate=args.integrate,
            continue_on_error=not args.stop_on_error
        )
        
        if not args.quiet:
            print_results(results)
        
        if args.integrate and results['parsed'] > 0:
            print("Skills have been added to Devin's knowledge system.")
            print("You can now use these skills by mentioning them in your requests.")
        
        return 0 if results['success'] else 1
        
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
