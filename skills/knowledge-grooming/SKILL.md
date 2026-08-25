---
name: knowledge-grooming
description: >
  Audit and groom Devin knowledge notes. Use when asked to review, deduplicate,
  clean up, organize, or resolve contradictions in a knowledge base. Separates
  safe mechanical changes from conflicts that require an owner decision.
---

# Knowledge Grooming

Produce a safe, reviewable knowledge cleanup instead of rewriting notes opportunistically.

## Define scope

1. Confirm the requested organization, folder, repository, product, or author scope.
2. List every note in scope and fetch each full body before judging it.
3. Unless explicitly requested, exclude:
   - Auto-generated repository indexes.
   - System-owned notes.
   - Notes outside the requested product or repository.
4. Never infer note contents from a title or scope string alone.

## Build the audit

For each note, record:

```text
id | name | author | scope | category | proposed action | confidence
```

Use these categories:

- `empty`: no meaningful content.
- `exact-duplicate`: materially identical body and scope.
- `subset-duplicate`: one note adds no information beyond another.
- `scope-overlap`: similar content applies to different scopes.
- `contradiction`: instructions cannot both be followed in the overlapping scope.
- `stale`: references removed behavior, tooling, ownership, or identifiers.
- `broken-reference`: links to a missing note, file, issue, or resource.
- `healthy`: distinct, current, and correctly scoped.

Normalize whitespace and formatting when comparing, but preserve meaningful wording,
priority terms, exceptions, and scope differences.

## Decide what is safe

Safe mechanical proposals:

- Delete empty placeholders.
- Delete exact duplicates while keeping the clearer or better-scoped canonical note.
- Merge strict subsets into a canonical note without losing unique content.
- Repair a broken reference only when the intended target is unambiguous.
- Narrow an obviously overbroad scope when the body names a single product or repo.

Require an owner decision when:

- Two notes prescribe incompatible behavior.
- The canonical identifier, project key, owner, or policy is unclear.
- A merge would change precedence or broaden applicability.
- A stale-looking rule may still be required by an external workflow.

Never choose a winner in a contradiction based only on recency.

## Apply changes

1. Present a compact plan grouped into delete, merge, update, and unresolved.
2. Preserve user-authored knowledge over generated or system suggestions when they
   conflict, unless the user explicitly says otherwise.
3. Apply approved changes in bounded batches.
4. Re-fetch changed notes after each batch and verify scopes, links, and retained
   unique content.
5. Do not put secrets, tokens, private keys, or temporary session details into notes.

## Report

Return:

- Number of notes reviewed and excluded.
- Changes applied or awaiting approval.
- Canonical notes selected.
- Contradictions requiring decisions, quoting only the conflicting clauses.
- Broken references that could not be repaired safely.

## Completion checklist

- [ ] Every in-scope note body was fetched
- [ ] Generated/system notes were excluded unless explicitly requested
- [ ] No note was deleted based on title alone
- [ ] Unique content and scope exceptions were preserved
- [ ] Contradictions were escalated rather than guessed
- [ ] Updated notes were re-read after mutation
