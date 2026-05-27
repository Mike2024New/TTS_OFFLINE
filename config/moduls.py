"""
В этом модуле централизованно подключаются движки
"""

INSTALL_DEPENDS = {'add_data': [], 'add_binary': [], 'excluded': []}  # добавление пакетов и бинарников для Pyinstaller
TTS_REGISTRY = {}  # классы движков
TTS_INFO = {}  # информация о движках и моделях
NORMALIZERS_REGISTRY = []  # нормализаторы текста
__all__ = ['TTS_REGISTRY', 'TTS_INFO', 'INSTALL_DEPENDS', 'NORMALIZERS_REGISTRY']


def add_piper(enabled: bool = False):
    # Подключение piper_engine
    if enabled:
        from app.tts.piper_engine.ttscore import TTSCore
        from app.tts.piper_engine.model_info import tts_info
        from pathlib import Path

        TTS_REGISTRY['piper'] = {
            'module': TTSCore,
            'models_list': [],
        }
        INSTALL_DEPENDS['add_data'].append(Path('piper') / 'espeak-ng-data')
        TTS_INFO['piper'] = tts_info.get_info()
        return
    # Если не подключен исключить библиотеки для этого проекта из зависимостей в PYINSTALLER
    INSTALL_DEPENDS['excluded'].append('onnxruntime')


def add_silero(enabled: bool = False):
    # подключение silero
    if enabled:
        from app.tts.silero_engine.ttscore import TTSCore
        from app.tts.silero_engine.model_info import tts_info

        TTS_REGISTRY['silero'] = {
            'module': TTSCore,
            'models_list': [],
        }
        TTS_INFO['silero'] = tts_info.get_info()
        return

    # Если не подключен исключить библиотеки для этого проекта из зависимостей в PYINSTALLER
    INSTALL_DEPENDS['excluded'].extend(['torch', 'torchvision', 'torchaudio', 'tensorflow'])


def add_normalizer(enabled: bool = False):
    if enabled:
        from pathlib import Path
        from app.text_normalizers.main import normalizer

        NORMALIZERS_REGISTRY.append(normalizer)
        INSTALL_DEPENDS['add_data'].append(Path('ru_normalizr') / 'dictionaries')
        return
    # Если не подключен исключить библиотеки для этого проекта из зависимостей в PYINSTALLER
    INSTALL_DEPENDS['excluded'].extend(['eng_to_ipa', 'nltk', 'spacy'])


# управление компонентами сборки.
# здесь можно определить какие движки попадут в сборку Pyinstaller, и будут запущены в приложении а какие нет
add_piper(enabled=True)
add_silero(enabled=True)
add_normalizer(enabled=True)
