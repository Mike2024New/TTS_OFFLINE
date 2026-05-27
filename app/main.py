import threading
from app._protocol import AppProtocol
from app.tts.tts import TTS
from config.moduls import TTS_INFO

__all__ = ['app']


class App(AppProtocol):
    def __init__(self):
        self._exit_flag = threading.Event()
        self.is_running = False
        self.app = TTS()
        self.lang = None
        self._model_name = None
        self._normalizer = []

    def start(self, engine: str, model: str, voice: str, text_normalizer: bool = True, *args, **kwargs):
        """
        engine : движок модели например piper_engine, silero
        model : внутренняя модель движка например в piper_engine это 'ru_RU-dmitri-medium', а в silero это 'v5_ru'
        voice : выбор голоса зашитого в модели например в piper_engine `ru_RU-dmitri-medium` это и есть сама модель. А в silero v5_ru это уже список голосов ['xenia', 'aidar', и так далее]
        Запуск речевой модели на выбранном движке
        """
        if not self.is_running:
            if engine not in TTS_INFO:
                raise RuntimeError(f'Движок `{engine}` не найден среди списка движков `{list(TTS_INFO.keys())}`')
            model_data = TTS_INFO[engine][model]
            if model_data is None:
                raise RuntimeError(f'Модель `{model}` не найдена в движке `{engine}`')

            self._model_name = model
            self.lang = TTS_INFO[engine][model]['lang']  # получение языка модели
            if text_normalizer:
                from config.moduls import NORMALIZERS_REGISTRY
                self._normalizer = NORMALIZERS_REGISTRY
            self.app.start(engine=engine, model=model, voice=voice)
            self.is_running = True
            return True
        return False

    def stop(self) -> bool:
        """остановка речевой модели"""
        if self.is_running:
            self.app.stop()
            self.is_running = False
            return True
        return False

    def say(self, text: str, voice: str | None = None, wait: bool = False):
        """произнести речь"""
        # проход текста через список нормализаторов
        if self._normalizer:
            for normalizer in self._normalizer:
                text = normalizer(lang=self.lang, text=text)
        self.app.say(text, voice=voice, wait=wait)

    def say_from_generator(self, generator, voice: str | None = None):
        """речь из генератора (например для ИИ который не сразу выдает весь текст)"""
        self.app.say_from_generator(generator=generator, voice=voice)

    def interrupt(self):
        """прервать текущую озвучку"""
        self.app.interrupt()

    def is_silent(self):
        """тишина ли сейчас (может быть полезным для api)"""
        return self.app.is_silent()

    def pause(self):
        """приостановить текущий диалог с возможностью продолжить (resume)"""
        self.app.pause()

    def resume(self):
        """продолжить приостановленный диалог"""
        self.app.resume()

    def repeat(self):
        """Повтор последней фразы, работает только если сейчас спикер молчит, и если нет состояния паузы"""
        self.app.repeat()


app = App()

if __name__ == '__main__':
    app.start(engine='piper', model='ru_RU-dmitri-medium.onnx', voice='ru_RU-dmitri-medium.onnx')
    app.say(text='Привет! Я Руслан. Hello world! Я купил себе PC.', wait=True)

    # app.start(engine='silero', model='v5_ru_RU.pt', voice='aidar', lang='ru-RU', text_normalizer=True)
    # app.say(text='Привет! Я Айдар! 007', voice='aidar', wait=True)
    # app.say(text='А я Ксения! 3.12.4', voice='xenia', wait=True)
    # app.say(text='3.12.4', voice='xenia', wait=True)
