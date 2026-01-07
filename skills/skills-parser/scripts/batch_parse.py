#!/usr/bin/env python3
"""
Batch Skills Parser - Parse multiple Anthropic Skills and generate Devin playbooks/knowledge

This script processes multiple skill directories and generates Devin-compatible
playbooks (markdown) and knowledge entries (markdown) for each.

Usage:
    batch_parse.py <skills-directory> [--output-dir <output-directory>]

Examples:
    batch_parse.py ./my-skills
    batch_parse.py ./my-skills --output-dir ./devin-output
"""

import argparse
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

from parse_skill import parse_skill, generate_devin_playbook, generate_devin_knowledge


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
    continue_on_error: bool = True
) -> dict:
    """
    Parse multiple skills from a directory and generate Devin playbooks/knowledge.
    
    Args:
        skills_dir: Path to the directory containing skill subdirectories
        output_dir: Optional path to save generated markdown files
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
            'errors': [],
            'generated_files': []
        }
    
    output_path = Path(output_dir).resolve() if output_dir else Path.cwd()
    output_path.mkdir(parents=True, exist_ok=True)
    
    playbooks_dir = output_path / 'playbooks'
    knowledge_dir = output_path / 'knowledge'
    playbooks_dir.mkdir(parents=True, exist_ok=True)
    knowledge_dir.mkdir(parents=True, exist_ok=True)
    
    results = {
        'success': True,
        'total': len(skill_dirs),
        'parsed': 0,
        'failed': 0,
        'skills': [],
        'errors': [],
        'generated_files': []
    }
    
    for skill_dir in skill_dirs:
        skill_name = skill_dir.name
        
        try:
            parsed_skill = parse_skill(str(skill_dir))
            
            playbook_md = generate_devin_playbook(parsed_skill)
            knowledge_md = generate_devin_knowledge(parsed_skill)
            
            playbook_file = playbooks_dir / f"{parsed_skill['name']}-playbook.md"
            knowledge_file = knowledge_dir / f"{parsed_skill['name']}-knowledge.md"
            
            playbook_file.write_text(playbook_md, encoding='utf-8')
            knowledge_file.write_text(knowledge_md, encoding='utf-8')
            
            results['parsed'] += 1
            results['skills'].append({
                'name': parsed_skill['name'],
                'status': 'success',
                'description': parsed_skill['description'][:100]
            })
            results['generated_files'].append({
                'skill': parsed_skill['name'],
                'playbook': str(playbook_file),
                'knowledge': str(knowledge_file)
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
            desc = skill['description'][:50] if len(skill['description']) > 50 else skill['description']
            print(f"  - {skill['name']}: {desc}...")
        print()
    
    if results['generated_files']:
        print("Generated files:")
        for files in results['generated_files']:
            print(f"  {files['skill']}:")
            print(f"    - Playbook: {files['playbook']}")
            print(f"    - Knowledge: {files['knowledge']}")
        print()
    
    if results['errors']:
        print("Errors:")
        for error in results['errors']:
            print(f"  - {error['skill']}: {error['error']}")
        print()


def main():
    parser = argparse.ArgumentParser(
        description='Parse multiple Anthropic Skills and generate Devin playbooks/knowledge'
    )
    parser.add_argument(
        'skills_directory',
        help='Path to the directory containing skill subdirectories'
    )
    parser.add_argument(
        '--output-dir', '-o',
        help='Output directory for generated markdown files (default: current directory)'
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
            output_dir=args.output_dir,
            continue_on_error=not args.stop_on_error
        )
        
        if not args.quiet:
            print_results(results)
        
        if results['parsed'] > 0:
            print("You can now add these files to Devin:")
            print("  - Add files from 'playbooks/' directory as Devin playbooks")
            print("  - Add files from 'knowledge/' directory as Devin knowledge")
        
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
