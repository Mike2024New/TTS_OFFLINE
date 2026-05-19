import threading
from app._protocol import AppProtocol
from app.tts.tts import TTS

__all__ = ['app']


class App(AppProtocol):
    def __init__(self):
        self._exit_flag = threading.Event()
        self.is_running = False
        self.app = TTS()

    def start(self, engine: str, model: str | None = None, voice: str | None = None, *args, **kwargs):
        """Запуск речевой модели на выбранном движке"""
        if not self.is_running:
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
    app.start(engine='silero')
    app.say(text='Привет! Я голосовой ассистент, но ты даже не представляешь, что я могу.')
    app.say(text='Привет! Я голосовой ассистент, но ты даже не представляешь, что я могу.', voice='xenia')
    input()
