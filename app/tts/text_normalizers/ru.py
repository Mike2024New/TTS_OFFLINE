from ru_normalizr import Normalizer, NormalizeOptions

"""
Нормализация чисел, дат, английских слов в русский язык для TTS моделей. 
(Дело в том что silero например очень хорошие и качественные модели, но они к сожалению не распознают числа и 
английские буквы в тексте)
"""

__all__ = ['normalize']

normalizer = Normalizer(NormalizeOptions.tts(latinization_backend='ipa', ))


def normalize(text: str, library_words: dict[str, str]):
    for term, pronunciation in library_words.items():
        text = text.replace(term, pronunciation)
    return normalizer.normalize(text=text)


if __name__ == '__main__':
    print(normalize(text='Я купил себе крутой PC, у него мощный CPU', library_words={'PC': 'ПК', 'CPU': 'си пи ю'}))
# print(normalize(text='Привет! Давай встретимся в 15:00'))
# print(normalize(text='Привет! Сегодня 16.05.2026'))
# print(normalize(text='Привет! Давай сходим в macdonalds'))
# print(normalize(text='I am live in Moscow'))
# print(normalize(text='У меня есть 3 яблока и 4 груши'))
# print(normalize(text='Тебе письмо от ГБУ Жилищник'))
# print(normalize(text='Я запустился на CPU'))
