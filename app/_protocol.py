from typing import Protocol


class AppProtocol(Protocol):
    """
    Подключаемый класс компонента.
    В классе должны быть реализованы:
    is_running - поле состояния компонента
    start - метод запуска приложения (запускающий все потоки)
    stop - метод остановки приложения (убивающий все потоки внутри)
    """
    is_running: bool

    def start(self, *args, **kwargs) -> bool: ...

    def stop(self) -> bool: ...
