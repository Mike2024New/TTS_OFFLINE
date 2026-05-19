from app.tts.piper.ttscore import TTSCore as PiperVoice
from app.tts.silero.ttscore import TTSCore as SileroVoice
from app.tts.piper.model_info import stt_info as piper_stt_info
from app.tts.silero.model_info import stt_info as silero_stt_info

"""
Подключение голосовых stt движков
"""

__all__ = ['TTS_REGISTRY', 'get_info', ]

# блок с классами моделей
TTS_REGISTRY = {
    "piper": PiperVoice,
    "silero": SileroVoice
}

# Блок с информацией для внешних модулей и API
TTS_INFO = {
    'piper': piper_stt_info.get_info,
    'silero': silero_stt_info.get_info,
}


def get_info():
    """Сборщик информации о движках моделях и голосах"""
    info = {}
    for engine in TTS_INFO.keys():
        data = TTS_INFO.get(engine)()
        if data:
            try:
                """Определение доступного голоса по умолчанию, чтобы модель запускалась сразу"""
                first_model = list(data.keys())[0]
                first_voice = data[first_model][0]
                data['default'] = {'engine': engine, 'model': first_model, 'voice': first_voice}
            except Exception:  # noqa
                pass
        info[engine] = data
    return info

# def search_voice():



if __name__ == '__main__':
    res = get_info()
    print(res)
