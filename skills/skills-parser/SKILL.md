---
name: skills-parser
description: Parse and integrate Anthropic Skills files into Devin's knowledge system. Use this skill when customers want to import skills.md files (following the Anthropic Agent Skills format) into Devin, convert skills from the Anthropic format to Devin-compatible format, or add external skills to Devin's knowledge base. This skill automatically extracts YAML frontmatter metadata, markdown body content, and bundled resources (scripts, references, assets) from skill directories.
---

# Skills Parser

This skill provides automated parsing and integration of Anthropic Skills files into Devin's knowledge system, demonstrating full support for the Agent Skills standard.

## Overview

The Skills Parser accepts skill directories containing SKILL.md files (following the Anthropic Agent Skills format) and converts them into Devin-compatible knowledge entries. The parser handles the complete skill structure including metadata, instructions, and bundled resources.

## Quick Start

To parse and integrate a skill into Devin's knowledge system:

```bash
python scripts/parse_skill.py <path-to-skill-directory>
```

Example:
```bash
python scripts/parse_skill.py /path/to/my-custom-skill
```

The script will:
1. Validate the skill structure
2. Extract YAML frontmatter (name, description)
3. Parse the markdown body content
4. Discover and catalog bundled resources
5. Generate a Devin-compatible knowledge entry
6. Provide confirmation of successful integration

## Skill Structure Requirements

The parser expects skills to follow the Anthropic Agent Skills format:

```
skill-name/
├── SKILL.md (required)
│   ├── YAML frontmatter (name, description)
│   └── Markdown instructions
└── Bundled Resources (optional)
    ├── scripts/          - Executable code (Python/Bash/etc.)
    ├── references/       - Documentation for context loading
    └── assets/           - Files used in output (templates, etc.)
```

### SKILL.md Format

Every SKILL.md must contain:

**YAML Frontmatter** (required):
```yaml
---
name: skill-name
description: Complete description of what the skill does and when to use it
---
```

**Markdown Body** (required):
Instructions, examples, and guidelines that define the skill's behavior.

## Parsing Workflow

### Step 1: Validate Skill Structure

Before parsing, validate the skill directory:

```bash
python scripts/validate_skill.py <path-to-skill-directory>
```

This checks:
- SKILL.md exists and is readable
- YAML frontmatter is valid with required fields
- Directory structure follows conventions
- Resource directories are properly organized

### Step 2: Parse and Extract

Run the main parser to extract all components:

```bash
python scripts/parse_skill.py <path-to-skill-directory>
```

The parser extracts:
- **Metadata**: name, description from YAML frontmatter
- **Body**: Full markdown content after frontmatter
- **Scripts**: List of executable files in scripts/
- **References**: Documentation files in references/
- **Assets**: Resource files in assets/

### Step 3: Generate Knowledge Entry

The parser automatically generates a Devin-compatible knowledge entry in JSON format:

```bash
python scripts/parse_skill.py <path-to-skill-directory> --output knowledge_entry.json
```

Output format:
```json
{
  "name": "skill-name",
  "description": "Skill description",
  "content": "Full markdown body content",
  "resources": {
    "scripts": ["script1.py", "script2.sh"],
    "references": ["api_reference.md", "guide.md"],
    "assets": ["template.pptx", "logo.png"]
  },
  "source": "anthropic-skills",
  "parsed_at": "2024-01-01T00:00:00Z"
}
```

### Step 4: Integrate into Devin

To add the parsed skill to Devin's knowledge system:

```bash
python scripts/integrate_skill.py <knowledge_entry.json>
```

Or use the all-in-one command:

```bash
python scripts/parse_skill.py <path-to-skill-directory> --integrate
```

## Batch Processing

To parse multiple skills at once:

```bash
python scripts/batch_parse.py <skills-directory> --output <output-directory>
```

Example:
```bash
python scripts/batch_parse.py ./my-skills --output ./parsed-skills
```

## Validation Rules

The parser enforces these validation rules:

1. **Name**: Must be lowercase, hyphen-separated, max 40 characters
2. **Description**: Must be non-empty and descriptive
3. **SKILL.md**: Must exist in the skill root directory
4. **Frontmatter**: Must be valid YAML with `name` and `description` fields

## Error Handling

The parser provides clear error messages for common issues:

| Error | Cause | Solution |
|-------|-------|----------|
| `SKILL.md not found` | Missing main file | Create SKILL.md in skill root |
| `Invalid YAML frontmatter` | Malformed YAML | Check YAML syntax |
| `Missing required field: name` | No name in frontmatter | Add `name:` field |
| `Missing required field: description` | No description | Add `description:` field |
| `Invalid skill name format` | Name doesn't follow conventions | Use lowercase, hyphens only |

## Integration Confirmation

After successful integration, the parser outputs:

```
Successfully parsed skill: my-skill-name
  - Name: my-skill-name
  - Description: [first 100 chars of description]...
  - Scripts: 3 files
  - References: 2 files
  - Assets: 1 file

Skill has been added to Devin's knowledge system.
You can now use this skill by mentioning it in your requests.
```

## Resources

- **scripts/parse_skill.py**: Main parsing script
- **scripts/validate_skill.py**: Skill validation utility
- **scripts/integrate_skill.py**: Knowledge system integration
- **scripts/batch_parse.py**: Batch processing utility
- **references/skill_format.md**: Detailed format specification
