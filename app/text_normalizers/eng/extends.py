import re
from app import message_bus, Message
from num2words import num2words
from datetime import datetime

__all__ = ['extension_pipeline']


def money_ext(text: str) -> str:
    """
    Денежные суммы: $1,500.50 или $1,500
    """

    def replace_money(match):
        amount_str = match.group(1).replace(',', '')

        if '.' in amount_str:
            # Сумма с центами: $1,500.50
            parts = amount_str.split('.')
            dollars = int(parts[0])
            # Центов всегда две цифры (или одна, тогда дополняем)
            cents_str = parts[1]
            if len(cents_str) == 1:
                cents_str += '0'
            cents = int(cents_str)

            dollars_words = num2words(dollars)
            cents_words = num2words(cents)

            # Правильное склонение: dollar/dollars, cent/cents
            dollar_label = "dollar" if dollars == 1 else "dollars"
            cent_label = "cent" if cents == 1 else "cents"

            return f"{dollars_words} {dollar_label} and {cents_words} {cent_label}"
        else:
            # Целая сумма: $1,500
            dollars = int(amount_str)
            dollars_words = num2words(dollars)
            dollar_label = "dollar" if dollars == 1 else "dollars"
            return f"{dollars_words} {dollar_label}"

    return re.sub(r'\$(\d{1,3}(?:,?\d{3})*(?:\.\d{1,2})?)', replace_money, text)


def units_ext(text: str) -> str:
    """Единицы измерения: 16GB, 3.5GHz, 100Mbps"""

    def replace_units(match):
        number_str = match.group(1).replace(',', '')
        unit = match.group(2)
        try:
            if '.' in number_str:
                words = num2words(float(number_str))
            else:
                words = num2words(int(number_str))
        except ValueError:
            return match.group(0)

        unit_words = {
            'GB': 'gigabytes', 'MB': 'megabytes', 'KB': 'kilobytes', 'TB': 'terabytes',
            'GHz': 'gigahertz', 'MHz': 'megahertz',
            'Mbps': 'megabits per second', 'Gbps': 'gigabits per second',
            'km': 'kilometers', 'm': 'meters', 'cm': 'centimeters', 'mm': 'millimeters',
            'kg': 'kilograms', 'g': 'grams',
        }
        unit_word = unit_words.get(unit, unit)
        return f"{words} {unit_word}"

    return re.sub(r'(\d+(?:\.\d+)?)\s*(GB|MB|KB|TB|GHz|MHz|Mbps|Gbps|km|m|cm|mm|kg|g)\b', replace_units, text,
                  flags=re.IGNORECASE)


def date_ext(text: str) -> str:
    def replace_date(match):
        date_str = match.group(0)
        for fmt, pattern in [("%d.%m.%Y", r'\d{2}\.\d{2}\.\d{4}'),
                             ("%Y-%m-%d", r'\d{4}-\d{2}-\d{2}')]:
            if re.match(pattern, date_str):
                try:
                    dt_obj = datetime.strptime(date_str, fmt)
                    day = num2words(dt_obj.day, to='ordinal')
                    month = dt_obj.strftime('%B')
                    year = num2words(dt_obj.year, to='year')
                    return f"{month} the {day}, {year}"
                except ValueError:
                    return date_str
        return date_str

    return re.sub(r'\b\d{2}\.\d{2}\.\d{4}\b|\b\d{4}-\d{2}-\d{2}\b', replace_date, text)


def float_ext(text: str) -> str:
    """Десятичные дроби: 3.14"""

    def replace_float(match):
        number_str = match.group(0).replace(',', '')
        try:
            return num2words(float(number_str))
        except ValueError:
            return match.group(0)

    return re.sub(r'\b\d{1,3}(?:,?\d{3})*\.\d+\b', replace_float, text)


def int_ext(text: str) -> str:
    """Целые числа, но не те, за которыми следует точка с цифрами"""

    def replace_int(match):
        number_str = match.group(0).replace(',', '')
        try:
            return num2words(int(number_str))
        except ValueError:
            return match.group(0)

    return re.sub(r'\b\d{1,3}(?:,?\d{3})*\b(?!\.\d)', replace_int, text)


extends = [
    (money_ext, 'money normalizer'),
    (units_ext, 'units normalizer'),
    (date_ext, 'date normalizer'),
    (float_ext, 'float normalizer'),
    (int_ext, 'int normalizer'),
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
                    subcomponent='eng_normalizer',
                    message=f'Ошибка расширения нормализации `{ext[-1]}`: {err}',
                    level='error',
                )
            )

    return text


if __name__ == '__main__':
    pass
