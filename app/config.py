from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache

class Settings(BaseSettings):
    app_name: str = "Beyond Jersey AI Assistant"
    debug: bool = True

    ollama_model: str = "qwen3:4b"
    ollama_base_url: str = "http://localhost:11434"
    ollama_timeout_seconds: float = 90.0
    ollama_num_ctx: int = 1024
    allow_llm_fallback: bool = True

    supabase_url: str = "https://tdtcbbegqipymobgzeqi.supabase.co"
    supabase_anon_key: str = ""
    database_url: str = "sqlite:///./beyondjersey.db"

    payment_bca_bank: str = "Bank BCA"
    payment_bca_account_name: str = "Malva Nurina Tyagita"
    payment_bca_number: str = "5790318864"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

@lru_cache()
def get_settings() -> Settings:
    return Settings()
