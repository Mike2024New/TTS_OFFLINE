import threading
from collections import deque
from time import sleep

from app import message_bus, Message, COMPONENT_NAME, settings_manager
from app.tts import TTS_REGISTRY
from app.tts.tts_engine_protocol import TTSEngine
import numpy as np
from app.text_normalizers.main import normalizer
from app.tts.audio_output import AudioOutput

SUBCOMPONENT = 'TTS'
TEXT_DEVIDER_LIMIT = 1000
TEXT_DEVIDER_SYMBOLS = '!.,?;'

__all__ = ['TTS', 'TTSEngine']


class TTS:
    def __init__(self):
        self._audio_output = AudioOutput()
        self._voice: TTSEngine | None = None
        self.normalizer = None  # нормализатор
        # общая очередь чанков без фиксированного размера, просто складываются все чанки подряд
        self._buffer = deque()
        # кольцевой буфер, для формирования коллекции чанков размером который поддерживает sounddevice (frames)
        self._buffer_ring = np.zeros(0, dtype=np.int16)
        # мгновенная остановка
        self._stop_flag = threading.Event()
        self._pause_flag = threading.Event()
        self._last_bufer = deque()

    def is_silent(self):
        """Тишина ли сейчас или воспроизведение звука"""
        return self._audio_output.is_silent

    def start(self, engine, model: str | None = None, voice: str | None = None):
        """Запуск tts движка"""
        try:
            engine = TTS_REGISTRY.get(engine)
            if settings_manager.settings.normalizer:
                self.normalizer = normalizer  # нормализатор
            self._voice = engine()
            self._voice.start(model_name=model, voice=voice)  # загрузка модели
            self._audio_output.start(callback=self._callback, samplerate=self._voice.SAMPLERATE)  # запуск аудиодевайса
            message_bus.add(
                Message(
                    component=COMPONENT_NAME,
                    subcomponent=SUBCOMPONENT,
                    level='info',
                    message=f'Компонент {COMPONENT_NAME} успешно запущен.'
                )
            )
        except Exception as err:
            message_bus.add(
                Message(
                    component=COMPONENT_NAME,
                    subcomponent=SUBCOMPONENT,
                    level='error',
                    message=f'Ошибка при запуске компонента {COMPONENT_NAME}: {err}'
                )
            )
            raise RuntimeError(err)

    def stop(self):
        """Остановка tts движка"""
        try:
            self._voice.stop()
            self._audio_output.stop()
            message_bus.add(
                Message(
                    component=COMPONENT_NAME,
                    subcomponent=SUBCOMPONENT,
                    level='info',
                    message=f'Компонент `{COMPONENT_NAME}` успешно остановлен.'
                )
            )
        except Exception as err:
            message_bus.add(
                Message(
                    component=COMPONENT_NAME,
                    subcomponent=SUBCOMPONENT,
                    level='error',
                    message=f'Ошибка при остановке компонента {COMPONENT_NAME}: {err}'
                )
            )

    def pause(self):
        """Остановка воспроизведения речи"""
        if not self.is_silent():
            self._pause_flag.set()

    def resume(self):
        """продолжение воспроизведения речи"""
        self._pause_flag.clear()

    @staticmethod
    def text_devider(text: str):
        """Разбиение текста по предложениям, а также проверка чтобы он не превышал лимит символов
        (например silero выдает ошибку на длине текста более 1000 симвлов)"""
        text_out = []
        sentence = ''
        i = 0
        while i < len(text):
            sentence += text[i]
            if text[i] in TEXT_DEVIDER_SYMBOLS:
                text_out.append(sentence)
                sentence = ''
            elif len(sentence) >= TEXT_DEVIDER_LIMIT:
                j = sentence.rfind(' ')  # поиск последнего пробела
                text_out.append(sentence[:j])
                sentence = sentence[j:]
            i += 1

        # добавить хвостовое предложение
        if sentence:
            text_out.append(sentence)

        return text_out

    def say(self, text: str, voice: str | None = None, wait: bool = False):
        """Говорить фразу из текста, подходит для коротких фраз и тех случаев когда модель текст уже готов"""
        if text == '':
            return
        self.interrupt()  # прервать речь если она сейчас ведется
        self._last_bufer.clear()  # сброс последней фразы буфера
        self._stop_flag.clear()
        try:
            if settings_manager.settings.normalizer:
                text = self.normalizer(text=text, model_name=self._voice.model_name)
            text = self.text_devider(text)  # деление текста, проверка чтобы он не превышал лимит по длине
            for part_text in text:
                pcm_generator = self._voice.generate_speech_pcm(text=part_text, voice=voice)
                for pcm in pcm_generator:
                    if self._stop_flag.is_set():
                        break
                    self._buffer.append(pcm)
                    self._last_bufer.append(pcm)

            if wait:
                while self.is_silent():
                    sleep(0.05)
                while not self.is_silent():
                    sleep(0.1)

        except Exception as err:
            raise RuntimeError(
                f'Не удалось воспроизвести речь. Ошибка: {err}'
            )

    def say_from_generator(self, generator, voice: str | None = None):
        """Чтение текста из генератора (например от ИИ моделей которые выдают текст последовательно)"""
        self.interrupt()  # прервать речь если она сейчас ведется
        self._stop_flag.clear()
        self._last_bufer.clear()  # сброс последней фразы буфера

        def say():
            for text in generator:
                if settings_manager.settings.normalizer_extends:
                    text = self.normalizer(text=text, model_name=self._voice.model_name)  # перевод дат в тексте в слова
                text = self.text_devider(text)  # деление текста, проверка чтобы он не превышал лимит по длине
                for part_text in text:
                    pcm_generator = self._voice.generate_speech_pcm(text=part_text, voice=voice)
                    for pcm in pcm_generator:
                        if self._stop_flag.is_set():
                            break
                        self._buffer.append(pcm)
                        self._last_bufer.append(pcm)

        try:
            threading.Thread(target=say).start()
        except Exception as err:
            raise RuntimeError(
                f'Не удалось воспроизвести речь. Вероятно модель не инициализирована. Используйте `start`. orignal error: {err}'
            )

    def _callback(self, outdata, frames, _time, _status):
        """
        Модификация outdata (аудиовыхода)
        Просмотр аудиобуфера, выборка поддерживаемого sounddevice количества чанков (frames)
        эти данные (outdata) отдаются в аудиовыход.
        Метод поддерживает экстренную остановку (вызывается через interrupt)
        Ключевой компонент кольцевой буфер который собирает в себя чанки, строго нужное количество
        """
        if self._stop_flag.is_set() or self._pause_flag.is_set():  # если речь прервана (или пауза), отдать тишину
            outdata[:] = 0
            return

        while len(self._buffer_ring) < frames:  # пополнять буфер размером frames
            if not self._buffer:
                break

            chunk = self._buffer.popleft()
            self._buffer_ring = np.concatenate([self._buffer_ring, chunk])

        if len(self._buffer_ring) < frames:
            # если буфер меньше требуемой длины, не хватает данных то выдать тишину ( [0,0, ... 0, 0] )
            outdata[:] = 0  # заполнить все элементы массива нулями
            return

        # взять в outdata чанки из кольцевого буфера (преобразование в двумерный массив)
        outdata[:] = self._buffer_ring[:frames].reshape(-1, 1)
        self._buffer_ring = self._buffer_ring[frames:]

    def interrupt(self):
        """Резкая остановка речевой модели - перебивание"""
        self._stop_flag.set()
        # очистка буферов
        self._buffer.clear()
        self._buffer_ring = np.zeros(0, dtype=np.int16)
        self._pause_flag.clear()  # сброс пауз

    def repeat(self):
        """Возможность повторить последнюю фразу, если сейчас тишина"""
        if self._audio_output.is_silent and not self._pause_flag.is_set():
            self._buffer = self._last_bufer.copy()
            return
        raise RuntimeError(f'Повтор сейчас не возможен, так как спикер говорит или режим паузы.')


if __name__ == '__main__':
    tts = TTS()
    # tts.start(engine='piper', model='ru_RU-denis-medium')
    # tts.say(text='3.12.12', voice='ru_RU-denis-medium', wait=True)
    # tts.say(text='Привет! Я Ксения! Меня знает вся Кения.', voice='xenia', wait=True)
    # tts.say(text='Привет! Я Айдар, мой голос мой дар.', voice='aidar', wait=True)
