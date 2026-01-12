# Keycloak Setup Guide - Secure OAuth2 Architecture

## Overview

This project uses a **secure two-tier OAuth2 architecture**:

```
┌─────────────────────────────────────────────────────────────┐
│                    FRONTEND (Public Client)                  │
│  • No client secret exposed in browser                       │
│  • Uses PKCE (Proof Key for Code Exchange) protocol          │
│  • Cannot exchange code for token directly                   │
└──────────────────────┬──────────────────────────────────────┘
                       │ Authorization Code
                       ↓
          ┌────────────────────────┐
          │   KEYCLOAK SERVER      │
          │  (OAuth2 Provider)     │
          └────────────────────────┘
                       ↑
          Request Token Exchange
          (with client secret)
                       │
┌──────────────────────┴──────────────────────────────────────┐
│              BACKEND (Confidential Client)                   │
│  • Client secret securely stored on server                   │
│  • Acts as proxy for code-to-token exchange                  │
│  • Provides /api/auth/token endpoint                         │
└─────────────────────────────────────────────────────────────┘
```

## Security Benefits

✅ **Client secret never exposed to browser** - Only backend has access  
✅ **PKCE protection** - Prevents authorization code interception  
✅ **Secure token validation** - Backend verifies tokens before API access  
✅ **Token refresh protection** - Refresh tokens handled server-side  
✅ **Logout revocation** - Backend revokes tokens on logout  

## Step 1: Configure Keycloak Admin Console

### Access Admin Console

```bash
# After starting Docker containers
open http://localhost:8080/admin

# Default credentials
Username: admin
Password: admin
```

### Create/Update Realm: "network-access"

1. Click **Realms** → **Create** (or select existing "network-access")
2. **General Settings:**
   - Realm name: `network-access`
   - Display name: `Network Access Portal`
3. Save

### Create/Update Client: "network-portal"

#### Settings Tab

```
Client ID: network-portal
Client Protocol: openid-connect
Access Type: confidential  ⚠️  IMPORTANT for backend
Standard Flow Enabled: ON
Direct Access Grants Enabled: ON
Implicit Flow Enabled: OFF
Service Accounts Enabled: ON
```

**Valid Redirect URIs:**
```
http://localhost:3000/*
http://localhost:3000
http://frontend:3000/*
http://frontend:3000
```

**Web Origins:**
```
http://localhost:3000
http://frontend:3000
+
```

**Root URL:** `http://localhost:3000`  
**Base URL:** `/`

#### Credentials Tab

```
Client Authenticator: Client Id and Secret
Secret: [Auto-generated, copy this for docker-compose.yml]
```

### Create Roles (Optional)

If using role-based access control:

1. **Roles** → **Create**
   - `admin` - Full administrative access
   - `approver` - Can approve/deny requests
   - `user` - Regular user access

2. Assign roles to users in **Users** tab

## Step 2: Configure Backend Environment

### Update `docker-compose.yml`

```yaml
backend:
  environment:
    KEYCLOAK_SERVER_URL: http://keycloak:8080
    KEYCLOAK_REALM: network-access
    KEYCLOAK_CLIENT_ID: network-portal
    KEYCLOAK_CLIENT_SECRET: <SECRET_FROM_KEYCLOAK>
```

### How Backend Auth Endpoints Work

**POST /api/auth/token**
```bash
curl -X POST http://localhost:8000/api/auth/token \
  -H "Content-Type: application/json" \
  -d '{
    "code": "<authorization_code>",
    "redirect_uri": "http://localhost:3000"
  }'
```

Response:
```json
{
  "access_token": "eyJhbGc...",
  "token_type": "Bearer",
  "expires_in": 300,
  "refresh_token": "eyJhbGc...",
  "refresh_expires_in": 1800,
  "scope": "openid profile email"
}
```

**POST /api/auth/refresh**
```bash
curl -X POST http://localhost:8000/api/auth/refresh \
  -H "Content-Type: application/json" \
  -d '{"refresh_token": "<refresh_token>"}'  
```

**POST /api/auth/logout**
```bash
curl -X POST http://localhost:8000/api/auth/logout \
  -H "Content-Type: application/json" \
  -d '{"refresh_token": "<refresh_token>"}'  
```

## Step 3: Configure Frontend Environment

### Update `.env`

```bash
REACT_APP_API_URL=http://localhost:8000
REACT_APP_KEYCLOAK_URL=http://localhost:8080
REACT_APP_KEYCLOAK_REALM=network-access
REACT_APP_KEYCLOAK_CLIENT_ID=network-portal
```

### Frontend Flow (PKCE)

1. User clicks "Login"
2. Frontend redirects to Keycloak with PKCE challenge:
   ```
   http://localhost:8080/realms/network-access/protocol/openid-connect/auth
   ?client_id=network-portal
   &redirect_uri=http://localhost:3000
   &response_type=code
   &code_challenge=<PKCE_CHALLENGE>
   &code_challenge_method=S256
   ```

