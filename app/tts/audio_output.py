from time import sleep
import numpy as np
import sounddevice as sd
from typing import Callable
from app import message_bus, Message, COMPONENT_NAME

MAX_SILENCE_TIME = 0.5

SUBCOMPONENT = 'audio_input'
__all__ = ['AudioOutput', ]


class AudioOutput:
    def __init__(self):
        self.stream = None
        self.is_silent = True  # воспроизводится ли сейчас звук или нет
        self._polling_time = None  # время опроса для справки
        self._silence_counter = 0
        self._silence_limit = 0

    def start(self, samplerate: int, callback: Callable):
        """
        Запуск аудиовыхода. Умеет принимать pcm массив аудиоданных и выполнять с ними действия прописанные в callback
        :param samplerate: частота дискретизации (разбиения) звука в ГЦ, чем больше тем лучше но затратнее
        :param callback: функция преобразования/нормализации входного аудиопотока pcm, за тем идет на звуковую карту
        :return:
        """

        def wrapper(outdata, frames, time, status):
            if self._polling_time is None:
                blocksize = frames
                self._polling_time = blocksize / samplerate
                # вычисление лимита чанков, чтобы отследить тишину
                silence_time = MAX_SILENCE_TIME
                self._silence_limit = silence_time / self._polling_time
            callback(outdata, frames, time, status)

            # счётчик тишины
            if np.all(outdata == 0):
                self._silence_counter += 1  # счетчик увеличивается
            else:
                self._silence_counter = 0
                self.is_silent = False

            if self._silence_counter >= self._silence_limit:
                self.is_silent = True

        self.stream = sd.OutputStream(
            samplerate=samplerate,
            channels=1,
            dtype="int16",
            callback=wrapper,
            blocksize=0,  # драйвер звуковой карты автоматически определит размер блока
        )
        self.stream.start()
        # дождаться пока выполнится расчёт polling_time
        while self._polling_time is None:
            sleep(0.1)
        message_bus.add(
            Message(
                component=COMPONENT_NAME,
                subcomponent=SUBCOMPONENT,
                level='info',
                message=f'Компонент `{SUBCOMPONENT}` запущен.'
            )
        )

    def stop(self):
        if self.stream:
            self.stream.stop()
            self.stream = None
            message_bus.add(
                Message(
                    component=COMPONENT_NAME,
                    subcomponent=SUBCOMPONENT,
                    level='info',
                    message=f'Компонент `{SUBCOMPONENT}` остановлен.'
                )
            )


if __name__ == '__main__':
    def callback_fn(outdata, _frames, _time, _status):
        print(outdata)


    audio_output = AudioOutput()
    audio_output.start(samplerate=16000, callback=callback_fn)
    input()
