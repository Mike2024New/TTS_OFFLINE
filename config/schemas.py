from pydantic import BaseModel

__all__ = ['settings', 'Settings']


class Settings(BaseModel):
    pass


# поле для импорта
settings = Settings()
