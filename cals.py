#!/usr/bin/env python3
"""Simple script to track caloric intake and weight loss"""

import os
import sys
from datetime import datetime
import argparse
import sqlite3
#import pyfiglet
import pandas as pd
from rich.console import Console
from rich.table import Table

home = os.path.expanduser('~')
date = datetime.now().date()
today = date.strftime('%A')[:3]
time = datetime.now().time().strftime('%H:%M:%S')
ERROR = '\033[91m[ERROR]\033[00m'


db = sqlite3.connect(f"{home}/.calorie_log.db")
cursor = db.cursor()


def parse_args(args):
    """Define and parse args"""
    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description="cals -- track calories, protein, and weight loss/gain",
        epilog="""Usage examples:\n
    Add bar with 190kcal and 16g protein:
    \tcals -a 'Protein Bar' 190 16\n
    Remove the entry from previous example:
    \tcals -r 'Protein Bar' 190 16\n
    Print calorie log tables for past 3 days:
    \tcals -l 3\n
    Add a weight record of 142.7 to the table:
    \tcals -w 142.7\n
    Display weight log and total weight loss/gain:
    \tcals -w""")
    parser.add_argument(
        "--init", help="calculate TDEE and set weekly weight loss goal", action="store_true")
    parser.add_argument(
        "-z", help="use a zigzag diet instead of flat CICO", action="store_true")
    parser.add_argument(
        "-a", nargs=3, action="store", help="add a caloric entry ['food name' calories protein]")
    parser.add_argument(
        "-r", nargs=3, action="store", help="remove a caloric entry ['food name' calories protein]")
    parser.add_argument(
        "-l", nargs="?", const=1, help='list calorie info for day(s)')
    parser.add_argument(
        "-w", nargs="?", type=float, const=1, help='input weight into weight log')
    parser.add_argument(
        "-x", help="export calorie history to csv", action="store_true")

    return parser.parse_args()


class Entry:
    """
    A class to represent a bundle of data to be added to db
    ...
    Attributes
    ----------
    content : list
        array of items to be commited to/removed from db
    Methods
    -------
    add(item):
        Adds item to content list
    """

    def __init__(self):
        self.content = []

    def add(self, item):
        """Add item to entry content array"""
        self.content.append(item)


class CalEntry(Entry):
    """
    Entry subclass to represent caloric log record
    ...
    Methods
    -------
    validate():
        Validate caloric log record for addition or removal
    commit_cals():
        Commits caloric intake record to db
    remove_cals():
        Removes caloric record from db
    """

    def validate(self):
        """Validate caloric log record for addition or removal"""
        option = 'a' if args.a else 'r'
        usage = f"Usage: cals -{option} 'protein bar' 200 20"
        assert len(self.content) == 3, f"{usage}"
        for n in 1, 2:
            self.content[n] = int(self.content[n])
            assert type(self.content[n]) == int, f"{usage}"

    def commit_cals(self):
        """Commit caloric intake record to db"""
        self.validate()
        record = append_timestamp(self.content)
        with db:
            create_table(db, cursor, 'calorie_table')
            cursor.executemany("INSERT INTO calorie_table VALUES (?,?,?,?,?)",
                               (record, ))
            db.commit()

    def remove_cals(self):
        """Remove caloric intake record from db"""
        self.validate()
        with db:
            try:
                cursor.execute(
                    f"DELETE FROM calorie_table WHERE Date='{date}' AND Food_Name='{self.content[0]}' \
                    AND Calories='{self.content[1]}' AND Protein='{self.content[2]}'")
            except sqlite3.OperationalError as err:
                print(f"{ERROR} {err}")


class WeightEntry(Entry):
    """
    Entry subclass to represent weight data to be added to db
    ...
    Methods
    -------
    validate():
        Validate weight log entry for addition to table
    commit_weight():
        Commits weight entry to db
    """

    def validate(self):
        """Validate weight log entry for addition to table"""
        usage = "Usage: cals -w 175"
        assert len(self.content) == 1 and \
            type(float(self.content[0])) == float, f"{usage}"

    def commit_weight(self):
        """Commit weight data to db"""
        self.validate()
        record = append_timestamp(self.content)
        with db:
            create_table(db, cursor, 'weight_table')
            cursor.executemany(
                "INSERT INTO weight_table VALUES (?,?,?)", (record, ))
            db.commit()


