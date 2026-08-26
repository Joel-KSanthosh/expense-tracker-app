import logging
import os

import httpx
from httpx._models import Response

LOGGER = logging.getLogger(__name__)

BASE_URL: str = os.getenv("INFISICAL_BASE_URL", "")
CLIENT_ID: str = os.getenv("INFISICAL_CLIENT_ID", "")
CLIENT_SECRET: str = os.getenv("INFISICAL_CLIENT_SECRET", "")
PROJECT_ID: str = os.getenv("INFISICAL_PROJECT_ID", "")
ENVIRONMENT: str = os.getenv("INFISICAL_ENVIRONMENT", "")
SECRET_PATH: str = os.getenv("INFISICAL_SECRET_PATH", "")


class InfisicalSecretManager:
    def __init__(
        self,
        base_url: str = BASE_URL,
        client_id: str = CLIENT_ID,
        client_secret: str = CLIENT_SECRET,
        project_id: str = PROJECT_ID,
        env: str = ENVIRONMENT,
        secret_path: str = SECRET_PATH,
    ) -> None:
        self._auth_url: str = f"{base_url}/api/v1/auth/universal-auth/login"
        self._secret_url: str = f"{base_url}/api/v4/secrets"
        self._client_id: str = client_id
        self._client_secret: str = client_secret
        self._environment: str = env
        self._project_id: str = project_id
        self._env: str = env
        self._secret_path: str = secret_path

        self._timeout_config: httpx.Timeout = httpx.Timeout(
            timeout=10.0,
            connect=3.0,
            read=15.0,
        )

        missing: list[str] = [
            name
            for name, value in (
                ("INFISICAL_BASE_URL", base_url),
                ("INFISICAL_CLIENT_ID", client_id),
                ("INFISICAL_CLIENT_SECRET", client_secret),
                ("INFISICAL_PROJECT_ID", project_id),
                ("INFISICAL_ENVIRONMENT", env),
            )
            if not value
        ]

        if missing:
            raise ValueError(f"Missing Infisical configuration: {', '.join(missing)}")

    async def _authenticate(self) -> str:
        payload: dict[str, str] = {
            "clientId": self._client_id,
            "clientSecret": self._client_secret,
        }

        try:
            async with httpx.AsyncClient(timeout=self._timeout_config) as client:
                response: httpx.Response = await client.post(
                    url=self._auth_url,
                    json=payload,
                )
                response.raise_for_status()
                raw_data: dict = response.json()
        except httpx.HTTPStatusError as exc:
            raise RuntimeError(f"Infisical authentication rejected with status {exc.response.status_code}") from exc
        except httpx.RequestError as exc:
            raise RuntimeError(f"Could not reach Infisical: {exc!r}") from exc
        except ValueError as exc:
            raise RuntimeError(f"Infisical returned a malformed response: {exc}") from exc

        access_token: str = raw_data.get("accessToken", "")
        if not access_token:
            raise RuntimeError("Infisical response did not contain an accessToken")

        LOGGER.info(msg="Authenticated with Infisical.")
        return access_token

    async def get_secret(self, secret_name: str) -> str:
        token: str = await self._authenticate()
        headers: dict[str, str] = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        }

        params: dict[str, str] = {
            "projectId": self._project_id,
            "environment": self._environment,
            "secretPath": self._secret_path,
            "type": "shared",
            "viewSecretValue": "true",
        }

        url: str = f"{self._secret_url}/{secret_name}"
        try:
            async with httpx.AsyncClient(timeout=self._timeout_config) as client:
                response: Response = await client.get(
                    url,
                    headers=headers,
                    params=params,
                )
                response.raise_for_status()
                data: dict[str, dict[str, str]] = response.json()

        except httpx.HTTPStatusError as exc:
            raise RuntimeError(f"Infisical secret fetch rejected with status {exc.response.status_code}") from exc
        except httpx.RequestError as exc:
            raise RuntimeError(f"Could not reach Infisical: {exc!r}") from exc
        except ValueError as exc:
            raise RuntimeError(f"Infisical returned a malformed response: {exc}") from exc

        LOGGER.info("Secret fetched successfully.")
        return data.get("secret", {}).get("secretValue", "")
