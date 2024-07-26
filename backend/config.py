from dataclasses import dataclass
import os
from dotenv import load_dotenv


load_dotenv()


@dataclass
class Settings:
    DATABASE_PORT: int
    POSTGRES_PASSWORD: str
    POSTGRES_USER: str
    POSTGRES_DB: str
    POSTGRES_HOST: str

    SECRET_KEY: str

    ACCESS_TOKEN_EXPIRES_IN: int
    JWT_ALGORITHM: str


settings = Settings(
    **{k: os.environ.get(k) for k in Settings.__annotations__.keys()}
)
