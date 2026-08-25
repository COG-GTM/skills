---
name: sonarqube-pr-remediation
description: >
  Remediate SonarQube or SonarCloud findings on an existing pull-request branch.
  Use when given a PR, branch, quality-gate failure, or Sonar issue payload and
  asked to apply secure fixes, push to the same branch, and report the result.
---

# SonarQube PR Remediation

Fix the reported findings defensively with minimal scope and preserve the existing
pull-request workflow.

## Confirm inputs

Identify:

- Repository, pull request, source branch, and target branch.
- Changed files in the PR.
- Sonar project key, quality-gate conditions, issue keys, rules, severities, lines,
  and messages.
- Required commit message or workflow marker such as `[devin-fix]`.
- Whether to push the existing branch, comment on the PR, and wait for a rescan.

If issue details are incomplete, retrieve the specific issues from the configured
Sonar integration or API before editing. Never guess the vulnerable code path.

## Reproduce and scope

1. Check out and update the exact PR source branch.
2. Inspect the PR diff and run `git diff --name-only` against the target branch.
3. Read the surrounding implementation, callers, tests, and configuration.
4. Reproduce the issue with the smallest relevant test or static-analysis command
   when possible.
5. Restrict edits to files changed by the PR when the task requires it.

If a secure fix genuinely requires another file, explain why and obtain approval
before expanding a strict user-defined scope.

## Apply secure fixes

- Fix root causes rather than suppressing rules or adding broad exclusions.
- Keep TLS certificate and hostname validation enabled.
- Parameterize database queries; do not concatenate untrusted input.
- Replace embedded credentials with existing secret/configuration mechanisms.
- Use current, approved cryptographic primitives and safe randomness.
- Validate inputs and return controlled errors instead of allowing crashes.
- Treat security hotspots as review items: verify context before changing behavior.

Do not weaken repository security policy, dependency-age controls, CI gates, or
scanner configuration to make the check pass.

## Verify

1. Run targeted tests for each changed behavior.
2. Run the repository's applicable lint, typecheck, and static-analysis commands.
3. Re-run `git diff --name-only` and inspect the final diff for scope creep.
4. Confirm no secrets, debug output, disabled validation, or rule suppressions were
   introduced.
5. Create the required single commit when the workflow specifies one.
6. Push to the existing PR branch. Do not create a new PR unless explicitly asked.
7. Comment on the PR with the issue keys, root causes, fixes, and verification.

## Quality-gate follow-through

1. Trigger or wait for the normal Sonar rescan.
2. Poll the quality gate and inspect any remaining new-code findings.
3. Repeat the fix/verify loop for in-scope findings.
4. After three failed remediation attempts, stop and ask for help with evidence.
5. If the rescan is still pending, say so; do not claim the gate passed.

## Completion checklist

- [ ] Exact PR branch and issue details were verified
- [ ] Changes stayed within the requested file scope
- [ ] Findings were fixed without suppression or weakened controls
- [ ] Tests, lint/typecheck, and diff inspection were completed
- [ ] Commit and push behavior matches the existing PR workflow
- [ ] PR comment explains fixes and verification
- [ ] Final quality-gate status is verified or explicitly pending
