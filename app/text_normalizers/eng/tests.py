from app.text_normalizers.eng.main import normalize
from app.text_normalizers.eng.extends import extension_pipeline


def test_normalizer_and_extends():
    assert normalize(text='I want that cup of coffee for $1') == 'I want that cup of coffee for one dollar'
    assert normalize(text='It costs $1,500.50') == 'It costs one thousand, five hundred dollars and fifty cents'
    assert normalize(text='It costs $1.99') == 'It costs one dollar and ninety-nine cents'
    assert normalize(text='It costs $1,500') == 'It costs one thousand, five hundred dollars'
    assert normalize(
        text='Today is 12.12.2023 and I bought 2,500 apples.') == 'Today is December the twelfth, twenty twenty-three and I bought two thousand, five hundred apples.'
    assert normalize(
        text='File size is 16GB and speed is 100Mbps') == 'File size is sixteen gigabytes and speed is one hundred megabits per second'
    assert normalize(text='Pi is approximately 3.14') == 'Pi is approximately three point one four'
    assert normalize(text='I have in PC', library_words={'PC': 'personal computer'}) == 'I have in personal computer'


def test_only_extends():
    assert extension_pipeline(text='3.2') == 'three point two'
    assert extension_pipeline(text='0.05') == 'zero point zero five'
    assert extension_pipeline(text='100 GB') == 'one hundred gigabytes'
    assert extension_pipeline(text='$3,000') == 'three thousand dollars'
    assert extension_pipeline(text='3201 dollars') == 'three thousand, two hundred and one dollars'
    assert extension_pipeline(text='99999') == 'ninety-nine thousand, nine hundred and ninety-nine'


if __name__ == '__main__':
    test_normalizer_and_extends()
    test_only_extends()
