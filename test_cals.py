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


def test_harris_benedict(monkeypatch):
    data = (19, 'm', 170, 68, 2)
    fake_input = StringIO('1\n')
    monkeypatch.setattr('sys.stdin', fake_input)
    test_prof = cals.Profile(*data)
    assert round(test_prof.bmr, 0) == 1707

    data = (77, 'f', 120, 85, 2)
    fake_input = StringIO('1\n')
    monkeypatch.setattr('sys.stdin', fake_input)
    test_prof = cals.Profile(*data)
    assert round(test_prof.bmr, 0) == 1272

def test_calc_tdee(monkeypatch):
    data = (33, 'm', 99.06, 14.97, 3)
    fake_input = StringIO('1\n')
    monkeypatch.setattr('sys.stdin', fake_input)
    test_prof = cals.Profile(*data)
    assert round(test_prof.tdee, 0) == 692

    data = (33, 'm', 99.06, 14.97, 2)
    fake_input = StringIO('3\n')
    monkeypatch.setattr('sys.stdin', fake_input)
    test_prof = cals.Profile(*data)
    assert round(test_prof.tdee, 0) == 894

def test_calc_goal(monkeypatch):
    data = (33, 'm', 99.06, 14.97, 2)
    fake_input = StringIO('3\n')
    monkeypatch.setattr('sys.stdin', fake_input)
    test_prof = cals.Profile(*data)
    assert int(test_prof.goal) == -105
