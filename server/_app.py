from fastapi import FastAPI, status, Request
from app import message_bus
from app.main import app as component
from utils.message_bus_manager.message_bus_manager import Message
from app.routers import router
from app import settings_manager, Settings
from config.moduls import TTS_INFO
from server._server import Server

app = FastAPI()
app.include_router(router)
server = Server(application=app)

__all__ = ['server']  # объект для управления сервером


@app.get(
    '/info/',
    summary='Общая информация о доступных движках, их моделях и голосах если есть.'
)
def test(request: Request):
    info_data = {}
    port = request.url.port
    for eng in TTS_INFO:
        info_data[eng] = {}
        for model in TTS_INFO[eng]:
            info_data[eng][model] = {
                'voices': [],
                'urls': [],
                'lang': TTS_INFO[eng][model]['lang'],
            }
            for voice in TTS_INFO[eng][model]['voices']:
                url = f'http://localhost:{port}/start/?engine={eng}&model={model}&voice={voice}'
                info_data[eng][model]['voices'].append(voice)
                info_data[eng][model]['urls'].append(url)

    return {'info': info_data}


@app.get('/status/')
def component_status():
    return {
        'msg': 'Состояние компонента',
        'is_running': component.is_running,
    }


@app.get('/start/')
def component_start(engine: str, model: str | None = None, voice: str | None = None):
    """Информацию о движках и моделях можно посмотреть в `/info/`, там же можно получить url для запуска приложения"""
    component.start(engine=engine, model=model, voice=voice)
    return {
        'msg': f'Компонент `{component.name}` запущен.',
    }


@app.get('/stop/')
def component_stop():
    component.stop()
    return {
        'msg': f'Компонент `{component.name}` остановлен.',
    }


@app.get(
    '/messages/',
    response_model=dict[str, list[Message] | str],
    status_code=status.HTTP_200_OK,
    summary='Получение данных из шины сообщений',
)
def get_messages_all():
    messages = message_bus.get_all()
    return {
        'msg': 'Накопленные сообщения из шины сообщений',
        'messages': [m.model_dump() for m in messages],
    }


@app.get(
    '/settings/',
    response_model=dict[str, Settings],
    status_code=status.HTTP_200_OK,
    summary='Информация о текущих настройках',
)
def settings_get():
    return {'settings': settings_manager.settings}


@app.post(
    '/settings-edit/',
    response_model=dict[str, Settings],
    status_code=status.HTTP_200_OK,
    summary='Изменение настроек',
)
def settings_update(new_settings: Settings):
    settings_manager.apply_new_settings(settings=new_settings)
    return {'settings': settings_manager.settings}


@app.delete(
    '/settings-reset/',
    response_model=dict[str, Settings],
    status_code=status.HTTP_200_OK,
    summary='Сбросить все настройки к заводским',
)
def settings_reset():
    settings_manager.reset()
    return {'settings': settings_manager.settings}


@app.get(
    '/shutdown/',
    response_model=dict[str, str],
    status_code=status.HTTP_200_OK,
    summary='Остановка сервера'
)
def shutdown():
    """Остановка сервера"""
    # сперва остановить компонент если он запущен
    if component.is_running:
        component.stop()
    # остановить сервер
    server.stop()
    return {
        'msg': 'сервер остановлен.'
    }


if __name__ == '__main__':
    print(f'/shutdown/ для остановки сервера')
    server.start()
