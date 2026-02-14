# Web Security Study Guide

This short guide covers essential web security topics a security engineer should know.

## TLS & Certificates

- TLS provides confidentiality and integrity for data in transit.
- Certificates (X.509) are issued by CAs; trust chains are validated by clients.
- Certificate pinning binds a certificate/public key to a client but complicates rotation.
- Mutual TLS (mTLS) authenticates both client and server.

## Certificate Lifecycle

- Key generation, CSR submission, issuance, rotation, and revocation (CRL/OCSP).
- Use short-lived certs where possible and automate renewal (e.g., ACME/Let's Encrypt).

## API Security

- Use strong authentication (OAuth2, JWT with proper validation) and authorization checks.
- Protect secrets: store API keys in secret managers, not in source control.
- Implement rate limiting, input validation, and logging/monitoring.

## Multi-Factor Authentication (MFA)

- Use MFA for privileged access. Prefer phishing-resistant factors (security keys, FIDO2).

## HTTP Security Headers

- HSTS (Strict-Transport-Security) — enforce HTTPS.
- Content-Security-Policy — reduce XSS risk.
- X-Frame-Options / frame-ancestors — prevent clickjacking.

## Session & Token Best Practices

- Use short-lived access tokens and refresh tokens with rotation.
- Set cookies with `Secure`, `HttpOnly`, and `SameSite` attributes.

## Monitoring & Incident Response

- Collect TLS/HTTPS metrics, cert expiry alerts, and authentication anomalies.

## Further Reading

- RFC 8446 (TLS 1.3), OWASP API Security Top 10, NIST guidance on PKI
