import warnings
from app import SILERO_MODELS_DIR, message_bus, Message, COMPONENT_NAME
import torch
import json

SUBCOMPONENT = 'STTInfo'
# отключение предупреждений pytorch при загрузке silero (там есть свои внутренние ошибки, типа лишних `\` в регулярках
warnings.filterwarnings('ignore', category=SyntaxWarning)
warnings.filterwarnings('ignore', category=FutureWarning)
warnings.filterwarnings("ignore", category=UserWarning)

__all__ = ['stt_info']


class STTInfo:
    def __init__(self):
        self.update_models_list()  # проверка списка моделей

    @staticmethod
    def get_info() -> dict[str, list[str]]:
        if not (SILERO_MODELS_DIR / 'info.json').exists():
            return {}

        with open(file=(SILERO_MODELS_DIR / 'info.json'), mode='r', encoding='utf8') as f:
            data = json.loads(f.read())
            return data

    def update_models_list(self):
        models_list_from_json = self.get_info()
        models_list_actual = [mod.parts[-1].replace('.pt', '') for mod in SILERO_MODELS_DIR.iterdir()
                              if mod.name.endswith('.pt')]

        if not models_list_actual == list(models_list_from_json.keys()):
            models_info = {}
            message_bus.add(
                Message(
                    component=COMPONENT_NAME,
                    subcomponent=SUBCOMPONENT,
                    level='info',
                    message='Обновление списка моделей `silero` это может занять некоторое время',
                )
            )
            for model_name in models_list_actual:
                model_path = SILERO_MODELS_DIR / f"{model_name}.pt"
                model = torch.package.PackageImporter(str(model_path)).load_pickle("tts_models", "model")
                models_info[model_name] = model.speakers
            with open(file=(SILERO_MODELS_DIR / 'info.json'), mode='w', encoding='utf8') as f:
                f.write(json.dumps(models_info, ensure_ascii=False, indent=2))

    def get_default_parameters(self) -> dict[str, str]:
        try:
            data = self.get_info()
            first_model = list(data.keys())[0]
            first_voice = data.get(first_model)[0]
            default_parameters = {'model': first_model, 'voice': first_voice}
            return default_parameters
        except Exception as err:
            message_bus.add(
                Message(
                    component=COMPONENT_NAME,
                    subcomponent=SUBCOMPONENT,
                    level='error',
                    message=f'Не удалось прочитать настройки по умолчанию. Причина: {err}'
                )
            )
            return {}


stt_info = STTInfo()

if __name__ == '__main__':
    # stt_info.update_models_list()
    # res = stt_info.get_info()
    # print(res)
    print(stt_info.get_default_parameters())
