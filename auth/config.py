import os


class Settings:
    ACCESS_TOKEN_EXPIRE_MINUTES = 30
    SECRET_KEY: str = str(os.getenv("SECRET_KEY"))
    ALGORITHM = "HS256"

settings = Settings()