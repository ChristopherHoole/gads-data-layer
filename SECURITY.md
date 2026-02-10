# Security

- Never commit production secrets (developer tokens, OAuth refresh tokens, client secrets).
- Prefer environment variables or a local untracked config for real credentials.
- Rotate any credential if it is ever exposed publicly.
