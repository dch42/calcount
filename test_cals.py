import cals


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
