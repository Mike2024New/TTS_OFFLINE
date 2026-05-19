from pydantic import BaseModel

__all__ = ['settings', 'Settings']


class Settings(BaseModel):
    engine: str = 'silero'
    model: str = 'v5_5_ru'
    voice: str = 'xenia'
    max_silence_time: float = 0.5


# поле для импорта
settings = Settings()
