import sys
import subprocess

"""
Установка зависимостей
"""
from pathlib import Path

try:
    resources_path = Path.cwd() / 'resources' / 'models'
    (resources_path / 'piper').mkdir(parents=True, exist_ok=True)
    (resources_path / 'silero').mkdir(parents=True, exist_ok=True)
except Exception as err:
    print(
        f'Не удалось создать каталоги для моделей, причина:`{err}`\n'
        f'Создайте в главной каталоге проекта (там где лежит .venv) каталог resources/models, и в нем две папки silero и piper'
    )

try:
    print(f'Установка uv')
    cmd = [sys.executable, '-m', 'pip', 'install', 'uv']
    subprocess.run(cmd, capture_output=False)

    print(f'Установка зависимостей')
    cmd = ['uv', 'sync']
    subprocess.run(cmd, capture_output=False)
except Exception as err:
    print(
        f'Не удалось установить зависимости по причине {err}\n'
        f'Проверьте что у вас создано виртуальное окружение\n'
        f'За тем выполните `pip install uv` (если он не установлен в системе)\n'
        f'`uv sync` - установка зависимых библиотек'
    )
