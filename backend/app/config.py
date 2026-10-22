import os
from pathlib import Path
from pydantic_settings import BaseSettings

BASE_DIR = Path(__file__).resolve().parent.parent

class Settings(BaseSettings):
    PROJECT_NAME: str = "CitiusTech AI Content Intelligence & SEO Agent Platform"
    API_V1_STR: str = "/api/v1"
    DEBUG: bool = True
    
    # Storage
    DATA_DIR: Path = BASE_DIR / "data"
    DATABASE_URL: str = f"sqlite+aiosqlite:///{BASE_DIR / 'data' / 'citiustech_platform.db'}"
    
    # LLM Settings
    LLM_PROVIDER: str = os.getenv("LLM_PROVIDER", "hybrid") # hybrid, gemini, openai, anthropic, mock
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    ANTHROPIC_API_KEY: str = os.getenv("ANTHROPIC_API_KEY", "")
    
    # Search & Crawling
    MAX_SEARCH_RESULTS: int = 6
    REQUEST_TIMEOUT: int = 15
    USER_AGENT: str = "CitiusTechResearchBot/1.0 (+https://citiustech.com/ethical-bot)"
    
    # Quality & Revisions
    MAX_REVISION_CYCLES: int = 3
    MIN_QUALITY_SCORE_APPROVAL: float = 85.0
    
    class Config:
        env_file = ".env"
        extra = "ignore"

settings = Settings()
settings.DATA_DIR.mkdir(parents=True, exist_ok=True)
(settings.DATA_DIR / "citiustech_seed").mkdir(parents=True, exist_ok=True)
