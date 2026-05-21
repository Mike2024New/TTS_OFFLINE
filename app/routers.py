from app.main import app as component
from fastapi import APIRouter, HTTPException
from app.tts import get_info

router = APIRouter(
    prefix='/tts',
    tags=['tts'],
)


@router.get(
    '/info/',
    summary='Общая информация о доступных движках, их моделях и голосах если есть.'
)
def test():
    return {'info': get_info()}


@router.get(
    '/say/',
    summary="""
    Произнести переданную на вход фразу. Доступные голоса см. в /tts/info/
    """
)
def say(text: str, voice: str | None = None):
    try:
        component.say(text, voice)
        return {'msg': f'Идет озвучка текста'}
    except Exception as err:
        raise HTTPException(status_code=400, detail=f'Ошибка распознавания речи {err}')


@router.get(
    '/interrupt/',
    summary="""Прерывание текущей речи модели если она сейчас говорит"""
)
def interrupt():
    try:
        component.interrupt()
        return {'msg': f'Прерывание текста'}
    except Exception as err:
        raise HTTPException(status_code=400, detail=f'Ошибка прерывателя речи {err}')


from app.text_normalizers.library_words_manager import library_words_get, library_words_reset, library_words_update


@router.get(
    '/is_silent/',
    summary="Проверка тишина ли сейчас"
)
def is_silent():
    return {'is_silent': component.is_silent()}


@router.get(
    '/normalize-list/',
    summary="""Просмотр кастомного словаря слов нормализации для произношения моделью"""
)
def normalize_list():
    return library_words_get()


@router.put(
    '/normalize-list-update/',
    summary="Добавить новые слова нормализации для речевой модели"
)
def normalize_list_update(new_normalize_dict: dict[str, str], lang: str):
    library_words_update(add_normalize_dict=new_normalize_dict, lang=lang)


@router.delete(
    '/normalize-list-reset/',
    summary="""Сбросить словарь кастомных слов нормализации"""
)
def normalize_list_reset():
    return library_words_reset()
