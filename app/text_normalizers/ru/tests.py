from app.text_normalizers.ru.extends import extension_pipeline
from app.text_normalizers.ru.main import normalize


def test_normalizer_and_extends():
    """Тесты проверяющие корректность нормализатора, использующего под капотом расширения"""
    assert normalize(text='0.02') == 'ноль целых две сотых'
    assert normalize(text='Привет! Давай встретимся в 15:00') == 'Привет! Давай встретимся в пятнадцать: ноль ноль'
    assert normalize(text='Сегодня 16.05.2026') == 'Сегодня шестнадцатого мая две тысячи двадцать шестого года'
    assert normalize(text='Давай сходим в macdonalds') == 'Давай сходим в мэкдонэлдс'
    assert normalize(text='I am live in Moscow') == 'ай эм лив ин москау'
    assert normalize(text='У меня есть 3 яблока и 4 груши') == 'У меня есть три яблока и четыре груши'
    assert normalize(text='Тебе письмо от ГБУ Жилищник') == 'Тебе письмо от гэ бэ у Жилищник'
    assert normalize(text='3.2') == 'три целых две десятых'
    assert normalize(text='PC, CPU', library_words={'PC': 'пэ ка', 'CPU': 'си пи ю'}) == 'пэ ка, си пи ю'


def test_only_extends():
    """Тесты что всё в порядке ни чего не отвалилось"""
    assert extension_pipeline(text='0') == ' ноль '
    assert extension_pipeline(text='3.12.12') == '  три   двенадцать   двенадцать '
    assert extension_pipeline(text='00') == ' ноль ноль '
    assert extension_pipeline(text='00000') == ' ноль ноль ноль ноль ноль '
    assert extension_pipeline(text='1') == '1'
    assert extension_pipeline(text='10') == '10'
    assert extension_pipeline(text='10 000') == '10 000'
    assert extension_pipeline(text='10 000 000') == '10 000 000'
    assert extension_pipeline(text='01') == ' ноль 1'
    assert extension_pipeline(text='demo 000') == 'demo  ноль ноль ноль '
    assert extension_pipeline(text='demo 000 123 post, 10 000.') == 'demo  ноль ноль ноль  123 post, 10 000.'
    assert extension_pipeline(text='demo 000 123 post, 000.') == 'demo  ноль ноль ноль  123 post,  ноль ноль ноль .'
    assert extension_pipeline(
        text=f'21.02.2023 дата') == '  двадцать первого февраля две тысячи двадцать третьего года  дата'
    assert extension_pipeline(
        text=f'Не дата 55.02.2023') == 'Не дата   пятьдесят пять   ноль  два   две тысячи двадцать три '
    assert extension_pipeline(text=f'Артикул 21.05.130') == 'Артикул   двадцать один   ноль  пять   сто тридцать '
    assert extension_pipeline(text=f'Дробь 21.05') == 'Дробь двадцать одна целая пять сотых'
    assert extension_pipeline(text=f'Коэффициент 0.23 w') == 'Коэффициент ноль целых двадцать три сотых w'
    assert extension_pipeline(
        text=f'приложение на Python 3.12.12.') == 'приложение на Python   три   двенадцать   двенадцать .'
    assert extension_pipeline(text=f'Сегодня 3.12.2012.') == 'Сегодня   три   двенадцать   две тысячи двенадцать .'
    assert extension_pipeline(text=f'Код доступа 000123.') == 'Код доступа  ноль ноль ноль 123.'
    assert extension_pipeline(text=f'Не путаю нули, вот код 000.') == 'Не путаю нули, вот код  ноль ноль ноль .'
    assert extension_pipeline(text=f'Сумма 22 000.') == 'Сумма 22 000.'
    assert extension_pipeline(text=f'Не сумма 22 00.') == 'Не сумма 22  ноль ноль .'
    assert extension_pipeline(
        text=f'У меня в розетке напряжение 220 000 вольт, я боюсь') == 'У меня в розетке напряжение 220 000 вольт, я боюсь'
    assert extension_pipeline(text='3/2') == '3/2'


if __name__ == '__main__':
    test_only_extends()
    test_normalizer_and_extends()
