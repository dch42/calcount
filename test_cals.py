import cals
from io import StringIO


def test_to_metric():
    h, w = cals.to_metric(5, 140)
    assert h == 152.4
    assert w == 63.50
    h, w = cals.to_metric(7.4, 333)
    assert h == 223.52
    assert w == 151.05
    h, w = cals.to_metric(-1, -1)
    assert h == -30.48
    assert w == -.45


def test_validate_input(monkeypatch):
    fake_input = StringIO('5.1\n')
    monkeypatch.setattr('sys.stdin', fake_input)
    test = cals.validate_input('Float: ', float)
    assert type(test) == float
    fake_input = StringIO('1\n')
    monkeypatch.setattr('sys.stdin', fake_input)
    test = cals.validate_input('Int: ', int)
    assert type(test) == int
