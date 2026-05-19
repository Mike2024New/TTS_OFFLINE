import numpy as np
from typing import Protocol, Generator

__all__ = ['TTSEngine', ]


class TTSEngine(Protocol):
    """
    Единый стандарт для классов TTS:
      Переменные:
        SAMPLERATE - частота дискретизации для конкретнного движка, например piper 22050, silero 48000
      Методы:
        init - сделать облегченным (без тяжелых подгрузок модели)
        start - запуск всех движков (загрузка моделей)
        generate_speech_pcm - генерация аудио массива входных данных
        stop - остановка всех движков
    """
    SAMPLERATE: int
    model_name: str

    def start(self, model_name: str, voice: str) -> bool: ...

    def stop(self) -> bool: ...

    def generate_speech_pcm(self, text: str, voice: str | None = None) -> Generator[np.ndarray, None, None]: ...
