import pytest

@pytest.fixture
def ai():
    import ai
    return ai


rozumne_vyjimky = ValueError, TypeError


def test_empty(ai):
    """Hra na prázdné pole"""
    for symbol in 'ox':
        result = ai.tah_pocitace('-' * 20, symbol)
        assert len(result) == 20, result + ': Špatná délka pole'
        assert result.count('-') == 19, result + ': Špatný počet pomlček'
        assert result.count(symbol) == 1, result + ': Špatný počet symbolů ' + symbol


def test_full(ai):
    """Hra na plné pole"""
    for symbol in 'ox':
        with pytest.raises(rozumne_vyjimky):
            result = ai.tah_pocitace('x' * 20, symbol)


def test_short(ai):
    """Hra na krátké pole"""
    for symbol in 'ox':
        result = ai.tah_pocitace('-' * 5, symbol)
        assert len(result) == 5
        assert result.count('-') == 4, result + ': Špatný počet pomlček'
        assert result.count(symbol) == 1, result + ': Špatný počet symbolů ' + symbol


def test_long(ai):
    """Hra na dlouhé pole"""
    for symbol in 'ox':
        result = ai.tah_pocitace('-' * 100, symbol)
        assert len(result) == 100, 'Špatná délka pole'
        assert result.count('-') == 99, 'Špatný počet pomlček'
        assert result.count(symbol) == 1, 'Špatný počet symbolů ' + symbol


def test_zero(ai):
    """Hra na pole nulové délky"""
    for symbol in 'ox':
        with pytest.raises(rozumne_vyjimky):
            result = ai.tah_pocitace('', symbol)


def test_almost_full(ai):
    """Hra na skoro plné pole (volno uprostřed)"""
    pole = 'xoxoxoxoxo-xoxoxoxox'
    result = ai.tah_pocitace(pole, 'o')
    assert len(result) == 20, result + ': Špatná délka pole'
    assert result.count('x') == 10, result + ': Špatný počet symbolů x'
    assert result.count('o') == 10, result + ': Špatný počet symbolů o'


def test_almost_full_beginning(ai):
    """Hra na skoro plné pole (volno na začátku)"""
    pole = '-xoxoxoxoxoxoxoxoxox'
    result = ai.tah_pocitace(pole, 'o')
    assert len(result) == 20, result + ': Špatná délka pole'
    assert result.count('x') == 10, result + ': Špatný počet symbolů x'
    assert result.count('o') == 10, result + ': Špatný počet symbolů o'


def test_almost_full_end(ai):
    """Hra na skoro plné pole (volno na konci)"""
    pole = 'xoxoxoxoxoxoxoxoxox-'
    result = ai.tah_pocitace(pole, 'o')
    assert len(result) == 20, result + ': Špatná délka pole'
    assert result.count('x') == 10, result + ': Špatný počet symbolů x'
    assert result.count('o') == 10, result + ': Špatný počet symbolů o'

def test_almost_full_end(ai):
    """Hra na skoro plné pole (2× volno na konci)"""
    pole = 'xooxxooxoxoxoxooxx--'
    result = ai.tah_pocitace(pole, 'x')
    assert len(result) == 20, result + ': Špatná délka pole'
    assert result.count('x') == 10, result + ': Špatný počet symbolů x'
    assert result.count('o') == 9, result + ': Špatný počet symbolů o'