class ProfileEntry(Entry):
    """
    Entry subclass to represent calorie goal info to be added to db
    ...
    Methods
    -------
    validate():
        Validate profile data for addition to table
    commit_profile():
        Commit profile record to db
    """

    def validate(self):
        """Validate weight log entry for addition to table"""
        assert len(self.content) == 10

    def commit_profile(self):
        """Commit calorie goal info to db"""
        record = append_timestamp(self.content)
        self.validate()
        with db:
            cursor.execute("DROP TABLE IF EXISTS profile_table")
            create_table(db, cursor, 'profile_table')
            cursor.executemany(
                "INSERT INTO profile_table VALUES (?,?,?,?,?,?,?,?,?,?)", (record, ))


class Profile:
    """
    A class to represent user profile data for calculations
    ...
    Attributes
    ----------
    age : int
        Age of user in years
    sex : str
        Sex of user (m/f)
    height : float
        Height of user, feet.inches. Ex: 5'6" == 5.6
    weight : float
        Weight of user in lbs
    lose : float
        Amount of weight to lose per week in lbs
    bmr : int
        Basal Metabolic Rate
    tdee : int
        Total Daily Energy Expenditure
    Methods
    -------
    harris_benedict():
        Calculate BMR using Harris-Benedict equation
    calc_tdee():
        Calculate TDEE from BMR
    """

    def __init__(self, age, sex, height, weight, lose):
        self.age = age
        self.sex = sex
        self.height = height
        self.weight = weight
        self.lose = lose
        self.bmr = self.harris_benedict()
        self.tdee = self.calc_tdee()

    def harris_benedict(self):
        """Calculate BMR using Harris-Benedict equation"""
        nums = [88.362, 13.397, 4.799, 5.677] if self.sex == 'm' else [
            447.593, 9.247, 3.098, 4.330]
        print("\nCalculating basal metabolic rate (BMR)...")
        bmr = (nums[0] + (nums[1]*self.weight) +
               (nums[2]*self.height) - (nums[3]*self.age))
        print(
            f"\nResults:\n\n\tBMR: ~{int(bmr)} calories")
        return bmr

    def calc_tdee(self):
        """Calculate TDEE from BMR and activity multiplier"""
        print("\nAverage Daily Activity Level:\n")
        # activity levels and multipliers for tdee

        activity = {
            '1': ["sedentary (little or no exercise)", 1.2],
            '2': ["light activity (light exercise/sports 1 to 3 days per week)", 1.375],
            '3': ["moderate activity (moderate exercise/sports 3 to 5 days per week)", 1.55],
            '4': ["very active (hard exercise/sports 6 to 7 days per week)", 1.725],
            '5': ["extra active (very hard exercise/sports 6 to 7 days per week and physical job)", 1.9]
        }
        for k in activity:
            print(k, ": ", activity[k][0])
        print("\n")
        multiplier = input(
            "Please enter the option that most closely resembles your average activity level (1-5): ")
        print("Calculating total daily energy expenditure (TDEE)...")
        tdee = self.bmr*float(activity[multiplier][1])
        print(
            f"\nResults:\n\n\tTDEE: ~{int(tdee)} calories\n")
        return tdee

    def calc_goal(self):
        """Calculate caloric goal from TDEE"""
        goal = self.tdee - (self.lose*500)
        print(
            f"To lose {self.lose} lbs/week, you will need to consume {int(goal)} calories/day.\
                \nGood luck!\n")
        return goal


class Diet:
    """
    A class to represent CICO diet
    ...
    Attributes
    ----------
    tdee : int
        Total Daily Energy Expenditure
    to_lose : int
        Amount of weight to lose per week in lbs
    calories : int
        Calories to consume per day to lose $to_lose
    """

    def __init__(self, tdee, to_lose):
        self.tdee = tdee
        self.to_lose = to_lose
        self.calories = tdee-(to_lose*500)


class ZigZag(Diet):
    """
    Diet subclass, ZigZag diet
    ...
    Methods
    ----------
    calc_zigzag()
        Spreads caloric deficit across the week in zigzag fashion
    """

    def calc_zigzag(self):
        weekly_plan = [self.calories] * 7
        for i in range(0, 6):
            if not i % 2:
                weekly_plan[i] *= .75
            else:
                weekly_plan[i] *= 1.25
            if i in (1, 2):
                weekly_plan[i] *= .9
            if i in (3, 4):
                weekly_plan[i] *= 1.1
        return weekly_plan

# caloric logs


