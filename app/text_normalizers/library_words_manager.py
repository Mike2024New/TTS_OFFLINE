import json
from app import JSON_LIBRARY_WORDS_PATH

__all__ = ['library_words_get', 'library_words_reset', 'library_words_update']


def library_words_update(add_normalize_dict: dict[str, str], lang: str):
    """Обновление словаря"""
    with open(file=JSON_LIBRARY_WORDS_PATH, mode='r', encoding='utf8') as f:
        data = json.loads(f.read())

    data_lang = data.get(lang, {})

    for key, val in add_normalize_dict.items():
        data_lang[key] = val

    data[lang] = data_lang

    with open(file=JSON_LIBRARY_WORDS_PATH, mode='w', encoding='utf8') as f:
        f.write(json.dumps(data, ensure_ascii=False, indent=2))


def library_words_reset():
    with open(file=JSON_LIBRARY_WORDS_PATH, mode='w', encoding='utf8') as f:
        f.write(json.dumps({}, ensure_ascii=False, indent=2))


def library_words_get():
    if not JSON_LIBRARY_WORDS_PATH.exists():
        library_words_reset()

    # прочитать пользовательскую библиотеку слов
    try:
        with open(file=JSON_LIBRARY_WORDS_PATH, mode='r', encoding='utf8') as f:
            library_words = json.loads(f.read())
    except Exception:  # noqa
        library_words = {}
    return library_words


if __name__ == '__main__':
    library_words_update(add_normalize_dict={'country': 'кантри'}, lang='ru_RU')
