from app.main import app as component
from config.moduls import TTS_INFO
from rich import print


def run_command(cmd):
    """Безопасный запуск команд с проверкой запущен ли tts движок"""
    if component.is_running:
        cmd()
    else:
        print(
            f'[red]'
            f'Не запущен tts движок. Выберите движок в @info, '
            f'и запустите его "@start <engine> <model> <voice>" в терминале'
            f'[/red]'
        )


def help_info():
    print(
        f'[green]'
        f'[cyan]Функции (введите это в консоль):[/cyan]\n'
        f'  [cyan]@info[/cyan] - просмотр доступных голосовых tts движков (выводит команды запуска).\n'
        f'  [cyan]@params[/cyan] - текущее состояние tts, включен ли, какой движок и модель используются.\n'
        f'  [cyan]@start <engine> <model> <voice>[/cyan] - запустить новый движок (см. список tts в `@info` ).\n'
        f'  [cyan]@stop[/cyan] - остановить текущий движок.\n'
        f'  [cyan]@exit[/cyan] - завершить работу приложения.\n'
        f'  [cyan]@help[/cyan] - получить справку о командах.\n'
        f'[cyan]Управление воспроизведением:[/cyan].\n'
        f'  [cyan]#[/cyan] or [cyan]№[/cyan] - пауза/продолжить речь (в момент воспроизведения).\n'
        f'  [cyan]$[/cyan] or [cyan];[/cyan] - прервать речь (в момент воспроизведения).\n'
        f'  [cyan]%[/cyan] - повторить последнюю фразу.\n'
        f'[/green]'
    )


def interactive():
    """Интерактивный режим работы с tts движками"""
    text = ''
    text_repeat = ''
    engine = None
    model = None
    voice = None
    pause = False
    print(f'[yellow]Приложение запущено[/yellow]')
    help_info()
    while True:
        user_input = input('>>>')

        if user_input == '@help':
            help_info()

        elif user_input == '@exit':
            return None

        elif user_input == '@info':
            engines = TTS_INFO.keys()
            if engines:
                for eng in engines:
                    for model in TTS_INFO[eng]:
                        [print(f'@start {eng} {model} {voice}') for voice in TTS_INFO[eng][model]['voices']]
            else:
                print(
                    '[yellow]'
                    'Не найдено ни одного движка. См. README.md -> Быстрый старт для разработчиков -> пункт 3.'
                    '[/yellow]',
                )

        elif user_input.startswith('@start'):
            """Запуск tts движка"""
            try:
                if component.is_running:  # перезагрузка компонента
                    component.stop()
                user_input = user_input.replace('@start', '')
                user_input = user_input.strip()  # noqa
                engine, model, voice = user_input.split()
                component.start(engine=engine, model=model, voice=voice)
                print(f'[green]tts [{engine} {model} {voice}] запущен, введите текст и нажмите 2 раза enter.[/green]')
            except Exception as err:
                print(
                    f'Ошибка при запуска движка, вероятно неправильно введен формат.\n'
                    f'Правильный формат движка "@start <engine> <model> <voice>" (его можно выбрать в @info)\n'
                    f'err: {err}'
                )

        elif user_input == '@params':
            print(
                f'[cyan]'
                f'Параметры:\n'
                f'\tTTS : {"[green]ON[/green]" if engine is not None else "[red]OFF[/red]"}\n'
                f'\tengine: [yellow]{engine}[/yellow]\n'
                f'\tmodel: [yellow]{model}[/yellow]\n'
                f'\tvoice: [yellow]{voice}[/yellow]\n'
                f'[/cyan]'
            )

        elif user_input == '@stop':
            """Остановка tts движка"""
            try:
                run_command(cmd=lambda: component.stop())
                engine = None
                model = None
                voice = None
            except Exception as err:
                print(f'[red]Не удалось остановить движок. Ошибка: {err}[/red]')

        elif user_input == '%':
            """Повтор последней произнесенной речи"""
            run_command(cmd=lambda: component.say(text_repeat))

        elif user_input == '$' or user_input == ';':
            """Остановка речи"""
            run_command(cmd=lambda: component.interrupt())

        elif user_input == '#' or user_input == '№':
            """Пауза, приостановить речь"""
            if component.is_running:
                run_command(cmd=lambda: component.pause() if not pause else component.resume())
                pause = not pause

        else:
            # накопление текста до тех пор пока не получена пустая строка (для поддержки многострочного текста)
            if user_input != '':
                text += user_input
            else:
                run_command(cmd=lambda: component.say(text=text))
                text_repeat = text  # текст в повтор
                text = ''
                pause = False  # сброс паузы
