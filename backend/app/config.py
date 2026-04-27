from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    """Application settings"""

    # Application
    APP_NAME: str = "Traffic Congestion Analysis"
    DEBUG: bool = True
    API_V1_PREFIX: str = "/api/v1"

    # Database
    DATABASE_URL: str
    DB_HOST: str = "localhost"
    DB_PORT: int = 5432
    DB_NAME: str = "traffic_db"
    DB_USER: str = "postgres"
    DB_PASSWORD: str = "password"

    # JWT
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # CORS
    ALLOWED_ORIGINS: str = "http://localhost:3000"

    @property
    def cors_origins(self) -> List[str]:
        return [origin.strip() for origin in self.ALLOWED_ORIGINS.split(",")]

    # ML Model
    MODEL_PATH: str = "../data/models/yolov8n.pt"
    CONFIDENCE_THRESHOLD: float = 0.5
    NMS_THRESHOLD: float = 0.4

    # Traffic Classification
    DENSITY_LOW: int = 10
    DENSITY_MEDIUM: int = 25
    DENSITY_HIGH: int = 40
    SPEED_THRESHOLD_FREE: float = 50.0
    SPEED_THRESHOLD_MODERATE: float = 30.0

    # Video Processing
    FRAME_SKIP: int = 5
    VIDEO_UPLOAD_PATH: str = "../data/videos"

    # File Upload
    MAX_UPLOAD_SIZE_MB: int = 100

    # Google Maps (optional)
    GOOGLE_MAPS_API_KEY: str = ""

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
