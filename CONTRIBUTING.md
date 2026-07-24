# Contributing

1. Keep the Skill portable; do not add project-specific paths, credentials,
   service URLs, or model names.
2. Update `VERSION` and `CHANGELOG.md` for user-visible behavior changes.
3. Keep generated output additive and idempotent.
4. Add or update an evaluation prompt for new workflows.
5. Run the Skill validator and script tests before committing.

Suggested checks:

```powershell
python <skill-creator>/scripts/quick_validate.py .
python -m pytest tests -q
```
