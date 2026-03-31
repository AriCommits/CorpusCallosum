"""HashiCorp Vault integration for secrets management.

Uses the hvac library to authenticate with Vault and retrieve secrets.
Supports AppRole and token-based authentication.
"""

from __future__ import annotations

import logging
import os
import threading
import time
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    import hvac

logger = logging.getLogger(__name__)


@dataclass
class VaultConfig:
    """Configuration for Vault integration."""

    enabled: bool = False
    address: str = "http://localhost:8200"
    auth_method: str = "token"
    token: str | None = None
    role_id: str | None = None
    secret_id: str | None = None
    token_ttl: int = 3600
    token_max_ttl: int = 14400
    token_bound_cidrs: list[str] = field(default_factory=list)
    secret_paths: dict[str, str] = field(
        default_factory=lambda: {
            "api_keys": "corpus-callosum/api-keys",
            "database": "corpus-callosum/database",
            "model": "corpus-callosum/model",
        }
    )
    cache_ttl: int = 300
    retry_max_attempts: int = 3
    retry_backoff_ms: int = 1000


class _SecretCache:
    """Thread-safe cache for Vault secrets with TTL."""

    def __init__(self, ttl: int = 300) -> None:
        self._cache: dict[str, tuple[Any, float]] = {}
        self._lock = threading.Lock()
        self._ttl = ttl

    def get(self, key: str) -> Any | None:
        with self._lock:
            if key in self._cache:
                value, timestamp = self._cache[key]
                if time.time() - timestamp < self._ttl:
                    return value
                del self._cache[key]
        return None

    def set(self, key: str, value: Any) -> None:
        with self._lock:
            self._cache[key] = (value, time.time())

    def clear(self) -> None:
        with self._lock:
            self._cache.clear()


class VaultSecretsManager:
    """Manages secrets from HashiCorp Vault.

    Usage:
        config = VaultConfig(enabled=True, address="http://vault:8200", ...)
        vault = VaultSecretsManager(config)
        vault.authenticate()

        api_keys = vault.get_secret("api_keys")
        db_creds = vault.get_secret("database")
    """

    def __init__(self, config: VaultConfig) -> None:
        self.config = config
        self._client: hvac.Client | None = None
        self._cache = _SecretCache(ttl=config.cache_ttl)
        self._lock = threading.Lock()
        self._authenticated = False

    @property
    def available(self) -> bool:
        return self.config.enabled and self._authenticated

    def authenticate(self) -> bool:
        """Authenticate with Vault using the configured method."""
        if not self.config.enabled:
            logger.debug("Vault integration disabled")
            return False

        try:
            import hvac
        except ImportError:
            logger.warning("Vault enabled but hvac not installed. Install with: pip install hvac")
            return False

        try:
            self._client = hvac.Client(url=self.config.address)

            if self.config.auth_method == "approle":
                self._authenticate_approle()
            elif self.config.auth_method == "token":
                self._authenticate_token()
            else:
                logger.error("Unknown auth method: %s", self.config.auth_method)
                return False

            if self._client.is_authenticated():
                self._authenticated = True
                logger.info("Authenticated with Vault (%s)", self.config.auth_method)
                return True

            logger.error("Vault authentication failed")
            return False

        except Exception as exc:
            logger.error("Failed to authenticate with Vault: %s", exc)
            return False

    def _authenticate_approle(self) -> None:
        """Authenticate using AppRole method."""
        if not self._client:
            return

        role_id = self.config.role_id or os.getenv("VAULT_ROLE_ID")
        secret_id = self.config.secret_id or os.getenv("VAULT_SECRET_ID")

        if not role_id or not secret_id:
            raise ValueError(
                "AppRole authentication requires role_id and secret_id. "
                "Set VAULT_ROLE_ID and VAULT_SECRET_ID environment variables."
            )

        response = self._client.auth.approle.login(
            role_id=role_id,
            secret_id=secret_id,
        )

        if response and "auth" in response:
            self._client.token = response["auth"]["client_token"]

    def _authenticate_token(self) -> None:
        """Authenticate using a static token."""
        if not self._client:
            return

        token = self.config.token or os.getenv("VAULT_TOKEN")
        if not token:
            raise ValueError(
                "Token authentication requires a token. "
                "Set VAULT_TOKEN environment variable or config vault.token."
            )

        self._client.token = token

        if not self._client.is_authenticated():
            raise ValueError("Invalid Vault token")

    def get_secret(self, secret_name: str) -> dict[str, str] | None:
        """Retrieve a secret from Vault.

        Args:
            secret_name: Key from secret_paths config (e.g. "api_keys", "database")

        Returns:
            Dict of secret key-value pairs, or None if not found
        """
        if not self.available or not self._client:
            return None

        path = self.config.secret_paths.get(secret_name)
        if not path:
            logger.warning("Unknown secret path: %s", secret_name)
            return None

        cache_key = f"{path}"
        cached = self._cache.get(cache_key)
        if cached is not None:
            return cached

        for attempt in range(self.config.retry_max_attempts):
            try:
                response = self._client.secrets.kv.v2.read_secret_version(path=path)
                data = response.get("data", {}).get("data", {})
                if data:
                    self._cache.set(cache_key, data)
                    return dict(data)
                return None
            except Exception as exc:
                logger.warning(
                    "Vault read attempt %d failed for %s: %s",
                    attempt + 1,
                    path,
                    exc,
                )
                if attempt < self.config.retry_max_attempts - 1:
                    time.sleep(self.config.retry_backoff_ms / 1000 * (attempt + 1))

        return None

    def get_secret_value(
        self, secret_name: str, key: str, default: str | None = None
    ) -> str | None:
        """Get a specific value from a secret.

        Args:
            secret_name: Key from secret_paths config
            key: The specific key within the secret
            default: Default value if not found
        """
        secret = self.get_secret(secret_name)
        if secret is None:
            return default
        return secret.get(key, default)

    def clear_cache(self) -> None:
        """Clear the secret cache."""
        self._cache.clear()

    def renew_token(self) -> bool:
        """Renew the current Vault token."""
        if not self._client or not self._authenticated:
            return False

        try:
            self._client.auth.token.renew_self(increment=self.config.token_ttl)
            self._cache.clear()
            logger.info("Vault token renewed")
            return True
        except Exception as exc:
            logger.error("Failed to renew Vault token: %s", exc)
            self._authenticated = False
            return False


_instance: VaultSecretsManager | None = None
_init_lock = threading.Lock()


def get_vault(config: VaultConfig | None = None) -> VaultSecretsManager:
    """Get or create the global Vault secrets manager instance."""
    global _instance

    if _instance is not None:
        return _instance

    with _init_lock:
        if _instance is None:
            cfg = config or VaultConfig()
            _instance = VaultSecretsManager(cfg)
            if cfg.enabled:
                _instance.authenticate()
        return _instance


def reset_vault() -> None:
    """Reset the global Vault instance (useful for testing)."""
    global _instance
    with _init_lock:
        _instance = None
