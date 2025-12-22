from pathlib import Path

from pydantic import SecretStr, Field
from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parent.parent


class ConfigBase(BaseSettings):
    model_config = SettingsConfigDict(env_file=f'{BASE_DIR}/.env', env_file_encoding='utf-8', extra='ignore',
                                      case_sensitive=False)


class CloudflareSettings(ConfigBase):
    model_config = SettingsConfigDict(env_prefix='CLOUDFLARE_')
    API_KEY: SecretStr
    ACCOUNT_ID: str
    MODEL_NAME: str = '@cf/meta/llama-4-scout-17b-16e-instruct'
    MODEL_TEMPERATURE: float = 1.2
    REQUEST_TIMEOUT_SECONDS: int = 10


class Settings(ConfigBase):
    CLOUDFLARE: CloudflareSettings = Field(default_factory=CloudflareSettings)
    SERVER_HOST: str = '127.0.0.1'
    SERVER_PORT: int = 8000
    AUDIO_CHUNK_SIZE: int = 1024
    STREAM_ITERATIONS: int = 5
    TORCH_DEVICE: str = 'cpu'
    SILERO_SPEAKER: str = 'eugene'

    def get_resource_url(self, file_name: str) -> str:
        return f'http://{self.SERVER_HOST}:{self.SERVER_PORT}/static/{file_name}'


SETTINGS = Settings()
