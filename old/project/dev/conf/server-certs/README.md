# SSL Certificates

Self-signed certificates have been automatically generated for development:
- `fullchain.pem` - Full certificate chain
- `privkey.pem` - Private key

## For Production

Replace these self-signed certificates with proper SSL certificates from a Certificate Authority (e.g., Let's Encrypt).

## Regenerate Self-Signed Certificates

If needed, regenerate them with:
```bash
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
  -keyout privkey.pem -out fullchain.pem \
  -subj "/CN=localhost"
```
