import os
import secrets

from fastapi import HTTPException, Security, status
from fastapi.security import APIKeyHeader


API_KEY_ENV_VAR = "PARKING_API_KEYS"
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)


def _get_configured_api_keys() -> tuple[str, ...]:
    raw_keys = os.getenv(API_KEY_ENV_VAR, "")
    return tuple(key.strip() for key in raw_keys.split(",") if key.strip())


def require_api_key(api_key: str | None = Security(api_key_header)) -> str:
    configured_keys = _get_configured_api_keys()
    if not configured_keys:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"API keys are not configured. Set {API_KEY_ENV_VAR}.",
        )

    if api_key is None or not any(
        secrets.compare_digest(api_key, configured_key)
        for configured_key in configured_keys
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing or invalid API key",
        )

    return api_key
