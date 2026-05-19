import torch
from app import SILERO_MODELS_DIR, COMPONENT_NAME, message_bus, Message
import numpy as np
from typing import Generator
from app.tts.tts_engine_protocol import TTSEngine
import warnings
from app.tts.silero.model_info import stt_info

# отключение предупреждений pytorch при загрузке silero (там есть свои внутренние ошибки, типа лишних `\` в регулярках
warnings.filterwarnings('ignore', category=SyntaxWarning)
warnings.filterwarnings('ignore', category=FutureWarning)
warnings.filterwarnings("ignore", category=UserWarning)

__all__ = ['TTSCore', ]

CHUNK_SIZE = 1024
SUBCOMPONENT = 'silero'


class TTSCore(TTSEngine):
    SAMPLERATE = 48000

    def __init__(self):
        self._model = None
        default_parameters = stt_info.get_default_parameters()
        self.model_name = default_parameters.get('model')
        self.voice = default_parameters.get('voice')

    def start(self, model_name: str | None = None, voice: str | None = None):
        self.voice = voice if voice is not None else self.voice
        self.model_name = model_name if model_name is not None else self.model_name
        device = torch.device('cpu')
        model_path = SILERO_MODELS_DIR / f"{self.model_name}.pt"
        self._model = torch.package.PackageImporter(str(model_path)).load_pickle("tts_models", "model")

        self._model.to(device)
        message_bus.add(
            Message(
                component=COMPONENT_NAME,
                subcomponent=SUBCOMPONENT,
                level='info',
                message=f'Компонент `{SUBCOMPONENT}` запущен.',
                data={'model': {self.model_name}},
            )
        )
        self._check_exists_voice()  # проверка что голос существует

    def stop(self):
        # выгрузка модели
        if self._model:
            self._model = None
        message_bus.add(
            Message(
                component=COMPONENT_NAME,
                subcomponent=SUBCOMPONENT,
                level='info',
                message=f'Компонент `{SUBCOMPONENT}` остановлен.'
            )
        )

    def _check_exists_voice(self):
        if self.voice not in self._model.speakers:
            raise RuntimeError(
                f'Голос voice=`{self.voice}` для engine=`silero`, model=`{self.model_name}`  не найден. Доступны голоса: `{self._model.speakers}`')

    def generate_speech_pcm(self, text: str, voice: str | None = None) -> Generator[np.ndarray, None, None]:
        """
        Выдача генератора pcm массива из сгенерированных текстовых данных, например фраза "Привет! как дела?":
        [-9 -2  0 ... 30 39 41]
        [-3 -3  5 ...  7 14 13]
        * обычно фразы разбиваются по знакам припинания, здесь будет выдано 2 чанка.
        """
        self.voice = voice if voice is not None else self.voice
        self._check_exists_voice()

        if self._model is None:
            raise RuntimeError(f'Не загружена модель воспроизведения текста.')

        try:
            audio_tensor = self._model.apply_tts(text=text, speaker=self.voice)
            audio = audio_tensor.numpy()

            # нормализация аудио
            max_val = np.max(np.abs(audio))
            if max_val > 0:
                audio = audio / max_val

            # float32 → int16
            audio_int16 = (audio * 32767).astype(np.int16)

        except ValueError:
            # Если ошибка распознавания, то вернуть пустой массив из нулей
            audio_int16 = np.zeros(CHUNK_SIZE, dtype=np.int16)

        # разбиение на чанки как у Piper
        for i in range(0, len(audio_int16), CHUNK_SIZE):
            yield audio_int16[i:i + CHUNK_SIZE]


if __name__ == '__main__':
    tts = TTSCore()
    tts.start(voice='xen')
    [print(i) for i in tts.generate_speech_pcm(text='Скажи что нибудь')]
