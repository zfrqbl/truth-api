from pydantic import BaseModel
from typing import Dict, List


class AppConfig(BaseModel):
    name: str
    environment: str
    timezone_mode: str


class ApiConfig(BaseModel):
    endpoints: Dict[str, str]
    content_negotiation: Dict[str, str]


class TruthsConfig(BaseModel):
    source_file: str
    validation: Dict[str, int | List[str] | bool]
    normalization: Dict[str, str]


class SelectionConfig(BaseModel):
    random_mode: str
    weight_levels: Dict[str, int]
    day_weight_table: Dict[str, Dict[str, float]]


class RateLimitConfig(BaseModel):
    requests_per_period: int
    period_seconds: int
    key_strategy: str
    exempt_routes: List[str]


class HeadersConfig(BaseModel):
    cache_control: str
    vary: str
    security: Dict[str, str]


class ErrorsConfig(BaseModel):
    field_names: Dict[str, str]
    status_mappings: Dict[str, int]


class ObservabilityConfig(BaseModel):
    logging: Dict[str, str | List[str]]


class Settings(BaseModel):
    app: AppConfig
    api: ApiConfig
    truths: TruthsConfig
    selection: SelectionConfig
    rate_limit: RateLimitConfig
    headers: HeadersConfig
    errors: ErrorsConfig
    observability: ObservabilityConfig