def calc_cals(day):
    """Calculate calorie and protein totals for $day"""
    with db:
        info = []
        for col in ['Calories', 'Protein']:
            i = 0
            cursor.execute(
                f"SELECT {col} FROM calorie_table WHERE Date='{day}'")
            rows = cursor.fetchall()
            for row in rows:
                i = i + row[0]
            info.append(i)
        cals, protein = info[0], info[1]
        return cals, protein


def fetch_goal(day):
    """Fetch most recent caloric goals from db"""
    with db:
        cursor.execute(
            f"SELECT {day} FROM profile_table ORDER BY Date ASC")
        goal = cursor.fetchall()[-1][0]
        return goal


def print_days(num):
    """Print multiple caloric logs"""
    with db:
        try:
            cursor.execute(
                f"SELECT DISTINCT Date FROM calorie_table ORDER BY Date DESC LIMIT {num}")
            days = cursor.fetchall()
            # loop backwards through days
            for day in days[::-1]:
                print_daily_log(day[0])
        except sqlite3.OperationalError as err:
            print(f"{ERROR} {err}\n\tNo calorie data to display.\n\
\tFirst, please enter a food item to the table: \n`cals -a 'food' cals protein`")


def print_daily_log(day):
    """Print caloric log for $day"""
    try:
        with db:
            cursor.execute(
                f"SELECT Food_Name, Calories, Protein, Date FROM calorie_table WHERE Date='{day}'")
            rows = cursor.fetchall()
            try:
                weekday = datetime.strptime(
                    f'{rows[0][3]}', '%Y-%m-%d').strftime('%A')[:3]
            except IndexError:
                # prevent failure on empty table
                weekday = today
                pass
            cal_table = Table(title=f"Calorie Log: {weekday} {day}")
            for col in 'Food', 'Calories', 'Protein':
                cal_table.add_column(f"{col}", justify="right", no_wrap=True)
            for row in rows[:-1]:
                cal_table.add_row(f"{row[0]}", f"{row[1]}kcal", f"{row[2]}g")
            try:
                # style entry if just added
                cal_table.add_row(
                    f"{'+' if args.a else ''}{rows[-1][0]}", f"{rows[-1][1]}kcal",
                    f"{rows[-1][2]}g", style=f"{'green' if args.a else ''}")
            except IndexError:
                # prevent failure on empty table
                pass
            print('\n')
            console = Console()
            console.print(cal_table)
            cals, protein = calc_cals(day)
            calorie_limit = fetch_goal(weekday)
            calories_remaining = round(calorie_limit-cals)
            if calories_remaining >= 0:
                over_under = 'remaining'
            else:
                calories_remaining = abs(calories_remaining)
                over_under = 'over'
            print(f"Total: {cals} calories / {protein}g protein \
                        \n{calories_remaining} calories {over_under}\n")
    except sqlite3.OperationalError as err:
        print(f"{ERROR} {err}\n\tNo calorie data to display.\n\
\tFirst, please enter a food item to the table: `cals -a 'food' cals protein`")


# weight logs


def display_weight_table():
    """Fetch weight data from db and display table with weight progress"""
    weight_log = Table(title="Weight Log")
    for col in 'Date', 'Weight':
        weight_log.add_column(f"{col}", justify="right", no_wrap=True)
    with db:
        try:
            cursor.execute(
                "SELECT Date, Weight FROM weight_table ORDER BY Date ASC")
            weights = cursor.fetchall()
            for row in weights:
                weight_log.add_row(f"{row[0]}", f"{row[1]}")
            print('\n')
            console = Console()
            console.print(weight_log)
            lost = round(calc_weight_loss(), 2)
            if lost < 0:
                print(f"\nRecorded gain: {abs(lost)} lbs\n")
            else:
                print(f"\nRecorded loss: {lost} lbs\n")
        except sqlite3.OperationalError as err:
            print(f"{ERROR} {err}\n\tNo weight data to display.\n\
\tFirst, please enter a weight to the table: `cals -w weight`")


def calc_weight_loss():
    """Calculate difference between first recorded weight and last recorded weight"""
    with db:
        cursor.execute(
            "SELECT Weight FROM weight_table ORDER BY Date, Time")
        weights = cursor.fetchall()
        weight_loss = weights[0][0] - weights[-1][0]
        return weight_loss

# db


