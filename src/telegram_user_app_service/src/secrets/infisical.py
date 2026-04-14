"""Infisical secrets manager implementation."""

from logging import getLogger

from infisical_sdk import InfisicalSDKClient
from src.constants import INFISICAL_DEV_SECRET_NAME
from src.models.infisical import InfisicalSecretsKeys
from src.settings import settings
from src.settings.models.settings_model import InfiscalSettings
from src.utils.get_env_var import get_env_var
from src.utils.get_resource_url import get_resource_url

logger = getLogger(__name__)


class InfisicalSecretsManager:
    """Secrets manager implementation for Infisical. Retrieves secrets from the Infisical service."""

    def __init__(self, infisical_settings: InfiscalSettings):
        """Initialize the InfisicalSecretsManager with the provided settings."""
        logger.info("Initializing InfisicalSecretsManager with provided settings.")
        try:
            self._client = InfisicalSDKClient(host=get_resource_url(**settings.infisical.connection.model_dump()))
            logger.info("Infisical SDK client initialized successfully.")

            self._client.auth.universal_auth.login(
                client_id=infisical_settings.auth.client_id, client_secret=get_env_var(INFISICAL_DEV_SECRET_NAME)
            )
            logger.info("Authenticated with Infisical successfully.")
        except Exception as e:
            logger.error(f"Error initializing Infisical SDK client: {e}")
            raise

    def get_secret(self, secret_name: InfisicalSecretsKeys) -> str:
        """Retrieve the value of a secret by its name from Infisical."""
        try:
            secret = self._client.secrets.get_secret_by_name(
                secret_name,
                environment_slug=settings.infisical.project.env_slug,
                secret_path=settings.infisical.project.secret_path,
                project_id=settings.infisical.project.project_id,
            )
            return str(secret.secretValue)
        except Exception as e:
            logger.error(f"Error retrieving secret '{secret_name}': {e}")
            raise
