from pydantic import BaseModel

__all__ = ['settings', 'Settings']


class Settings(BaseModel):
    engine: str = 'piper'
    model: str = 'ru_RU-dmitri-medium'
    voice: str = 'ru_RU-dmitri-medium'
    max_silence_time: float = 0.5


# поле для импорта
settings = Settings()
