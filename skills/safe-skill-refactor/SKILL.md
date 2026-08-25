---
name: safe-skill-refactor
description: >
  Refactor or shorten an existing SKILL.md without losing executable behavior,
  safety controls, tool permissions, retries, validation loops, or required
  outputs. Use whenever a user asks to make a skill concise, reorganize it, or
  remove redundant guidance.
---

# Safe Skill Refactor

Make the skill easier to follow while preserving its behavioral contract.

## Read the complete skill package

1. Read the full `SKILL.md`, frontmatter, referenced assets, scripts, templates,
   sibling skills, and repository rules that it depends on.
2. Identify the skill's callers and expected invocation style.
3. Do not edit generated copies or installed plugin caches; edit the source package.

## Extract the behavioral contract

Before changing prose, inventory:

```text
trigger | prerequisite | input | command/API call | retry/loop |
safety control | validation | output | exception
```

Explicitly capture:

- Frontmatter fields, tool restrictions, and permissions.
- Required environment variables and how values are masked.
- Every executable command, API request, health check, polling loop, and timeout.
- File wiring, route registration, configuration entries, and naming conventions.
- Preconditions and expected failures.
- Required tests, screenshots, recordings, PR actions, and user approvals.

This contract is the acceptance test for the rewrite.

## Classify proposed removals

Remove or compress:

- Repeated explanations already expressed by an executable step.
- Large example matrices that can become one representative example.
- Duplicated checklists covering the same contract item.
- Historical commentary that does not affect execution.

Preserve:

- Commands and command ordering.
- Health polling, retries, triggers, and verification queries.
- Secret masking and other security controls.
- Integration wiring and route mounting.
- Edge cases that change the procedure.
- Required outputs and completion criteria.

If the user wants a behavior change, separate it from the concision refactor and
call it out explicitly.

## Rewrite

1. Keep YAML frontmatter valid and make the description trigger-specific.
2. Organize the body as a short ordered procedure.
3. Prefer one runnable example over many near-duplicates.
4. Use tables only when they reduce repetition.
5. Keep commands copy-pasteable; define variables before use.
6. Keep comments focused on intent, not the history of the edit.

## Validate semantically

After rewriting:

1. Compare every contract item against the new skill.
2. Verify all referenced paths and assets still exist.
3. Check shell snippets for undefined variables, quoting, masking, and failure modes.
4. Dry-run or safely execute non-destructive checks when possible.
5. Run any repository validation for skills or Markdown.
6. Inspect the diff specifically for deleted verbs such as `run`, `verify`, `poll`,
   `mount`, `append`, `trigger`, `mask`, and `retry`.

Do not use line-count reduction as the success criterion. The rewrite succeeds only
when the same valid invocation produces the same required outcome and safeguards.

## Completion checklist

- [ ] Frontmatter and invocation behavior are preserved
- [ ] Every command, loop, wiring step, and safety control is accounted for
- [ ] Referenced files and examples resolve
- [ ] No secret-revealing command was introduced
- [ ] The concise version is runnable without consulting the deleted prose
- [ ] Any intentional behavior change is separately documented
