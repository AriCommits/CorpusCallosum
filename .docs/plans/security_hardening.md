# Security Hardening Plan

Generated from comprehensive security audit on 2026-03-30.
Based on HashiCorp Vault best practices for Python applications.

## Architecture Decision: Vault Integration Pattern

### Recommended Approach: AppRole + hvac Client

For CorpusCallosum, the recommended Vault integration uses:

1. **AppRole authentication** — Machine-to-machine auth designed for applications
2. **hvac Python client** — Official HashiCorp Vault Python SDK
3. **KV v2 secrets engine** — For static secrets (API keys, database passwords)
4. **Short-lived tokens** — TTL-based token lifecycle with automatic renewal
5. **Vault Agent sidecar** (Docker deployments) — Manages token lifecycle, eliminates app-level Vault logic

### Why AppRole over alternatives?

| Method | Fit for CorpusCallosum | Reason |
|--------|----------------------|--------|
| AppRole | Best fit | Designed for apps, no external IdP needed |
| Kubernetes auth | Good (if deployed on K8s) | Requires K8s cluster |
| Token auth | Acceptable | Manual token management overhead |
| AWS/GCP auth | Good (if on cloud) | Tied to specific cloud provider |
| JWT/OIDC | Overkill | Requires identity provider |

### Secret Delivery Flow

```
┌─────────────┐     ┌──────────────┐     ┌─────────────┐
│  RoleID     │     │   SecretID   │     │   Vault     │
│  (env var)  │     │  (wrapped)   │     │   Server    │
└──────┬──────┘     └──────┬───────┘     └──────┬──────┘
       │                   │                    │
       └────────┬──────────┘                    │
                │                               │
         AppRole Login                          │
                │                               │
                └──────────────┬────────────────┘
                               │
                        Vault Token
                        (short-lived)
                               │
                        Read Secrets
                               │
                    ┌──────────┴──────────┐
                    │                     │
             API Keys              DB Passwords
             Model Keys            TLS Certs
```

## Phase 1: Critical Fixes (Immediate)

### 1.1 Remove Hardcoded Credentials
- [ ] Replace hardcoded Postgres password in docker-compose with env var interpolation
- [ ] Replace hardcoded Postgres password in otel-collector-config.yaml with env var
- [ ] Add `.env` file template and gitignore entry
- [ ] Use Docker secrets for production deployments

### 1.2 Fix Path Traversal Vulnerabilities
- [ ] Implement strict allowlist-based path validation in `ingest.py`
- [ ] Use `os.path.commonpath()` to verify resolved paths are within vault directory
- [ ] Add path validation in MCP `ingest_documents` tool
- [ ] Validate collection names against alphanumeric pattern

### 1.3 Stop Leaking Sensitive Information
- [ ] Replace raw exception messages in MCP tools/resources with generic errors
- [ ] Redact credentials from OTLP endpoint logging
- [ ] Add `max_length` constraints to all Pydantic request models
- [ ] Add request body size limiting to uvicorn

### 1.4 Enable Authentication by Default
- [ ] Default `auth_enabled` to `True` in config
- [ ] Default server bind to `127.0.0.1` instead of `0.0.0.0`
- [ ] Add startup warning when auth is disabled
- [ ] Add CORS middleware with explicit allowed origins

## Phase 2: Vault Integration

### 2.1 Vault Client Module (`src/corpus_callosum/vault_client.py`)
- [ ] Create `VaultSecretsManager` class using `hvac` library
- [ ] Support AppRole authentication (RoleID from env, SecretID from wrapped token)
- [ ] Support token-based auth (fallback for development)
- [ ] Implement automatic token renewal before TTL expiry
- [ ] Implement circuit breaker for Vault unavailability
- [ ] Cache secrets with TTL to reduce Vault calls

### 2.2 Secrets Migration
- [ ] Move API keys from YAML config to Vault KV store
- [ ] Move Postgres credentials to Vault KV store
- [ ] Move model API keys to Vault KV store
- [ ] Move OTLP credentials (if any) to Vault KV store
- [ ] Create migration script to import existing secrets into Vault

### 2.3 Config Integration
- [ ] Add `vault` section to config schema
- [ ] Support `vault.enabled` toggle (graceful degradation)
- [ ] Support `vault.address`, `vault.auth_method`, `vault.role_id`, `vault.secret_id`
- [ ] Support `vault.token_bound_cidrs` for IP restriction
- [ ] Fall back to config file secrets when Vault is unavailable (with warning)

