import yaml
from pydantic import BaseModel
from typing import List
from pathlib import Path


class AppSettings(BaseModel):
    title: str
    description: str
    version: str
    host: str
    port: int


class ApiEndpoints(BaseModel):
    root: str
    truth: str
    health: str


class ApiConfig(BaseModel):
    endpoints: ApiEndpoints


class FileSettings(BaseModel):
    truth_file_path: str


class RateLimitSettings(BaseModel):
    max_requests: int
    window_seconds: int


class CorsSettings(BaseModel):
    allow_origins: List[str]
    allow_credentials: bool
    allow_methods: List[str]
    allow_headers: List[str]


class LoggingSettings(BaseModel):
    level: str


class Settings(BaseModel):
    app: AppSettings
    api: ApiConfig
    files: FileSettings
    rate_limit: RateLimitSettings
    cors: CorsSettings
    logging: LoggingSettings


def load_settings(config_path: str = "settings.yaml") -> Settings:
    """
    Load settings from YAML file
    """
    with open(config_path, 'r', encoding='utf-8') as file:
        config_data = yaml.safe_load(file)
    
    return Settings(**config_data)


# Global settings instance
settings = load_settings()
