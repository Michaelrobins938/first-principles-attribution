import os
from pydantic import BaseModel
from typing import Optional


class Settings(BaseModel):
    app_name: str = "Attribution Mind Map API"
    debug: bool = False
    host: str = "0.0.0.0"
    port: int = 8000
    data_dir: str = "Data/attribution_input"
    cors_origins: list[str] = ["http://localhost:3000", "http://localhost:5173"]
    
    @classmethod
    def from_env(cls):
        return cls(
            debug=os.getenv("DEBUG", "false").lower() == "true",
            host=os.getenv("HOST", "0.0.0.0"),
            port=int(os.getenv("PORT", "8000")),
        )


settings = Settings.from_env()
