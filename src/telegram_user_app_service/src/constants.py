"""Constants for the Telegram User App Service microservice."""

BASE_SETTINGS_PATH = "src/settings"
SETTINGS_PATH = f"{BASE_SETTINGS_PATH}/settings.toml"
FASTAPI_SETTINGS_PATH = f"{BASE_SETTINGS_PATH}/fastapi_settings.toml"
MQ_WORKER_SETTINGS_PATH = f"{BASE_SETTINGS_PATH}/mq_worker_settings.toml"

SERVICE_CLIENT_SESSION_TIMEOUT = 30

SUBSCRIPTION_TOKEN_EXPIRATION_SECONDS = 60 * 60 * 24
