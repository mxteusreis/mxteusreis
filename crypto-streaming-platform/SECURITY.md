# Security considerations

- Do not commit `.env` with secrets.
- Restrict CORS to trusted origins in production.
- Add rate limiting (e.g., reverse proxy or middleware) for public `/bi/*` endpoints.
- Validate query params (`limit`, `days`, timestamps) to reduce abuse.
- Avoid exposing filesystem paths or stack traces in API errors.
