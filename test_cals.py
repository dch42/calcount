"""Tests for cals.py"""
import pytest
from io import StringIO
import cals
import sqlite3
import datetime


@pytest.fixture
def memory_db():
    """Fixture to set up an in-memory test db"""
    db = sqlite3.connect(':memory:')
    cursor = db.cursor()
    yield db, cursor


def test_Entry():
    """Verify that Entry class and add method behave as expected"""
    data = ['a', 1, (1, 2), -1, .5]
    test = cals.Entry()
    for item in data:
        test.add(item)
    assert len(test.content) == len(data)
    for i in range(0, len(data)-1):
        assert test.content[i] == data[i]


def test_CalEntry():
    """Test class CalEntry"""
    def test_add(data):
        """Add data to test obj and verify"""
        test = cals.CalEntry()
        i = 0
        for item in data:
            test.add(item)
            assert item == test.content[i]
            i += 1
    data = [['egg', 60, 6], [-2, -1, -0]]
    for i in range(len(data)):
        test_add(data[i])
    # TODO test validate method, commit, rm


def test_WeightEntry(memory_db):
    """Test class WeightEntry"""
    def test_add(data):
        """Add data to test obj and verify"""
        test = cals.WeightEntry()
        test.add(data)
        assert data == test.content[0]
        try:
            test.validate()
        except ValueError:
            pass
            check = 'fail' if type(data) is str else '?'
            assert check == 'fail'

    data = [130, -333, '', 'fish']
    for i in range(len(data)):
        test_add(data[i])


def test_create_table(memory_db, table):
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
    """Verify that append_timestamp appends as expected to array"""
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
