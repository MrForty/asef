# Contributing to ASEF

Thank you for helping improve ASEF. Keep each contribution focused, portable
across coding agents, and economical in context and token use.

## Before opening a pull request

1. Open an issue or discussion first when the change introduces a new rule,
   route, module, or workflow.
2. Create a branch from `main` and make the smallest coherent change.
3. Keep each rule in one authoritative document; link to it instead of copying
   it into other files.
4. Preserve `AUTO`, `ECONOMY`, progressive context, and the
   `deduce -> verify -> ask` policy unless the change explicitly updates them.
5. Update `README.md`, examples, or `CHANGELOG.md` when the public behavior
   changes.

## Verify locally

```bash
python tools/asef_lint.py --verbose
python tools/test_asef_lint.py
```

## Pull request scope

Describe the problem, the files changed, the behavior preserved or changed,
and the verification you ran. Do not include unrelated formatting or generated
files.

## Reporting problems

Use an issue for reproducible defects and a discussion for questions or early
ideas. Report security-sensitive findings privately as described in
[`SECURITY.md`](SECURITY.md).
