import threading
from time import sleep
from piper import PiperVoice
from collections import deque
from app import PIPER_MODELS_DIR, message_bus, Message, COMPONENT_NAME
from app.tts.tts_engine_protocol import TTSEngine
from app.tts.piper.model_info import stt_info

__all__ = ['TTSCore', ]

SUBCOMPONENT = 'piper'
CHUNK_SIZE = 1024


class TTSCore(TTSEngine):
    SAMPLERATE = 22050

    def __init__(self):
        self._model = None
        default_parameters = stt_info.get_default_parameters()
        self.model_name = default_parameters.get('model')
        self.voice = default_parameters.get('voice')

    def start(self, model_name: str | None = None, voice: str | None = None):
        self.voice = voice  # для этой модели голос не устанавливается, параметр просто для совместимости с другими моделями
        self.model_name = model_name if model_name is not None else self.model_name
        self._model = PiperVoice.load(str(PIPER_MODELS_DIR / f"{self.model_name}.onnx"))
        message_bus.add(
            Message(
                component=COMPONENT_NAME,
                subcomponent=SUBCOMPONENT,
                level='info',
                message=f'Компонент `{SUBCOMPONENT}` запущен.',
                data={'model': {self.model_name}},
            )
        )

    def generate_speech_pcm(self, text: str, voice: str = ''):
        """
        Выдача генератора pcm массива из сгенерированных текстовых данных, например фраза "Привет! как дела?":
        [-9 -2  0 ... 30 39 41]
        [-3 -3  5 ...  7 14 13]
        * обычно фразы разбиваются по знакам припинания, здесь будет выдано 2 чанка.
        """
        _voice = voice  # заглушка, в piper voice не меняется на лету (можно будет потом сделать пересоздание модели)
        if self._model is None:
            raise RuntimeError(
                f'Ошибка, запуска анализатора речи. Скорее всего не была загружена модель использу `start`'
            )
            # yield np.zeros(CHUNK_SIZE, dtype=np.int16)
        for chunk in self._model.synthesize(text):
            yield chunk.audio_int16_array

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


if __name__ == '__main__':
    """Пример использования речевого движка"""
    stop_event = threading.Event()
    bufer = deque()


    def audio_output():
        """Иммитация функции произношения текста"""
        while not stop_event.is_set():
            if bufer:
                pcm = bufer.popleft()
                # print(pcm)  # в этой точке текст отдается в аудиовоспроизводитель
                for p in pcm[:20]:
                    if stop_event.is_set():  # быстрое прерывание речи
                        print(f' речь была прервана ')
                        break
                    print(f" {p} ", end='')
                    sleep(0.2)
                print()
            sleep(0.2)


    stt = TTSCore()
    stt.start()
    threading.Thread(target=audio_output).start()
    while True:
        user_input = input(f'Введите любой текст для аудио:>_')
        if user_input == '':
            stop_event.set()
            break
        pcm_generator = stt.generate_speech_pcm(text=user_input)
        [bufer.append(ch) for ch in pcm_generator]
