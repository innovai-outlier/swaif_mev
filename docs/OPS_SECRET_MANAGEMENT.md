# Secret Management (Client Operations)

## JWT secret requirements
- API requires `JWT_SECRET_KEY` from environment.
- Secret must be at least 32 chars and include at least 3 character classes (upper/lower/number/symbol).
- Placeholder or default values are rejected on startup.

## Installation workflow
- `./scripts/run.sh --mode docker bootstrap` and `--mode onprem bootstrap` now auto-generate and persist a strong `JWT_SECRET_KEY` when missing/placeholder.
- Generated secret is stored in:
  - Docker mode: `infra/compose/.env`
  - On-prem mode: `config/.env.onprem`

## Validate configuration before go-live
From `services/api`:

```bash
python -m app.config_check
```

This command returns non-zero and prints a failure reason if secret configuration is missing/weak.

## Secret rotation procedure
1. Generate a new secret in a secure terminal:
   ```bash
   python - <<'PY'
   import secrets
   print(secrets.token_urlsafe(48))
   PY
   ```
2. Update `JWT_SECRET_KEY` in the active environment file.
3. Roll restart API and worker.
4. Validate with `python -m app.config_check`.
5. Force user re-authentication window (old JWTs become invalid after rotation).

## Backup and restore guidance
- Include environment files containing `JWT_SECRET_KEY` in encrypted backup procedures.
- Recommended: use secret manager or encrypted vault; avoid plaintext ticket/email sharing.
- On restore, ensure the exact secret value is restored if active sessions must remain valid.
- If secret cannot be restored, set a new secret and communicate mandatory re-login to all users.
