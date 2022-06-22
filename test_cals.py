"""Tests for cals.py"""
import pytest
from io import StringIO
import cals
import sqlite3
import datetime


@pytest.fixture
def memory_db():
    """Fixture to set up an in-memory db for testing"""
    db = sqlite3.connect(':memory:')
    cursor = db.cursor()
    yield db, cursor


def test_create_table(memory_db):
    """Test table creation"""
    db, cursor = memory_db
    tables = ['calorie_table', 'weight_table',
              'profile_table']
    bogus = [42, 'nope', (0, 1, 2)]

    def create_table(table):
        """Create table and return results"""
        cals.create_table(db, cursor, f'{table}')
        with db:
            check = list(cursor.execute(
                f"""SELECT * FROM {table}""").fetchall())
        return check

    for table in tables:
        check = create_table(table)
        assert check == []
    for table in bogus:
        try:
            check = create_table(table)
        except sqlite3.OperationalError:
            check = 'fail'
        assert check == 'fail'


def test_append_timestamp():
    def append_timestamp(arr):
        arr = cals.append_timestamp(arr)
        return arr
    arrs = [[0], [0, 2], ['str', 4, ['nest']]]
    for init_arr in arrs:
        init_len = len(init_arr)
        arr = append_timestamp(init_arr)
        assert len(arr) == init_len + 2
        assert type(arr[-2]) is str
        assert type(arr[-1]) is datetime.date


def test_to_metric():
    """Verify that to_metric converts imperial units to metric"""
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
    """Verify that validate_input returns expected datatypes"""
    fake_input = StringIO('5.1\n')
    monkeypatch.setattr('sys.stdin', fake_input)
    test = cals.validate_input('Float: ', float)
    assert type(test) == float

    fake_input = StringIO('1\n')
    monkeypatch.setattr('sys.stdin', fake_input)
    test = cals.validate_input('Int: ', int)
    assert type(test) == int


def test_harris_benedict(monkeypatch):
    """Verify that harris_benedict method returns expected BMR values"""
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
    """Verify that calc_tdee method returns expected TDEE values"""
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
    """Verify that calc_goal method returns expected caloric deficit values"""
    data = (33, 'm', 99.06, 14.97, 2)
    fake_input = StringIO('3\n')
    monkeypatch.setattr('sys.stdin', fake_input)
    test_prof = cals.Profile(*data)
    diet = cals.Diet(test_prof.tdee, test_prof.lose)
    assert int(diet.calories) == -105