def create_table(db, cursor, table):
    """Create $table if not exists"""
    with db:
        if table == 'calorie_table':
            cursor.execute("""CREATE TABLE IF NOT EXISTS calorie_table(
                Food_Name TEXT,
                Calories INTEGER,
                Protein INTEGER,
                Time TEXT,
                Date TEXT)
                """)
        elif table == 'weight_table':
            cursor.execute("""CREATE TABLE IF NOT EXISTS weight_table(
                Weight INTEGER,
                Time TEXT,
                Date TEXT)
                """)
        elif table == 'profile_table':
            cursor.execute("""CREATE TABLE IF NOT EXISTS profile_table(
                Lose INTEGER,
                Mon INTEGER,
                Tue INTEGER,
                Wed INTEGER,
                Thu INTEGER,
                Fri INTEGER,
                Sat INTEGER,
                Sun INTEGER,
                Time TEXT,
                Date TEXT)
                """)
        else:
            print(f"{ERROR} No table to create: {table}")


def export_cals(db):
    """Convert calorie table to pandas df and export to csv"""
    try:
        calorie_df = pd.read_sql_query("SELECT * FROM calorie_table", db)
        calorie_df.to_csv(
            f'./calorie_logs-{date}-{time}.csv', index=False)
        print(
            f"Exported calorie logs to './calorie_logs-{date}-{time}.csv'")
    except Exception as err:
        print(f"{ERROR} Export failed: {err}\033[0m")


def logo():
    """Print script logo"""
    pyfiglet.print_figlet("CalCount")
    print("Keep track of calories, protein, and weight loss/gain.\n")


def get_profile():
    """Get profile info from user input and commit weight to db"""
    age = validate_input("Please enter your age: ", int)
    sex = ''
    while sex not in ['m', 'f']:
        sex = validate_input("Please enter your sex (m/f): ", str)
    height = validate_input(
        "Please enter your height (feet.inches): ", float)
    weight = validate_input("Please enter your weight (lbs): ", float)
    lose = validate_input(
        "Please enter desired weight loss per week (lbs): ", float)

    # convert to metric for calculations
    height, weight = to_metric(height, weight)

    # enter initial weight data to db
    record = WeightEntry()
    record.add(weight)
    record.commit_weight()

    return age, sex, height, weight, lose


def append_timestamp(arr):
    """Append time and date to array"""
    for item in time, date:
        arr.append(item)
    return arr


def validate_input(prompt, dtype):
    """Ensure user input for $prompt matches datatype $type"""
    good = False
    while not good:
        val = input(prompt)
        try:
            test = dtype(val)
            good = True
            return test
        except ValueError as err:
            print(f"{ERROR} Please ensure input matches datatype `{dtype}`.\n{err}")


def to_metric(ft_in, lbs):
    """Convert imperial height/weight to metric"""
    cm = round((((ft_in//1)*12+((ft_in % 1)*10))*2.54), 2)
    kg = round(lbs*0.45359237, 2)
    return cm, kg


def print_cal_plan():
    """Print weekly calorie plan"""
    table = Table(title="Weekly Plan")
    for col in 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun':
        table.add_column(f"{col}", justify="right", no_wrap=True)
    with db:
        cursor.execute(
            f"SELECT Mon, Tue, Wed, Thu, Fri, Sat, Sun FROM profile_table ORDER BY Date DESC")
        plan = list(cursor.fetchall()[0])
        for i in range(len(plan)):
            plan[i] = round(plan[i])
    table.add_row(f"{plan[0]}", f"{plan[1]}", f"{plan[2]}",
                  f"{plan[3]}", f"{plan[4]}", f"{plan[5]}", f"{plan[6]}")
    print('\n')
    console = Console()
    console.print(table)


if __name__ == '__main__':
    args = parse_args(sys.argv[1:])
    if args.init:
        logo()
        user_data = get_profile()
        profile = Profile(*user_data)
        record = ProfileEntry()
        if args.z:
            diet = ZigZag(profile.tdee, profile.lose)
            cal_arr = diet.calc_zigzag()
        else:
            diet = Diet(profile.tdee, profile.lose)
            cal_arr = [diet.calories] * 7
        items = [profile.lose] + cal_arr
        for item in items:
            record.add(item)
        record.commit_profile()
    if args.a or args.r:
        print_cal_plan()
        record = CalEntry()
        food = args.a if args.a else args.r
        for arg in food:
            record.add(arg)
        if args.a:
            record.commit_cals()
        elif args.r:
            record.remove_cals()
        print_daily_log(date)
    if args.l:
        print_cal_plan()
        if int(args.l) > 1:
            print_days(int(args.l))
        else:
            print_daily_log(date)
    if args.w:
        if int(args.w) > 1:
            record = WeightEntry()
            record.add(args.w)
            record.commit_weight()
        else:
            display_weight_table()
    if args.x:
        export_cals(db)
