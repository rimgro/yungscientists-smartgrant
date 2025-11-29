from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_name: str = "SmartGrant API"
    debug: bool = False

    db_url: str = Field(..., alias="DB_URL")
    secret_key: str = Field(..., alias="SECRET_KEY")
    access_token_expire_minutes: int = 30

    mir_api_key: str = Field(..., alias="MIR_API_KEY")
    mir_api_base_url: str = Field("https://api.mir-payments.example", alias="MIR_API_BASE_URL")
    payment_bank_api_base_url: str | None = Field(None, alias="PAYMENT_BANK_API_BASE_URL")
    app_bank_account_number: str = Field(..., alias="APP_BANK_ACCOUNT_NUMBER")


settings = Settings()
