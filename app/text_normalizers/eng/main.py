from app.text_normalizers.eng.extends import extension_pipeline

__all__ = ['normalize']


def normalize(text: str, library_words: dict[str, str] | None = None) -> str:
    """Заменяет в тексте даты, числа, деньги, единицы измерения на их словесную форму."""
    library_words = library_words or {}
    # замена слов из словаря library_words, например "PC" -> "personal computer"
    for term, pronunciation in library_words.items():
        text = text.replace(term, pronunciation)

    # подключаемые к нормализатору расширения extends
    text = extension_pipeline(text)
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
