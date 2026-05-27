from app.text_normalizers.eng.main import normalize as eng_normalize
from app.text_normalizers.ru.main import normalize as ru_normalize
from app.text_normalizers.library_words_manager import library_words_get

__all__ = ['normalizer']


def normalizer(lang: str, text: str) -> str:
    """
    lang : выбор языка нормализатора (если нет такого то просто вернёт оригинальный не нормализованный текст)
    text : оригинальный текст
    Если произойдет ошибка, то вернется просто оригинальный текст
    """
    try:
        if lang == 'ru_RU':
            current_library_words = library_words_get().get('ru_RU', {})

            # ru_normalizer не очень корректно обрабатывает числа если они стоят в начале, например 3.14 сотых он
            # назовет как "три точка четырнадцать сотых", необходимо присадочное слово спереди, для этого и добавлен
            # префикс
            special_prefix = '~ нормализатор '
            is_prefix = False
            if text[0].isdigit():
                is_prefix = True
                text = special_prefix + text

            text = ru_normalize(text=text, library_words=current_library_words)

            if is_prefix:
                text = text[len(special_prefix):]

        elif lang == 'en_EN':
            current_library_words = library_words_get().get('en_EN', {})
            text = eng_normalize(text=text, library_words=current_library_words)
    except Exception:  # noqa
        pass

    return text


if __name__ == '__main__':
    txt = "3.12.4"
    res = normalizer(lang='ru_RU', text=txt)
    print(res)
