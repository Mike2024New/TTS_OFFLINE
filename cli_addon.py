from rich import print
from app.tts import get_info
from app import settings_manager
from app.tts.text_normalizers.main import get_current_language_by_model
import sys
from app.tts.text_normalizers.get_curren_date_ru import get_current_date_ru

__all__ = ['interactive']


def safe_input(prompt: str = "") -> str:
    """Безопасный ввод для Linux, игнорирует невалидные UTF-8 байты."""
    sys.stdout.write(prompt)
    sys.stdout.flush()
    raw = sys.stdin.buffer.readline()
    try:
        return raw.decode('utf-8').strip()
    except UnicodeDecodeError:
        return ''  # возвращаем пустую строку при мусоре


def interactive(component):
    """Набросаный на скору руку интерактивный режим работы приложения"""
    voices_data = get_info()

    def get_settings_params():
        # попытка загрузиться через конфигурацию пользователя
        data = voices_data.get(settings_manager.settings.engine)
        if not data:
            print(
                f'[yellow]Не найден engine `{settings_manager.settings.engine}`, прописанный в настройках settings.json, будет взята первая доступная модель.[/yellow]')
            return None
        data = data.get(settings_manager.settings.model)
        if not data:
            print(
                f'[yellow]Не найдена model `{settings_manager.settings.model}`, прописанная в настройках settings.json, будет взята первая доступная модель.[/yellow]')
            return None
        if settings_manager.settings.voice in data:
            return {
                'engine': settings_manager.settings.engine,
                'model': settings_manager.settings.model,
                'voice': settings_manager.settings.voice,
            }
        print(
            f'[red]Не найден voice `{settings_manager.settings.voice}`, прописанный в настройках settings.json, будет взята первая доступная модель. Поправьте настройки json[/red]')
        return None

    settings_params = get_settings_params()
    if settings_params:
        default_speaker_str = f"@start {settings_params['engine']} {settings_params['model']} {settings_params['voice']}"
        engine = settings_params['engine']
        model = settings_params['model']
        voice = settings_params['voice']
        component.start(
            engine=engine,
            model=model,
            voice=voice,
        )
        current_language = get_current_language_by_model(model_name=settings_params['model'])
        print(f'[green]Загружен спикер из настроек settings.json[/green]')
    else:
        engines = list(voices_data.keys())
        first_engine = None
        for engine in engines:
            if voices_data[engine]:
                first_engine = engine
        if first_engine is None:
            print(
                f'[red]'
                f'Сейчас в приложении нет ни одной модели, скачайте модели:\n'
                f'  [cyan]piper[/cyan] - https://huggingface.co/rhasspy/piper-voices/tree/main - скачивать `.onnx` , `.onnx.json`, например для работы модели [cyan]`ru_RU-denis-medium`[/cyan] качать файлы [cyan]`ru_RU-denis-medium.onnx`[/cyan] и [cyan]`ru_RU-denis-medium.onnx.json`[/cyan].\n'
                f'  [cyan]silero[/cyan] - https://models.silero.ai/models/tts/ - скачивать файлы с расширением .pt, например для работы модели [cyan]`v5_5_ru`[/cyan] файл [cyan]`v5_5_ru.pt`[/cyan].\n'
                f'После скачивания разместите модели в директории: silero положить в `resources/models/silero`, piper положить в `resources/models/piper` (используйте команду `model-dir` в терминале\n'
                f'* (url актуален на 18.05.2026)\n'
                f'[/red]'
            )
            return None
        default = voices_data[first_engine]['default']
        default_speaker_str = f"@start {first_engine} {default['model']} {default['voice']}"
        engine = default['engine']
        model = default['model']
        voice = default['voice']
        component.start(
            engine=engine,
            model=model,
            voice=voice,
        )
        current_language = get_current_language_by_model(model_name=default['model'])

    availables_voices_list = get_info().get(engine).get(model)

    current_speaker_str = default_speaker_str

    print(
        f'[green]'
        f'Приложение запущено\n'
        f'{"-" * 50}\n'
        f'Введите текст и нажмите `enter` два раза (двойной enter чтобы можно было вставлять многострочный текст)\n'
        f'По умолчанию загружен [yellow]`{current_language}`[/yellow] спикер [yellow]`{default_speaker_str}`[/yellow]\n'
        f'Функции (введите это в консоль):\n'
        f'  [cyan]#[/cyan] или [cyan]№[/cyan]  - приостановить/продолжить.\n'
        f'  [cyan]$[/cyan] или [cyan];[/cyan]  - прервать речь.\n'
        f'  [cyan]%[/cyan]  - повторить последнюю фразу (не работает если спикер говорит, или режим паузы).\n'
        f'  [cyan]@start <engine> <model> <voice>[/cyan]   - запустить новый голос (см. список голосов в [cyan]`@info`[/cyan] ).\n'
        f'  [cyan]@info[/cyan]   - посмотреть доступные голоса, и выбрать спикера. Скопировать команду и вставить в терминал.\n'
        f'  [cyan]@demo[/cyan]   - спикер произнесет демонстрационный текст.\n'
        f'  [cyan]@date[/cyan]   - спикер скажет точное время.\n'
        f'  [cyan]@params[/cyan] - текущий спикер, доступные голоса спикера.\n'
        f'  [cyan]@exit[/cyan]  - завершить работу приложения.\n'
        f'{"-" * 50}\n'
        f'[/green]')

    text = ''
    text_repeat = ''
    pause = False
    while True:
        user_input = safe_input(prompt='>>>')
        if user_input.startswith('@start'):
            try:
                user_input = user_input.replace('@start', '')
                engine, model, voice = user_input.split()
                # перезагрузка компонента на другой голос
                print(f'[yellow]Запуск спикера...[/yellow]')
                if component.is_running:
                    component.stop()
                current_speaker_str = f"@start {engine} {model} {voice}"
                component.start(engine=engine, model=model, voice=voice)
                availables_voices_list = get_info().get(engine).get(model)  # обновление списка доступных голосов
                print(f'[green]Спикер запущен введите текст и нажмите 2 раза enter[/green]')
            except Exception as err:
                print(f'[red]'
                      f'Не удалось запустить голос. Скорее всего не правильно введен формат.\n'
                      f'Введите в таком виде `@start <engine> <model> <voice>` (см. подсказки в @info),\n'
                      f'оригинальный текст ошибки: {err}'
                      f'[/red]')

        elif user_input == '@params':
            print(f'[yellow]'
                  f'Текущие параметры модели: `{current_speaker_str}`\n'
                  f'Список голосов для данной модели: `{availables_voices_list}`'
                  f'[/yellow]')

        elif user_input == '@demo':
            if component.is_running:
                component.interrupt()
                demo_text = (
                    'Привет! Пользователь приложения. Теперь твой компьютер умеет разговаривать.'
                    'Ты можешь напечатать в этом чате всё что захочешь, а я проговорю это всё вслух.'
                    'Можешь выбрать любой голос из доступных, которые ты можешь посмотреть в собачка @info.'
                    'Я могу сказать тебе точное время если ты введешь в чате собачка @date.'
                    f'Например: {get_current_date_ru()}'
                )
                print(f'~~~ {demo_text}')
                text_repeat = demo_text
                component.say(text=demo_text)


        elif user_input == '@info':
            voices_data = get_info()
            print(f'[yellow]Доступные модели (скопировать и вставить в чат):[/yellow]')
            for eng in voices_data:
                for mod in (voices_data[eng]).keys():
                    if mod != 'default':
                        [print(f'[green]@start {eng} {mod} {voice}[/green]') for voice in voices_data[eng][mod]]

        elif user_input == '@date':
            if component.is_running:
                component.interrupt()
                date_text = get_current_date_ru()
                print(f'~~~ {date_text}')
                text_repeat = date_text
                component.say(text=date_text)

        elif user_input == '$' or user_input == ';':
            if component.is_running:
                component.interrupt()
                print(f'[yellow]прервано[/yellow]')

        elif user_input == '#' or user_input == '№':
            if component.is_running and not pause:
                component.pause()
                pause = True
                print(f'[yellow]пауза[/yellow]')
            else:
                print(f'[yellow]продолжение речи[/yellow]')
                component.resume()
                pause = False

        elif user_input == '%':
            if component.is_running:
                try:
                    print(f'~~~ {text_repeat}')
                    component.repeat()
                except Exception as err:
                    print(f'[red]{err}[/red]')


        elif user_input == '@exit':
            break


        else:
            if component.is_running:
                text_repeat = ''
                if user_input != '':
                    text += f" {user_input} "
                    continue

                if text == '':
                    continue

                pause = False
                print(f'~~~ {text}')
                text_repeat = text

                component.say(text=text, voice=voice)
                text = ''
                continue
            print(f'[yellow]Спикер не инициализирован выберите спикера из `@info`[/yellow]')

    return None
