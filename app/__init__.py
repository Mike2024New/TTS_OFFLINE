import sys
from pathlib import Path
from utils.message_bus_manager.message_bus_manager import MessageBus, Message
from utils.settings_manager import get_settings_manager
from config.schemas import settings, Settings

__all__ = [
    'settings_manager', 'Settings',
    'message_bus', 'Message', 'COMPONENT_NAME',
    # 'PIPER_MODELS_DIR', 'SILERO_MODELS_DIR',
    'JSON_LIBRARY_WORDS_PATH', 'MODELS_DIR',
]

COMPONENT_NAME = 'TTS'
SUBCOMPONENT_NAME = 'init'

# определение текущего метода исполнения (для exe, или из pycharm)
EXE_MODE = getattr(sys, 'frozen', False)

# поиск путей к папкам
JSON_SETTINGS_PATH = Path.cwd() / 'settings.json' if EXE_MODE else Path(__file__).parent.parent / 'settings.json'
JSON_LIBRARY_WORDS_PATH = Path.cwd() / 'library_words.json' if EXE_MODE else Path(
    __file__).parent.parent / 'library_words.json'

message_bus = MessageBus(print_message=False)  # шина сообщений
settings_manager = get_settings_manager(
    settings_model=settings,
    json_file_path=JSON_SETTINGS_PATH,
)  # менеджер настроек

# Пути к моделям речевым синтезаторам
MODELS_DIR = Path.cwd() / 'resources' / 'models' if EXE_MODE else Path(__file__).parent.parent / 'resources' / 'models'
# PIPER_MODELS_DIR = MODELS_DIR / 'piper_engine'
# SILERO_MODELS_DIR = MODELS_DIR / 'silero'
#
# # обязательно создать папки
# PIPER_MODELS_DIR.mkdir(exist_ok=True, parents=True)
# SILERO_MODELS_DIR.mkdir(exist_ok=True, parents=True)
