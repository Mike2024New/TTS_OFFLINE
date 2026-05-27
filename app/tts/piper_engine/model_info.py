import re
from app.tts.piper_engine import PIPER_MODELS_DIR
from app import message_bus, Message, COMPONENT_NAME
import json

SUBCOMPONENT = 'STTInfo'
__all__ = ['tts_info']


class TTSInfo:
    def __init__(self):
        self.update_models_list()  # проверка списка моделей

    @staticmethod
    def get_info() -> dict[str, list[str]]:
        if not (PIPER_MODELS_DIR / 'info.json').exists():
            return {}

        with open(file=(PIPER_MODELS_DIR / 'info.json'), mode='r', encoding='utf8') as f:
            data = json.loads(f.read())
            return data

    def update_models_list(self):
        models_list_from_json = self.get_info()
        models_list_actual = [mod.parts[-1] for mod in PIPER_MODELS_DIR.iterdir() if
                              mod.name.endswith('.onnx')]

        if not models_list_actual == list(models_list_from_json.keys()):
            models_info = {}
            message_bus.add(
                Message(
                    component=COMPONENT_NAME,
                    subcomponent=SUBCOMPONENT,
                    level='info',
                    message='Обновление списка моделей `piper` это может занять некоторое время',
                )
            )

            for model_name in models_list_actual:
                lang = re.search(pattern=r'^(\S\S\_\S\S)\-', string=model_name)
                lang = lang.group(1) if lang is not None else None
                models_info[model_name] = {'voices': [model_name], 'lang': lang}

            with open(file=(PIPER_MODELS_DIR / 'info.json'), mode='w', encoding='utf8') as f:
                f.write(json.dumps(models_info, ensure_ascii=False, indent=2))


tts_info = TTSInfo()

if __name__ == '__main__':
    # stt_info.update_models_list()
    print(tts_info.get_info())