### 2.4 Vault Policies (Terraform/HCL)
- [ ] Define `corpus-callosum-read` policy (read-only access to KV paths)
- [ ] Define `corpus-callosum-admin` policy (full access for setup)
- [ ] Create AppRole with `secret_id_bound_cidrs` restriction
- [ ] Set `secret_id_num_uses=1` for single-use SecretIDs
- [ ] Set token TTL to 1 hour with max 4 hours

### 2.5 Docker Integration
- [ ] Add Vault Agent sidecar container to docker-compose
- [ ] Configure Vault Agent template to render secrets as env vars
- [ ] Mount Vault Agent token sink as tmpfs
- [ ] Remove hardcoded credentials from compose file

## Phase 3: Docker Hardening

### 3.1 Container Security
- [ ] Add non-root user to Dockerfile
- [ ] Add `security_opt: [no-new-privileges:true]` to all services
- [ ] Add resource limits (memory, CPU) to all services
- [ ] Add `read_only: true` with tmpfs for writable dirs

### 3.2 Network Security
- [ ] Bind internal service ports to `127.0.0.1` only
- [ ] Remove public port mappings for Postgres, OTel collector
- [ ] Use Docker networks for inter-service communication
- [ ] Pin Docker image versions (no `:latest` tags)

### 3.3 Dependency Security
- [ ] Generate and commit lock file (`uv.lock` or `requirements-lock.txt`)
- [ ] Add `pip audit` to CI pipeline
- [ ] Pin exact versions in Docker base image

## Phase 4: API & MCP Hardening

### 4.1 MCP Authentication
- [ ] Add API key authentication to MCP HTTP transport
- [ ] Add rate limiting to MCP server
- [ ] Validate all MCP tool input parameters

### 4.2 API Security
- [ ] Add request body size limits
- [ ] Add CORS middleware
- [ ] Protect OpenAPI docs in production mode
- [ ] Add thread-safe rate limiter (use `threading.Lock`)
- [ ] Add `session_id` validation (format + length constraints)

### 4.3 Observability Security
- [ ] Remove debug exporter from production OTel config
- [ ] Add structured logging with trace context
- [ ] Add audit logging for sensitive operations (ingest, key changes)

## Phase 5: Testing & CI

### 5.1 Security Tests
- [ ] Add path traversal test cases
- [ ] Add input validation test cases
- [ ] Add auth bypass test cases
- [ ] Add rate limiting test cases

### 5.2 CI Integration
- [ ] Add `pip audit` / `safety check` to CI
- [ ] Add secret scanning (gitleaks or trufflehog)
- [ ] Add dependency vulnerability scanning

## Reference: Vault Setup Commands

```bash
# Enable KV v2 secrets engine
vault secrets enable -path=corpus-callosum kv-v2

# Write secrets
vault kv put corpus-callosum/api-keys \
  primary_key="sk-xxx" \
  secondary_key="sk-yyy"

vault kv put corpus-callosum/database \
  postgres_user="otel" \
  postgres_password="auto-generated"

vault kv put corpus-callosum/model \
  openai_api_key="sk-xxx" \
  anthropic_api_key="sk-xxx"

# Create policy
vault policy write corpus-callosum-read - <<EOF
path "corpus-callosum/*" {
  capabilities = ["read"]
}
EOF

# Create AppRole
vault write auth/approle/role/corpus-callosum \
  secret_id_ttl=10m \
  token_ttl=1h \
  token_max_ttl=4h \
  token_bound_cidrs="10.0.0.0/8" \
  policies="corpus-callosum-read"

# Get RoleID (non-secret, can be embedded)
vault read auth/approle/role/corpus-callosum/role-id

# Generate wrapped SecretID (single-use, 60s TTL)
vault write -wrap-ttl=60s -f auth/approle/role/corpus-callosum/secret-id
```

## Config Schema (Proposed)

```yaml
vault:
  enabled: false
  address: "http://vault:8200"
  auth_method: "approle"  # or "token"
  role_id: "${VAULT_ROLE_ID}"        # From env var
  secret_id: "${VAULT_SECRET_ID}"    # From env var (wrapped)
  token: "${VAULT_TOKEN}"            # Fallback for dev
  token_ttl: 3600                    # 1 hour
  token_max_ttl: 14400               # 4 hours
  token_bound_cidrs: []              # IP restrictions
  secret_paths:
    api_keys: "corpus-callosum/api-keys"
    database: "corpus-callosum/database"
    model: "corpus-callosum/model"
  cache_ttl: 300                     # 5 min secret cache
  retry_max_attempts: 3
  retry_backoff_ms: 1000
```
