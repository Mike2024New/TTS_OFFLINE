import warnings
from app.tts.silero_engine import SILERO_MODELS_DIR
from app import message_bus, Message, COMPONENT_NAME
import torch
import json
import re

SUBCOMPONENT = 'STTInfo'
# отключение предупреждений pytorch при загрузке silero (там есть свои внутренние ошибки, типа лишних `\` в регулярках
warnings.filterwarnings('ignore', category=SyntaxWarning)
warnings.filterwarnings('ignore', category=FutureWarning)
warnings.filterwarnings("ignore", category=UserWarning)

__all__ = ['tts_info']


class TTSInfo:
    def __init__(self):
        self.update_models_list()  # проверка списка моделей

    @staticmethod
    def get_info() -> dict[str, list[str]]:
        if not (SILERO_MODELS_DIR / 'info.json').exists():
            return {}

        with open(file=(SILERO_MODELS_DIR / 'info.json'), mode='r', encoding='utf8') as f:
            data = json.loads(f.read())
            return data

    @staticmethod
    def _identify_lang(model_name: str) -> tuple[str, str | None]:
        lang = None
        m_name = model_name.replace('.pt', '')
        res = re.search(pattern=r'\_(\S\S\_\S\S)$', string=m_name)
        if res is not None:
            lang = res.group(1)
            return model_name, lang
        res = re.search(pattern=r'\_(\S\S)$', string=m_name)
        if res is not None:
            lang = res.group(1)
            m_name = f"{m_name}_{lang.upper()}.pt"
            return m_name, f"{lang}_{lang.upper()}"
        return f"{model_name}", lang

    def update_models_list(self):
        models_list_from_json = self.get_info()
        models_list_actual = []
        for mod in SILERO_MODELS_DIR.iterdir():
            if mod.name.endswith('.pt'):
                model_name = mod.name
                file_name, lang = self._identify_lang(model_name)
                models_list_actual.append({'model': file_name, 'lang': lang})
                # переименовать файлы с учётом ISO стандарта языка (если язык известен)
                if mod.name != file_name:
                    mod.rename(mod.parent / file_name)

        # обновить список моделей только если появились новые файлы
        if not [key['model'] for key in models_list_actual] == list(models_list_from_json.keys()):
            message_bus.add(
                Message(
                    component=COMPONENT_NAME,
                    subcomponent=SUBCOMPONENT,
                    level='info',
                    message='Обновление списка моделей `silero` это может занять некоторое время',
                )
            )

            models_info = {}
            for model_dict in models_list_actual:
                model_path = SILERO_MODELS_DIR / model_dict['model']
                model = torch.package.PackageImporter(str(model_path)).load_pickle("tts_models", "model")
                voices = model.speakers if model.speakers else []
                models_info[model_dict['model']] = {'voices': voices, 'lang': model_dict['lang']}

            with open(file=(SILERO_MODELS_DIR / 'info.json'), mode='w', encoding='utf8') as f:
                f.write(json.dumps(models_info, ensure_ascii=False, indent=2))


tts_info = TTSInfo()

if __name__ == '__main__':
    # stt_info.update_models_list()
    print(tts_info.get_info())
