from app.text_normalizers.eng.eng import normalize as eng_normalize
from app.text_normalizers.ru.ru import normalize as ru_normalize
from app.text_normalizers.library_words_manager import library_words_get

__all__ = ['normalizer', 'get_current_language_by_model']
library_words = None


def get_current_language_by_model(model_name: str):
    if model_name.startswith('ru_') or model_name.endswith('_ru'):
        return 'ru'
    elif model_name.startswith('en_') or model_name.endswith('_en'):
        return 'en'
    return 'unknow'


def normalizer(model_name: str, text: str) -> str:
    """Автоматическое определение типа нормализатора моделей"""
    # присадка к тексту (так как нормализер не корректно воспроизводит числа если они без доп слов)
    model_name = model_name.lower()
    try:
        if get_current_language_by_model(model_name=model_name) == 'ru':
            current_library_words = library_words_get().get('ru', {})

            # ru_normalizer не очень корректно обрабатывает числа если они стоят в начале, например 3.14 сотых он
            # назовет как "три точка четырнадцать сотых", необходимо присадочное слово спереди, для этого и добавлен
            # префикс
            special_prefix = '~ нормализатор'
            is_prefix = False
            if text[0].isdigit():
                is_prefix = True
                text = special_prefix + text

            text = ru_normalize(text=text, library_words=current_library_words)

            if is_prefix:
                text = text[len(special_prefix) + 1:]

        elif get_current_language_by_model(model_name=model_name) == 'en':
            current_library_words = library_words_get().get('en', {})
            text = eng_normalize(text=text, library_words=current_library_words)
    except Exception:  # noqa
        pass

    return text


if __name__ == '__main__':
    txt = "3.14"
    res = normalizer(model_name='ru_RU-denis-medium', text=txt)
    print(res)
