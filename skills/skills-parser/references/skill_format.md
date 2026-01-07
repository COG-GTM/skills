# Anthropic Agent Skills Format Specification

This document provides a detailed reference for the Anthropic Agent Skills format that the Skills Parser understands and processes.

## Overview

Skills are modular, self-contained packages that extend AI agent capabilities by providing specialized knowledge, workflows, and tools. The Skills Parser converts these packages into Devin-compatible knowledge entries.

## Directory Structure

A skill directory follows this structure:

```
skill-name/
├── SKILL.md (required)
│   ├── YAML frontmatter (required)
│   │   ├── name: (required)
│   │   └── description: (required)
│   └── Markdown instructions (required)
└── Bundled Resources (optional)
    ├── scripts/          - Executable code
    ├── references/       - Documentation
    └── assets/           - Output resources
```

## SKILL.md Format

### YAML Frontmatter

The frontmatter must be enclosed in triple dashes and contain at minimum:

```yaml
---
name: skill-name
description: Complete description of what the skill does and when to use it
---
```

#### Required Fields

**name** (string, required)
- Must be lowercase letters, numbers, and hyphens only
- Maximum 40 characters
- Should match the directory name
- Examples: `pdf-processor`, `data-analyzer`, `brand-guidelines`

**description** (string, required)
- Complete explanation of what the skill does
- Should include when to use the skill (triggers/contexts)
- Minimum 20 characters recommended
- This is the primary mechanism for skill triggering

#### Optional Fields

**license** (string, optional)
- License information for the skill
- Example: `license: Apache-2.0` or `license: Complete terms in LICENSE.txt`

### Markdown Body

The body contains instructions, examples, and guidelines that define the skill's behavior. Common sections include:

- Overview/Introduction
- Quick Start
- Detailed Instructions
- Examples
- Guidelines
- Resources/References

## Bundled Resources

### scripts/ Directory

Contains executable code (Python, Bash, etc.) for tasks requiring deterministic reliability.

**When to include:**
- Code that would be rewritten repeatedly
- Operations requiring deterministic reliability
- Automation scripts

**Best practices:**
- Make scripts executable (`chmod +x`)
- Include docstrings explaining usage
- Handle errors gracefully

### references/ Directory

Contains documentation intended to be loaded into context as needed.

**When to include:**
- API documentation
- Database schemas
- Domain knowledge
- Detailed workflow guides

**Best practices:**
- Keep files focused on specific topics
- Include table of contents for files over 100 lines
- Use clear, descriptive filenames

### assets/ Directory

Contains files used in output, not loaded into context.

**When to include:**
- Templates (PPTX, DOCX, etc.)
- Images and icons
- Boilerplate code
- Fonts

**Best practices:**
- Organize by type or purpose
- Use descriptive filenames
- Include any required licenses

## Progressive Disclosure

Skills use a three-level loading system:

1. **Metadata** (always loaded): name + description (~100 words)
2. **SKILL.md body** (when triggered): Instructions (<5k words recommended)
3. **Bundled resources** (as needed): Scripts, references, assets

This design minimizes context usage while providing full capability when needed.

## Validation Rules

The Skills Parser enforces these rules:

### Name Validation
- Lowercase letters, numbers, hyphens only: `^[a-z0-9-]+$`
- Maximum 40 characters
- No leading/trailing hyphens
- No consecutive hyphens

### Description Validation
- Non-empty
- Minimum 20 characters recommended
- Should explain both what and when

### Structure Validation
- SKILL.md must exist in root
- Resource directories must be actual directories
- Python scripts must have valid syntax

## Devin Knowledge Entry Format

The parser generates knowledge entries in this format:

```json
{
  "name": "skill-name",
  "description": "Skill description from frontmatter",
  "content": "Full markdown body content",
  "resources": {
    "scripts": ["script1.py", "script2.sh"],
    "references": ["api_reference.md"],
    "assets": ["template.pptx"]
  },
  "source": "anthropic-skills",
  "parsed_at": "2024-01-01T00:00:00Z",
  "metadata": {
    "format": "anthropic-skills",
    "version": "1.0",
    "source_path": "/path/to/original/skill"
  }
}
```

## Examples

### Minimal Skill

```
my-skill/
└── SKILL.md
```

SKILL.md:
```markdown
---
name: my-skill
description: A simple skill that does X when the user asks for Y
---

# My Skill

Instructions for using this skill...
```

### Full-Featured Skill

```
data-processor/
├── SKILL.md
├── scripts/
│   ├── process_data.py
│   └── validate_input.py
├── references/
│   ├── schema.md
│   └── api_docs.md
└── assets/
    └── template.csv
```

## Common Patterns

### Workflow-Based Skills
Best for sequential processes with clear steps.

### Task-Based Skills
Best for tool collections with different operations.

### Reference/Guidelines Skills
Best for standards, specifications, or brand guidelines.

### Capabilities-Based Skills
Best for integrated systems with multiple features.

## Troubleshooting

### "SKILL.md not found"
Ensure SKILL.md exists in the skill root directory (not in a subdirectory).

### "Invalid YAML frontmatter"
Check that frontmatter starts and ends with `---` on their own lines.

### "Missing required field"
Ensure both `name` and `description` are present in frontmatter.

### "Invalid skill name format"
Use only lowercase letters, numbers, and hyphens. No spaces or special characters.

## References

- [Agent Skills Specification](https://agentskills.io/specification)
- [What are skills?](https://support.claude.com/en/articles/12512176-what-are-skills)
- [Creating custom skills](https://support.claude.com/en/articles/12512198-creating-custom-skills)
