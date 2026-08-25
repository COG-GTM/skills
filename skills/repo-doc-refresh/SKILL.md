---
name: repo-doc-refresh
description: >
  Refresh repository documentation from the current implementation. Use for
  README audits, scheduled documentation maintenance, architecture and endpoint
  updates, or requests to make docs accurately reflect the code while avoiding
  functional changes.
---

# Repository Documentation Refresh

Update documentation from evidence in the codebase and keep the change documentation-only.

## Verify the target before investing

1. Resolve the exact repository owner/name, requested ref, and default branch.
2. Confirm the checked-out repository matches the requested owner and remote.
3. If a PR is required, verify write/PR access immediately.
4. If the requested repo is missing, points to a different fork, or lacks required
   access, report the mismatch before substituting another repository or doing a
   large edit. For unattended runs, stop unless a documented fork workflow exists.

## Establish sources of truth

Read:

- `README`, contribution, setup, and architecture documents.
- Build manifests, lockfiles, tool-version files, and CI workflows.
- Application entrypoints and configuration.
- Public controllers, routes, GraphQL resolvers, CLI commands, or exported APIs.
- Core domain models, services, persistence mappings, schemas, and migrations.
- Existing tests that demonstrate supported behavior.

Use the repository's own commands and version declarations. Do not infer an exact
version from memory or invent features from dependency names.

Build a short evidence map:

```text
doc claim | implementation/config source | current status | required edit
```

## Update documentation

Cover only what the code supports:

- Prerequisites and exact setup/build/run/test commands.
- Technology stack and versions declared by the repository.
- Configuration and environment variables without exposing values.
- REST, GraphQL, CLI, or other public interfaces.
- Project structure and architecture boundaries.
- Known limitations that materially affect setup or usage.

Prefer updating existing documents over creating new ones. Add a new architecture
or endpoint document only when it removes substantial README clutter or fills a
clear gap.

Do not make functional code changes. Record bugs, dead code, stale dependencies,
and inconsistencies as follow-up findings rather than fixing them in the docs PR.

## Validate

1. Check every changed command against the repository.
2. Run the relevant lightweight compile, format, lint, link, or documentation check.
3. If the user requested broader verification, run it; otherwise avoid unrelated
   expensive builds.
4. Verify links, headings, code fences, and referenced paths.
5. Confirm the final diff contains documentation files only.
6. If the user requested PR delivery, open a focused PR that distinguishes
   documentation changes from recommended code follow-ups.

When a check fails, separate failures caused by the documentation change from
pre-existing repository failures and include evidence for that distinction.

## Completion checklist

- [ ] Repository identity, branch, and PR access were checked first
- [ ] Claims are grounded in code, config, CI, or tests
- [ ] Commands and versions were verified rather than guessed
- [ ] No functional code was changed
- [ ] The diff is documentation-only
- [ ] Code issues are listed as follow-ups, not silently fixed
