import cals
from io import StringIO


def test_to_metric():
    h, w = cals.to_metric(5, 140)
    assert h, w == 152.4
    63.50

    h, w = cals.to_metric(7.4, 333)
    assert h, w == 223.52
    151.05

    h, w = cals.to_metric(-1, -1)
    assert h, w == -30.48
    -.45


def test_validate_input(monkeypatch):
    fake_input = StringIO('5.1\n')
    monkeypatch.setattr('sys.stdin', fake_input)
    test = cals.validate_input('Float: ', float)
    assert type(test) == float

    fake_input = StringIO('1\n')
    monkeypatch.setattr('sys.stdin', fake_input)
    test = cals.validate_input('Int: ', int)
    assert type(test) == int


# def test_harris_benedict():
#     h, w, a, s = 170, 68, 19, 'm'
#     bmr = cals.Profile.harris_benedict(w, h, s, a)
#     assert round(bmr, 0) == 1707

#     h, w, a, s = 120, 85, 77, 'f'
#     bmr = cals.Profile.harris_benedict(w, h, s, a)
#     assert round(bmr, 0) == 1272
