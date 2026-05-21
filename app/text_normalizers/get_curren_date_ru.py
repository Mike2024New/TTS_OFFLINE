from datetime import datetime


def get_current_date_ru():
    """Получение точного времени сейчас на русском языке"""

    def plural_form(n: int, forms: tuple[str, str, str]) -> str:
        n = abs(n) % 100
        if 11 <= n <= 19:
            return forms[2]
        n = n % 10
        if n == 1:
            return forms[0]
        elif 2 <= n <= 4:
            return forms[1]
        else:
            return forms[2]

    current_time = datetime.now()
    date = f'{current_time.day}.{current_time.month}.{current_time.year}'

    hours = current_time.hour
    minutes = current_time.minute
    hours_word = plural_form(hours, ('час', 'часа', 'часов'))
    minutes_word = plural_form(minutes, ('минута', 'минуты', 'минут'))
    time_str = f'{hours} {hours_word} {minutes} {minutes_word}'

    return f'Сегодня {date}, точное время {time_str}'
