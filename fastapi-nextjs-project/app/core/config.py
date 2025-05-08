import os
from typing import List, Union, Optional, Dict
from pydantic import AnyHttpUrl, validator
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "MCP Server"

    # CORS settings
    BACKEND_CORS_ORIGINS: List[AnyHttpUrl] = []

    @validator("BACKEND_CORS_ORIGINS", pre=True)
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> Union[List[str], str]:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)

    # Database settings
    DATABASE_URL: str = os.getenv("DATABASE_URL", "postgresql+asyncpg://postgres:postgres@localhost/postgres")

    # AI settings
    ENABLE_AI_FEATURES: bool = os.getenv("ENABLE_AI_FEATURES", "").lower() in ("true", "1", "t", "yes")

    # AI model selection
    AI_MODEL_TYPE: str = os.getenv("AI_MODEL_TYPE", "jellyfish")  # Options: jellyfish, xlnet, t5, bert

    # Model paths for different model types
    AI_MODEL_PATHS: Dict[str, str] = {
        "jellyfish": "NECOUDBFM/Jellyfish-13B",
        "xlnet": "xlnet-base-cased",
        "t5": "t5-base",
        "bert": "bert-base-uncased"
    }

    # Override default model paths with environment variables if provided
    AI_JELLYFISH_PATH: str = os.getenv("AI_JELLYFISH_PATH", AI_MODEL_PATHS["jellyfish"])
    AI_XLNET_PATH: str = os.getenv("AI_XLNET_PATH", AI_MODEL_PATHS["xlnet"])
    AI_T5_PATH: str = os.getenv("AI_T5_PATH", AI_MODEL_PATHS["t5"])
    AI_BERT_PATH: str = os.getenv("AI_BERT_PATH", AI_MODEL_PATHS["bert"])

    # Update model paths with environment variables
    AI_MODEL_PATHS: Dict[str, str] = {
        "jellyfish": AI_JELLYFISH_PATH,
        "xlnet": AI_XLNET_PATH,
        "t5": AI_T5_PATH,
        "bert": AI_BERT_PATH
    }

    # Hardware settings
    AI_MODEL_DEVICE: str = os.getenv("AI_MODEL_DEVICE", "cuda" if os.getenv("CUDA_VISIBLE_DEVICES") else "cpu")
    AI_MODEL_QUANTIZATION: Optional[str] = os.getenv("AI_MODEL_QUANTIZATION", "4bit")  # 4bit, 8bit, or None

    # Model-specific settings
    AI_MAX_LENGTH: int = int(os.getenv("AI_MAX_LENGTH", "1024"))
    AI_TEMPERATURE: float = float(os.getenv("AI_TEMPERATURE", "0.1"))
    AI_TOP_P: float = float(os.getenv("AI_TOP_P", "0.95"))

    # Timeout settings
    DEFAULT_PROCESS_TIMEOUT: int = int(os.getenv("DEFAULT_PROCESS_TIMEOUT", "300"))  # 5 minutes

    # File upload settings
    UPLOAD_DIR: str = os.getenv("UPLOAD_DIR", os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "uploads"))
    MAX_UPLOAD_SIZE: int = int(os.getenv("MAX_UPLOAD_SIZE", "104857600"))  # 100 MB

    class Config:
        case_sensitive = True
        env_file = ".env"

settings = Settings()