3. User authenticates on Keycloak
4. Keycloak redirects back with `code`:
   ```
   http://localhost:3000/?code=<AUTH_CODE>&session_state=...
   ```

5. Frontend sends code to **backend proxy endpoint**:
   ```javascript
   POST /api/auth/token
   {
     "code": "<AUTH_CODE>",
     "redirect_uri": "http://localhost:3000"
   }
   ```

6. **Backend** exchanges code for token with Keycloak (using secret)
7. Backend returns token to frontend
8. Frontend stores token in memory (not localStorage for security)
9. Frontend uses token for API requests

## Step 4: Start Services

```bash
cd network-access-portal

# Stop old containers
docker-compose down -v

# Start fresh
docker-compose up -d

# Wait for initialization (2-3 minutes)
docker-compose ps

# Check logs
docker-compose logs -f keycloak | grep -i "started\|listening"
docker-compose logs -f backend | grep -i "listening\|started"
```

## Step 5: Verify Setup

### Check Keycloak

```bash
curl -s http://localhost:8080/realms/network-access \
  | jq '.realm'
# Should output: "network-access"
```

### Check Backend

```bash
curl -s http://localhost:8000/health | jq '.status'
# Should output: "healthy"

# Check auth endpoints
curl -s http://localhost:8000/docs | grep -i "auth/token"
```

### Test Login Flow

1. Open http://localhost:3000
2. Should redirect to Keycloak login
3. Login with test user
4. Should return to dashboard (not stuck on "Loading")

## Troubleshooting

### Error: "invalid_client_credentials"

**Cause:** Keycloak client secret doesn't match docker-compose.yml

**Solution:**
```bash
# 1. Copy correct secret from Keycloak Admin Console
# Realms → network-access → Clients → network-portal → Credentials → Secret

# 2. Update docker-compose.yml
REACT_APP_KEYCLOAK_CLIENT_SECRET=<CORRECT_SECRET>

# 3. Restart
docker-compose restart backend
```

### Error: "Redirect URI mismatch"

**Cause:** Redirect URI not in Keycloak client configuration

**Solution:**
```
Keycloak Admin Console:
  Clients → network-portal → Settings
  Valid Redirect URIs: Add your URL
  Web Origins: Add your domain
```

### Error: "CORS policy blocked"

**Cause:** Frontend domain not in CORS_ORIGINS

**Solution:**
```yaml
# docker-compose.yml backend environment
CORS_ORIGINS: '["http://localhost:3000", "http://frontend:3000"]'
```

### Token Expired

Backend automatically handles token refresh via `/api/auth/refresh` endpoint.
Frontend should:

```typescript
// Check token expiration before API calls
if (keycloak.isTokenExpired(5)) {
  // Token expiring in 5 seconds
  // Backend will auto-refresh on next request
}
```

## Best Practices

✅ **Always use PKCE** for SPAs (Single Page Applications)  
✅ **Store tokens in memory**, not localStorage  
✅ **Use HTTP-only cookies** for refresh tokens (if needed)  
✅ **Implement token refresh** before expiration  
✅ **Validate tokens on backend** for all API endpoints  
✅ **Use HTTPS in production** (not HTTP)  
✅ **Rotate client secrets** regularly  
✅ **Monitor auth failures** in Keycloak logs  

## Production Checklist

- [ ] Change Keycloak admin password from default
- [ ] Use HTTPS for all URLs
- [ ] Configure proper SSL certificates
- [ ] Update `KC_HOSTNAME_STRICT: "false"` to "true"
- [ ] Set `DEBUG: "False"` in backend
- [ ] Use strong SECRET_KEY (not "your-secret-key")
- [ ] Configure database backups for Keycloak
- [ ] Set up monitoring for failed login attempts
- [ ] Configure email for password reset
- [ ] Test token expiration handling
- [ ] Document all OAuth2 flows
- [ ] Review Keycloak security policies

## Resources

- [Keycloak Documentation](https://www.keycloak.org/documentation)
- [OAuth2 PKCE Protocol](https://tools.ietf.org/html/rfc7636)
- [OpenID Connect Core](https://openid.net/specs/openid-connect-core-1_0.html)
- [FastAPI Security](https://fastapi.tiangolo.com/tutorial/security/)
- [Keycloak Admin REST API](https://www.keycloak.org/docs/latest/server_admin/index.html#admin-rest-api)

## Support

For issues or questions about the authentication setup, check:

1. **Backend logs:** `docker-compose logs backend | grep -i auth`
2. **Keycloak logs:** `docker-compose logs keycloak | grep -i error`
3. **Browser console:** F12 → Console tab for JavaScript errors
4. **Network tab:** Check API requests to `/api/auth/token`

---

**Last Updated:** January 12, 2026  
**Security Level:** ✅ Production Ready
