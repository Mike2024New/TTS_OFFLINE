import os
import subprocess
import threading
import typer
from rich import print
from rich.prompt import Prompt
import platform

print(f'[yellow]Загрузка модуля, подождите...[/yellow]')

from app import message_bus, settings_manager, MODELS_DIR
from app.main import app as component
from app import JSON_LIBRARY_WORDS
from app.tts.text_normalizers.library_words_manager import library_words_get, library_words_reset
from cli_addon import interactive

app = typer.Typer(no_args_is_help=True)
stop_print_messages = threading.Event()
is_windows = platform.system() == "Windows"


def print_messages():
    """Печать сообщений в терминал (для запуска терминальной версии) cli"""
    for msg in message_bus.stream():
        if stop_print_messages.is_set():  # выход из бесконечного полинга сообщений
            break
        print(msg)


@app.callback()
def main():
    """описание модуля"""


@app.command()
def run():
    """Запуск спикера в интерактивном режиме, произношение фраз в терминале [yellow]run[/yellow]"""
    interactive(component)
    # try:
    #     interactive(component)
    # except Exception as err:
    #     component.stop()
    #     print(f'Приложение завершило работу по причине: {err}')


@app.command()
def run_server(
        port: int = typer.Option(8000, '--port', '-p'),
        msg_print: bool = typer.Option(False, '--msg-print', '-msgp', is_flag=True),
):
    """
    Запуск сервера (информация о маршрутах доступна на docs) [yellow]run-server[/yellow]
    --port или -p указать порт на котором будет запущен сервер прямую
    --msg-print или -msgp печатать сообщения из шины сообщений прямо в консоль
    """
    from server import server
    url = f'http://localhost:{port}/docs/'
    print(f'Сервер загружен url: `{url}`')

    if msg_print:
        # запуск печати сообщений прямо в терминал в режиме наблюдения (тогда messages будет пустой)
        threading.Thread(target=print_messages, daemon=True).start()

    try:
        server.start(port=port)
    except KeyboardInterrupt:
        component.stop()
        server.stop()


@app.command()
def model_dir():
    """Открыть директорию с моделями для добавления скачанных моделей [yellow]model-dir[/yellow]"""
    if is_windows:
        os.startfile(MODELS_DIR)
    else:
        subprocess.call(["xdg-open", MODELS_DIR])


@app.command()
def normalize_list():
    """Просмотр кастомного словаря слов нормализации для произношения моделью [yellow]normalize-list[/yellow]"""
    normalizers_words = library_words_get()
    print(normalizers_words)


@app.command()
def normalize_list_edit():
    """Просмотр кастомного словаря слов нормализации для произношения моделью [yellow]normalize-list-edit[/yellow]"""
    if is_windows:
        os.startfile(JSON_LIBRARY_WORDS)
        return

    try:
        subprocess.call(["nano", JSON_LIBRARY_WORDS])
    except Exception:  # noqa
        subprocess.call(['xdg-open', JSON_LIBRARY_WORDS])


@app.command()
def normalize_list_reset():
    """Сбросить словарь кастомных слов нормализации [yellow]normalize-list-reset[/yellow]"""
    user_input = Prompt.ask('[yellow]Вы точно хотите сбросить словарь кастомных слов нормализации(Y/n)?[/yellow]')
    if user_input != 'Y':
        return
    library_words_reset()


@app.command()
def settings_view():
    """Просмотреть текущие настройки [yellow]settings_view[/yellow]"""
    print(settings_manager.settings)


@app.command()
def settings_edit():
    """Открыть настройки json, для редактирования параметров в приложении по умолчанию [yellow]settings_edit[/yellow]"""
    if is_windows:
        os.startfile(settings_manager.json_file_path)
        return

    try:
        subprocess.call(["nano", settings_manager.json_file_path])
    except Exception:  # noqa
        subprocess.call(['xdg-open', settings_manager.json_file_path])


@app.command()
def settings_reset():
    """Сброс параметров к заводским настройкам [yellow]settings-reset[/yellow]"""
    user_input = Prompt.ask('[yellow]Вы точно хотите сбросить настройки параметров к исходным(Y/n)?[/yellow]')
    if user_input != 'Y':
        return
    settings_manager.reset()


if __name__ == '__main__':
    app()
