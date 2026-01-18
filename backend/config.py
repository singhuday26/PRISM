from functools import lru_cache
from pydantic import Field, field_validator, ValidationError
from pydantic_settings import BaseSettings, SettingsConfigDict
import sys


class Settings(BaseSettings):
    mongo_uri: str = Field(..., env="MONGO_URI", description="MongoDB connection URI")
    db_name: str = Field("prism_db", env="DB_NAME")
    api_host: str = Field("0.0.0.0", env="API_HOST")
    api_port: int = Field(8000, env="API_PORT", ge=1, le=65535)
    log_level: str = Field("INFO", env="LOG_LEVEL")
    risk_high_threshold: float = Field(0.7, env="RISK_HIGH_THRESHOLD", ge=0.0, le=1.0)
    
    # Additional robustness settings
    mongo_connect_timeout_ms: int = Field(5000, env="MONGO_CONNECT_TIMEOUT_MS", ge=1000)
    mongo_server_selection_timeout_ms: int = Field(5000, env="MONGO_SERVER_SELECTION_TIMEOUT_MS", ge=1000)
    enable_cors: bool = Field(True, env="ENABLE_CORS")
    cors_origins: str = Field("*", env="CORS_ORIGINS", description="Comma-separated list of allowed origins")

    model_config = SettingsConfigDict(env_file=".env", case_sensitive=False, extra="ignore")

    @field_validator("log_level")
    @classmethod
    def validate_log_level(cls, v: str) -> str:
        valid_levels = {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}
        v_upper = v.upper()
        if v_upper not in valid_levels:
            raise ValueError(f"log_level must be one of {valid_levels}")
        return v_upper

    def get_cors_origins_list(self) -> list[str]:
        """Parse CORS origins from comma-separated string."""
        if self.cors_origins == "*":
            return ["*"]
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]


@lru_cache()
def get_settings() -> Settings:
    try:
        return Settings()
    except ValidationError as e:
        print("\n❌ Configuration Error:")
        for error in e.errors():
            field = error.get("loc", [""])[0]
            msg = error.get("msg", "")
            if field == "mongo_uri":
                print(f"  - MONGO_URI is required. Please set it in your .env file or environment variables.")
            else:
                print(f"  - {field}: {msg}")
        print("\nPlease check your .env file or environment variables.\n")
        sys.exit(1)
