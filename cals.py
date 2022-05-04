#!/usr/bin/env python3
"""Simple script to track caloric intake and weight loss"""

import os
from datetime import datetime
import argparse
import sqlite3
import pyfiglet
from rich.console import Console
from rich.table import Table

home = os.path.expanduser('~')
date = datetime.now().date()
time = datetime.now().time().strftime('%H:%M:%S')

db = sqlite3.connect(f"{home}/.calorie_log.db")
cursor = db.cursor()

# activity levels and multipliers for tdee
activity = {
    '1': ["sedentary (little or no exercise)", 1.2],
    '2': ["light activity (light exercise/sports 1 to 3 days per week)", 1.375],
    '3': ["moderate activity (moderate exercise/sports 3 to 5 days per week)", 1.55],
    '4': ["very active (hard exercise/sports 6 to 7 days per week)", 1.725],
    '5': ["extra active (very hard exercise/sports 6 to 7 days per week and physical job)", 1.9]
}


# define and parse args
parser = argparse.ArgumentParser(
    description="Track caloric intake")
parser.add_argument(
    "--init", help="answer questions to calculate TDEE and set caloric goals", action="store_true")
parser.add_argument(
    "-a", "--add", nargs=3, action="store", help="add a caloric entry ['food name' calories protein],\
        \nEx: -a 'Protein Bar' 190 16")
parser.add_argument(
    "-l", "--list", nargs="?", const=1, help='list calorie info for day(s)')
parser.add_argument(
    "-w", "--weight", nargs="?", type=float, const=1, help='input weight into weight log')

args = parser.parse_args()


def logo():
    """Print script logo"""
    pyfiglet.print_figlet("CalCount")


def validate_input(prompt, type):
    """Ensure user input for $prompt matches datatype $type"""
    ok = False
    while not ok:
        val = input(prompt)
        try:
            test = type(val)
            ok = True
            return test
        except ValueError as error:
            print(f"ValueError: {error}")

# tdee/bmr


def get_profile():
    """Collect input for user profile and calculations"""
    print("Please answer the following questions.\nThey will be used to calculate your BMR, TDEE, and caloric deficit required to reach your weight loss goal.\n")
    age = validate_input("Please enter your age: ", int)
    sex = validate_input("Please enter your sex (m/f): ", str)
    height = validate_input("Please enter your height (feet.inches): ", float)
    weight = validate_input("Please enter your weight (lbs): ", float)
    lose = validate_input(
        "Please enter desired weight loss per week (lbs): ", float)
    height, weight = to_metric(height, weight)
    return age, sex, height, weight, lose


