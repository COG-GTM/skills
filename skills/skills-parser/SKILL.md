# Skills Parser Playbook

This Devin playbook automatically converts Anthropic Skills files into Devin-compatible playbooks and knowledge entries. Use this playbook when you need to integrate any repository that uses the Anthropic Skills format (`/skills` directory with SKILL.md files) into Devin.

## When to Use This Playbook

Run this playbook when:
- A customer has a repository with Anthropic Skills files (SKILL.md)
- You need to convert skills from the Anthropic format to Devin playbooks and knowledge
- You want to automatically generate Devin-compatible markdown files from existing skills

## Quick Start

### Parse a Single Skill

To parse one skill and generate Devin playbook + knowledge files:

```bash
python scripts/parse_skill.py <path-to-skill-directory> --output-dir ./devin-output
```

This generates two markdown files:
- `<skill-name>-playbook.md` - A Devin playbook with instructions
- `<skill-name>-knowledge.md` - A Devin knowledge entry with reference information

### Parse All Skills in a Repository

To parse all skills in a `/skills` directory:

```bash
python scripts/batch_parse.py <skills-directory> --output-dir ./devin-output
```

This generates organized output:
```
devin-output/
├── playbooks/
│   ├── skill1-playbook.md
│   ├── skill2-playbook.md
│   └── ...
└── knowledge/
    ├── skill1-knowledge.md
    ├── skill2-knowledge.md
    └── ...
```

## What Gets Generated

### Devin Playbooks (markdown)

Each generated playbook includes:
- Title and description from the original skill
- "When to Use" section
- Full instructions from the skill's markdown body
- List of available scripts with paths
- Reference documentation links
- Asset locations

### Devin Knowledge Entries (markdown)

Each generated knowledge entry includes:
- Overview of the skill
- Detailed instructions and guidelines
- Scripts, references, and assets organized by category
- Source attribution to the original Anthropic Skill

## Input Format (Anthropic Skills)

The parser expects skills following the Anthropic Agent Skills format:

```
skill-name/
├── SKILL.md (required)
│   ├── YAML frontmatter (name, description)
│   └── Markdown instructions
└── Bundled Resources (optional)
    ├── scripts/          - Executable code
    ├── references/       - Documentation
    └── assets/           - Templates, images, etc.
```

### SKILL.md Format

```yaml
---
name: skill-name
description: What the skill does and when to use it
---

# Skill Title

Instructions and guidelines...
```

## Validation

Before parsing, you can validate a skill directory:

```bash
python scripts/validate_skill.py <path-to-skill-directory>
```

Validation checks:
- SKILL.md exists and is readable
- YAML frontmatter has required `name` and `description` fields
- Name follows conventions (lowercase, hyphens, max 40 chars)
- Directory structure is properly organized

## Example Usage

### Single Skill

```bash
# Parse the PDF skill
python scripts/parse_skill.py ./skills/pdf --output-dir ./output

# Output:
# ./output/pdf-playbook.md
# ./output/pdf-knowledge.md
```

### Batch Processing

```bash
# Parse all skills in a repository
python scripts/batch_parse.py ./skills --output-dir ./devin-integration

# Output:
# ./devin-integration/playbooks/*.md
# ./devin-integration/knowledge/*.md
```

## Adding Generated Files to Devin

After running the parser:

1. **Playbooks**: Add the generated `*-playbook.md` files as Devin playbooks in your organization settings
2. **Knowledge**: Add the generated `*-knowledge.md` files as Devin knowledge entries

The generated files are ready to use immediately - no additional formatting required.

## Available Scripts

- `scripts/parse_skill.py` - Parse a single skill and generate Devin playbook + knowledge
- `scripts/batch_parse.py` - Parse multiple skills at once
- `scripts/validate_skill.py` - Validate skill structure before parsing

## Reference Documentation

See `references/skill_format.md` for the complete Anthropic Skills format specification.
