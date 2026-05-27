from ru_normalizr import Normalizer, NormalizeOptions
from app.text_normalizers.ru.extends import extension_pipeline

"""
Нормализация чисел, дат, английских слов в русский язык для TTS моделей. 
(Дело в том что silero например очень хорошие и качественные модели, но они к сожалению не распознают числа и 
английские буквы в тексте)
"""

__all__ = ['normalize']

normalizer = Normalizer(NormalizeOptions.tts(latinization_backend='ipa', ))


def normalize(text: str, library_words: dict[str, str] | None = None) -> str:
    library_words = library_words or {}
    # замена слов из словаря library_words, например "PC" -> "ПЭ КА"
    for term, pronunciation in library_words.items():
        text = text.replace(term, pronunciation)
    # подключаемые к нормализеру расширения extends
    text = extension_pipeline(text)
    # после всех обработок применение ru_normalizr
    return normalizer.normalize(text=text)
