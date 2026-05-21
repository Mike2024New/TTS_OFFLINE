from num2words import num2words
import re
from app import message_bus, Message
from ru_normalizr import Normalizer, NormalizeOptions

normalizer = Normalizer(NormalizeOptions.tts(latinization_backend='ipa', ))
__all__ = ['extension_pipeline']


def date_ext(text: str) -> str:
    """
    Преобразование дат в тексте.
    """

    def repl(match):
        date = match.group()
        end = match.end()
        if end < len(text):
            if text[end] == '.' and text[end + 1].isdigit():
                return date
        normalize_date = normalizer.normalize(text=f'`{date}')
        if 'целых' not in normalize_date:
            # нормализер может преобразовывать даты в дробь особенно если они в начале текста, чтобы этого избежать
            # в начало фразы подстановка символа `, который смещает дату от начала предложения и нормализер дает
            # корректный результат. Если в результате нормализера отсутствует слово целых, значит на выходе именно дата
            date = normalize_date.replace('`', '')
            return f' {date} '
        return date

    pattern = r'(\d{1,2}\.\d{1,2}\.\d{4})'

    return re.sub(pattern=pattern, repl=repl, string=text)


def version_ext(text: str) -> str:
    """
    Обнаружение версий или артикулов например.
    Артикулами или версиями считаются разделители больше 2 точек 0.0.0 (если 1 точка то это дробь, например 2.1)
    """

    def repl(match):
        version = match.group().split('.')
        out_text = ''
        if len(version) > 2:
            for v in version:
                j = 0
                prefix = ''
                while v[j] == '0':
                    prefix += ' ноль '
                    j += 1
                out_text += f' {prefix} {num2words(v, lang='ru')} '
            return out_text
        return match.group()

    return re.sub(pattern=r'\b\d+(?:\.\d+)+\b', repl=repl, string=text)


def fractions_ext(text: str) -> str:
    """
    Решение проблемы с дробями. Принудительный перевод дробей в текстовый формат.
    Так как ru_normalizer не всегда корректно их выдает
    """

    def repl(match):
        original_number = match.group()
        number = original_number.replace(',', '.')
        first_part_number = number.split('.')[0]
        if len(first_part_number) > 1 and first_part_number[0] == '0':
            return original_number
        number = num2words(number, lang='ru')
        # поставить отметку о том что фильтр уже был применен, чтобы исключить модификацию другими фильтрами
        result = number
        return result

    return re.sub(pattern=rf'(\d+[,.]\d+)', repl=repl, string=text)


def zero_ext(text: str, fill: str = 'ноль') -> str:
    """
    Решение проблем ru_normalizer с нулями!
    Решение проблем с нулями для ru_normalizer.
    Проблема, нули проглатываются нормализатором, например 000 будет произнесено как `ноль`
    А `000123` будет произенесено как `сто двадцать три`.
    При этом метод должен учитывать написание чисел с пробелом, например 100 000 (здесь замена нулей не нужна)
    То есть 000 не должно быть нормализованно так как это относится к 100 т.е. выход должен быть `100 000`, что
    нормализер прочтет как `сто тысяч`, а не `сто ноль ноль ноль`.
    При этом записи вида `10 00`, не корректны с точки зрения тысячных и на выходе нужно `10 ноль ноль `
    """

    def repl(match) -> str:
        start = match.start()
        end = match.end()
        zero_count = (end - start)

        i = start
        if i != 0:

            # анализ влево, проверка относятся ли нули к тысячным разрядам
            while i >= 0:
                i -= 1
                # если пробелы, то пролистывать их
                if text[i] == ' ' or text[i] == '0':
                    continue
                else:
                    if text[i].isdigit():
                        # перед группой нулей встретилась цифра? Значит это тысячные нули не нормализовывать их
                        if zero_count == 3:
                            return match.group()
                        else:
                            break
                    else:
                        break

        insert = ' '.join([fill] * (end - start))
        insert = f' {insert} '
        return insert

    return re.sub(pattern=r'((?<!\d)0+)', repl=repl, string=text)


# конвейер расширений - порядок важен! Иначе например расширение замены дробей может повредить даты
extends = [
    (date_ext, 'нормализатор дат'),
    (version_ext, 'нормализатор версий'),
    (fractions_ext, 'нормализатор дробей'),
    (zero_ext, 'нормализатор нулей'),
]


def extension_pipeline(text: str):
    """Конвейер расширений преобразования текста перед ru_normalizer"""
    for ext in extends:
        try:
            text = ext[0](text=text)
        except Exception as err:
            message_bus.add(
                Message(
                    component='normalizer',
                    subcomponent='ru_normalizer',
                    message=f'Ошибка расширения нормализации `{ext[-1]}`: {err}',
                    level='error',
                )
            )

    return text


if __name__ == '__main__':
    assert extension_pipeline(
        text=f'21.02.2023 дата') == '  двадцать первого февраля две тысячи двадцать третьего года  дата'
    assert extension_pipeline(
        text=f'Не дата 55.02.2023') == 'Не дата   пятьдесят пять   ноль  два   две тысячи двадцать три '
    assert extension_pipeline(text=f'Артикул 21.05.130') == 'Артикул   двадцать один   ноль  пять   сто тридцать '
    assert extension_pipeline(text=f'Дробь 21.05') == 'Дробь двадцать одна целая пять сотых'
    assert extension_pipeline(text=f'Коэффициент 0.23 w') == 'Коэффициент ноль целых двадцать три сотых w'
    assert extension_pipeline(
        text=f'Завтра 22.05.2026, я буду писать приложение на Python 3.12.12.') == 'Завтра   двадцать второго мая две тысячи двадцать шестого года , я буду писать приложение на Python   три   двенадцать   двенадцать .'
    assert extension_pipeline(text=f'Сегодня 3.12.2012.') == 'Сегодня   три   двенадцать   две тысячи двенадцать .'
    assert extension_pipeline(text=f'Код доступа 000123.') == 'Код доступа  ноль ноль ноль 123.'
    assert extension_pipeline(text=f'Не путаю нули, вот код 000.') == 'Не путаю нули, вот код  ноль ноль ноль .'
    assert extension_pipeline(text=f'Сумма 22 000.') == 'Сумма 22 000.'
    assert extension_pipeline(text=f'Не сумма 22 00.') == 'Не сумма 22  ноль ноль .'
    assert extension_pipeline(
        text=f'У меня в розетке напряжение 220 000 вольт, я боюсь') == 'У меня в розетке напряжение 220 000 вольт, я боюсь'
    assert extension_pipeline(text='3/2') == '3/2'