def to_metric(height, weight):
    """Convert imperial height/weight to metric"""
    height = (((height//1)*12+((height % 1)*10))*2.54)
    weight = weight*0.45359237
    return height, weight


def harris_benedict(weight, height, sex, age):
    """Calculate BMR using Harris-Benedict equation"""
    bmr = ((weight*10) + (6.25*height) + (5*age))
    if sex == 'm':
        bmr += 5
    else:
        bmr -= 161
    return bmr


def calc_tdee(bmr):
    """Calculate TDEE from BMR and activity multiplier"""
    print("\nAverage Daily Activity Level:\n")
    for k in activity:
        print(k, ": ", activity[k][0])
    print("\n")
    multiplier = input(
        "Please enter the option that most closely resembles your average activity level (1-5): ")
    tdee = bmr*float(activity[multiplier][1])
    return tdee


def tdee_to_goal():
    """Calculate caloric goal from TDEE"""
    age, sex, height, weight, lose = get_profile()
    print("\nCalculating basal metabolic rate (BMR)...")
    bmr = harris_benedict(weight, height, sex, age)
    print("Calculating total daily energy expenditure (TDEE)...")
    tdee = calc_tdee(bmr)
    goal = tdee - (lose*500)
    print(
        f"\nResults:\n\n\tBMR: ~{int(bmr)} calories\n\tTDEE: ~{int(tdee)} calories\n")
    print(
        f"To lose {lose} lbs/week, you will need to consume {int(goal)} calories/day.\
            \nGood luck!\n")
    return lose, goal, time, date


def commit_goal(goal):
    """Commit goal data to db"""
    cursor.execute("""CREATE TABLE IF NOT EXISTS goal_table(
        Lose INTEGER,
        Goal INTEGER,
        Time TEXT,
        Date TEXT)
        """)
    cursor.executemany(
        "INSERT INTO goal_table VALUES (?,?,?,?)", (goal, ))
    db.commit()

# weight log


def commit_weight(weight):
    """Commit weight data to db"""
    entry = [weight,
             time,
             date
             ]
    cursor.execute("""CREATE TABLE IF NOT EXISTS weight_table(
        Weight INTEGER,
        Time TEXT,
        Date TEXT)
        """)
    cursor.executemany(
        "INSERT INTO weight_table VALUES (?,?,?)", (entry, ))
    db.commit()


def display_weight():
    """Fetch weight data from db and display table with weight progress"""
    weight_log = Table(title=f"Weight Log")
    weight_log.add_column("Date", justify="right", no_wrap=True)
    weight_log.add_column("Weight", justify="right", no_wrap=True)
    with db:
        try:
            cursor.execute(
                "SELECT Date, Weight FROM weight_table ORDER BY Date DESC")
            weights = cursor.fetchall()
            for row in weights:
                weight_log.add_row(f"{row[0]}", f"{row[1]}")
            print('\n')
            console = Console()
            console.print(weight_log)
            lost = calc_weight_loss()
            if lost < 0:
                print(f"\nRecorded gain: {abs(lost)} lbs\n")
            else:
                print(f"\nRecorded loss: {lost} lbs\n")
        except sqlite3.OperationalError as error:
            print(f"\033[91m[ERROR]\033[00m {error}\n\tNo weight data to display.\n\
\tFirst, please enter a weight to the table: `cals -w weight`")


def calc_weight_loss():
    """Calculate difference between first recorded weight and last recorded weight"""
    with db:
        cursor.execute(
            "SELECT Weight FROM weight_table ORDER BY Date, Time ASC LIMIT 1")
        start_weight = cursor.fetchone()
        cursor.execute(
            "SELECT Weight FROM weight_table ORDER BY Date, Time DESC LIMIT 1")
        current_weight = cursor.fetchone()
        weight_loss = float(start_weight[0]) - float(current_weight[0])
        return weight_loss


# calorie log


def fetch_goal():
    """Fetch most recent caloric goals from db"""
    with db:
        cursor.execute(
            "SELECT Lose, Goal FROM goal_table ORDER BY Date")
        to_lose, goal = cursor.fetchone()
        return to_lose, goal


def validate_entry():
    """Validate and build caloric log entry"""
    if str(args.add[1:]).isdigit:
        entry = [
            str(args.add[0]),
            int(args.add[1]),
            int(args.add[2]),
            str(time),
            str(date)
        ]
        return entry


def commit_entry(entry):
    """Insert food entry info into database"""
    cursor.execute("""CREATE TABLE IF NOT EXISTS calorie_table(
        Food_Name TEXT,
        Calories INTEGER,
        Protein INTEGER,
        Time TEXT,
        Date TEXT)
        """)
    cursor.executemany(
        "INSERT INTO calorie_table VALUES (?,?,?,?,?)", (entry, ))
    db.commit()


def print_days(num):
    """Print multiple caloric logs"""
    with db:
        cursor.execute(
            f"SELECT DISTINCT Date FROM calorie_table ORDER BY Date DESC LIMIT {num}")
        days = cursor.fetchall()
        for day in days[::-1]:
            print_daily_log(day[0])


def print_daily_log(day):
    """Print caloric log for $day"""
    cal_table = Table(title=f"Calorie Log: {day}")
    cal_table.add_column("Food", justify="right", no_wrap=True)
    cal_table.add_column("Calories", justify="right", no_wrap=True)
    cal_table.add_column("Protein", justify="right", no_wrap=True)
    cursor.execute(
        f"SELECT Food_Name, Calories, Protein FROM calorie_table WHERE Date='{day}'")
    rows = cursor.fetchall()
    for row in rows:
        cal_table.add_row(f"{row[0]}", f"{row[1]}kcal", f"{row[2]}g")
    print('\n')
    console = Console()
    console.print(cal_table)
    cals, protein = calc_cals(day)
    to_lose, goal = fetch_goal()
    print(f"Total: {cals} calories / {protein}g protein \
                \n{int(goal)-int(cals)} calories remaining\n")


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

 # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
###############################################################
 # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #


if __name__ == '__main__':
    if args.init:
        logo()
        goal = tdee_to_goal()
        commit_goal(goal)
    if args.weight:
        if int(args.weight) > 1:
            commit_weight(args.weight)
        else:
            display_weight()
    if args.add:
        entry = validate_entry()
        commit_entry(entry)
    if args.list:
        if int(args.list) > 1:
            print_days(int(args.list))
        else:
            print_daily_log(date)
