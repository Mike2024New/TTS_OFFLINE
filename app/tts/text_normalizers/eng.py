import re
from datetime import datetime
from num2words import num2words

__all__ = ['normalize']


def normalize(text: str, library_words: dict[str, str]):
    """Заменяет в тексте даты, числа, деньги, единицы измерения на их словесную форму."""

    for term, pronunciation in library_words.items():
        text = text.replace(term, pronunciation)

    # 1. Денежные суммы: $1,500.50 или $1,500
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

    text = re.sub(r'\$(\d{1,3}(?:,?\d{3})*(?:\.\d{1,2})?)', replace_money, text)

    # 2. Единицы измерения: 16GB, 3.5GHz, 100Mbps
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

    text = re.sub(r'(\d+(?:\.\d+)?)\s*(GB|MB|KB|TB|GHz|MHz|Mbps|Gbps|km|m|cm|mm|kg|g)\b', replace_units, text,
                  flags=re.IGNORECASE)

    # 3. Даты: DD.MM.YYYY и YYYY-MM-DD
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

    text = re.sub(r'\b\d{2}\.\d{2}\.\d{4}\b|\b\d{4}-\d{2}-\d{2}\b', replace_date, text)

    # 4. Десятичные дроби: 3.14
    def replace_float(match):
        number_str = match.group(0).replace(',', '')
        try:
            return num2words(float(number_str))
        except ValueError:
            return match.group(0)

    text = re.sub(r'\b\d{1,3}(?:,?\d{3})*\.\d+\b', replace_float, text)

    # 5. Целые числа, но не те, за которыми следует точка с цифрами
    def replace_int(match):
        number_str = match.group(0).replace(',', '')
        try:
            return num2words(int(number_str))
        except ValueError:
            return match.group(0)

    text = re.sub(r'\b\d{1,3}(?:,?\d{3})*\b(?!\.\d)', replace_int, text)

    return text


if __name__ == '__main__':
    current_library_words = {'PC': 'personal computer'}
    print(normalize(text='I have in PC', library_words=current_library_words))
    print(normalize("It costs $1,500.50", library_words=current_library_words))
    print(normalize("It costs $1.99", library_words=current_library_words))
    print(normalize("It costs $1,500", library_words=current_library_words))
    print(normalize("Today is 12.12.2023 and I bought 2,500 apples.", library_words=current_library_words))
    print(normalize("File size is 16GB and speed is 100Mbps", library_words=current_library_words))
    print(normalize("Pi is approximately 3.14", library_words=current_library_words))
