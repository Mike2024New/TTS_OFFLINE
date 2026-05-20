import sys
import subprocess
import platform
from pathlib import Path

is_windows = platform.system().lower() == 'windows'
separator = ";" if is_windows else ":"
ext = ".dll" if is_windows else ".so"
python_lib = f"Lib\\site-packages" if is_windows else f"lib/python{sys.version_info.major}.{sys.version_info.minor}/site-packages"
python_lib = Path('.venv') / python_lib


def build(
        name: str = 'component',
        add_binary: list[str] | None = None,
        add_data: list[Path] | None = None
):
    print('[green]Сборка приложения[/green]')

    cmd = [
        sys.executable, '-m', 'PyInstaller',
        '--onefile',
        '--console',
        '--name', name,
        '--exclude-module', Path(__file__).stem,
        '--icon=icon.ico',
    ]

    # сборка бинарных файлов (.dll, библиотек)
    if add_binary is not None:
        for binary in add_binary:
            binary_path = python_lib / binary
            # сборка .dll или .so файлов
            for f in binary_path.iterdir():
                if str(f).endswith(ext):
                    cmd.extend(['--add-binary', f'{f}{separator}{binary}'])

    # сборка data
    if add_data is not None:
        for d in add_data:
            data_path = python_lib / d
            cmd.extend(['--add-data', f'{str(data_path)}{separator}{d}'])

    cmd.append('cli.py')

    distributive_path = Path(__file__).parent / 'dist'
    subprocess.run(cmd, shell=is_windows)
    print(f'[green]Приложение собрано. {distributive_path.parent}[/green]')


if __name__ == '__main__':
    build(
        name='TTS',
        add_data=[
            Path('piper') / 'espeak-ng-data',
            Path('ru_normalizr') / 'dictionaries'
        ],
    )
