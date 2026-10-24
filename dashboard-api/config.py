from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    DISCORD_CLIENT_ID: str
    DISCORD_CLIENT_SECRET: str
    DISCORD_REDIRECT_URI: str
    JWT_SECRET: str
    MONGODB_URI: str
    API_SECRET: str = ""
    CORS_ORIGINS: str = "http://localhost:3000"
    FRONTEND_URL: str = "http://localhost:3000"
    LAVALINK_PUBLIC_LABEL: str = "Lavalink"
    LAVALINK_PUBLIC_HOST: str = "localhost"
    LAVALINK_PUBLIC_PORT: int = 2333

    @property
    def cors_list(self) -> list[str]:
        return [o.strip() for o in self.CORS_ORIGINS.split(",") if o.strip()]


settings = Settings()  # type: ignore[call-arg]
