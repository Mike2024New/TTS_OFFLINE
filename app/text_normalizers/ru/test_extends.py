from app.text_normalizers.ru.extends import extension_pipeline


def test_extends():
    """Тесты что всё в порядке ни чего не отвалилось"""
    assert extension_pipeline(text='0') == ' ноль '
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