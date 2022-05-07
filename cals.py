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
    "-a", nargs=3, action="store", help="add a caloric entry ['food name' calories protein]")
parser.add_argument(
    "-r", nargs=3, action="store", help="remove a caloric entry ['food name' calories protein]")
parser.add_argument(
    "-l", nargs="?", const=1, help='list calorie info for day(s)')
parser.add_argument(
    "-w", nargs="?", type=float, const=1, help='input weight into weight log')

args = parser.parse_args()


def logo():
    """Print script logo"""
    pyfiglet.print_figlet("CalCount")
    print("Keep track of calories, protein, and weight loss/gain.\n")


def validate_input(prompt, dtype):
    """Ensure user input for $prompt matches datatype $type"""
    good = False
    while not good:
        val = input(prompt)
        try:
            test = dtype(val)
            good = True
            return test
        except ValueError as error:
            print(f"Please ensure input matches datatype `{dtype}`.\n{error}")

# tdee/bmr


def get_profile():
    """Collect input for user profile and calculations"""
    print("Please answer the following questions.\nThey will be used to calculate your BMR, TDEE, and caloric deficit required to reach your weight loss goal.\n")
    age = validate_input("Please enter your age: ", int)
    sex = validate_input("Please enter your sex (m/f): ", str)
    height = validate_input("Please enter your height (feet.inches): ", float)
    weight = validate_input("Please enter your weight (lbs): ", float)
    commit_weight(weight)
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
    commit_goal((lose, goal, time, date))


def commit_goal(goal_entry):
    """Commit goal data to db"""
    cursor.execute("""CREATE TABLE IF NOT EXISTS goal_table(
        Lose INTEGER,
        Goal INTEGER,
        Time TEXT,
        Date TEXT)
        """)
    cursor.executemany(
        "INSERT INTO goal_table VALUES (?,?,?,?)", (goal_entry, ))
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
    weight_log = Table(title="Weight Log")
    weight_log.add_column("Date", justify="right", no_wrap=True)
    weight_log.add_column("Weight", justify="right", no_wrap=True)
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
        except sqlite3.OperationalError as error:
            print(f"\033[91m[ERROR]\033[00m {error}\n\tNo weight data to display.\n\
\tFirst, please enter a weight to the table: `cals -w weight`")


def calc_weight_loss():
    """Calculate difference between first recorded weight and last recorded weight"""
    with db:
        cursor.execute(
            "SELECT Weight FROM weight_table ORDER BY Date, Time")
        weights = cursor.fetchall()
        weight_loss = weights[0][0] - weights[-1][0]
        return weight_loss


# calorie log


def fetch_goal():
    """Fetch most recent caloric goals from db"""
    with db:
        cursor.execute(
            "SELECT Goal FROM goal_table ORDER BY Date")
        goal = cursor.fetchone()[0]
        return goal


def validate_entry(args):
    """Validate and build caloric log entry for addition or removal"""
    if str(args[1:]).isdigit:
        entry = [
            str(args[0]),
            int(args[1]),
            int(args[2]),
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
        try:
            cursor.execute(
                f"SELECT DISTINCT Date FROM calorie_table ORDER BY Date DESC LIMIT {num}")
            days = cursor.fetchall()
            for day in days[::-1]:
                print_daily_log(day[0])
        except sqlite3.OperationalError as error:
            print(f"\033[91m[ERROR]\033[00m {error}\n\tNo calorie data to display.\n\
\tFirst, please enter a food item to the table: `cals -f 'food' cals protein`")


def print_daily_log(day):
    """Print caloric log for $day"""
    cal_table = Table(title=f"Calorie Log: {day}")
    cal_table.add_column("Food", justify="right", no_wrap=True)
    cal_table.add_column("Calories", justify="right", no_wrap=True)
    cal_table.add_column("Protein", justify="right", no_wrap=True)
    try:
        with db:
            cursor.execute(
                f"SELECT Food_Name, Calories, Protein FROM calorie_table WHERE Date='{day}'")
            rows = cursor.fetchall()
            for row in rows:
                cal_table.add_row(f"{row[0]}", f"{row[1]}kcal", f"{row[2]}g")
            print('\n')
            console = Console()
            console.print(cal_table)
            cals, protein = calc_cals(day)
            calorie_limit = fetch_goal()
            print(f"Total: {cals} calories / {protein}g protein \
                        \n{int(calorie_limit-cals)} calories remaining\n")
    except sqlite3.OperationalError as error:
        print(f"\033[91m[ERROR]\033[00m {error}\n\tNo calorie data to display.\n\
\tFirst, please enter a food item to the table: `cals -f 'food' cals protein`")


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


def remove_entry(entry):
    """Remove caloric entry from db"""
    food, calories, protein = entry[0], entry[1], entry[2]
    with db:
        try:
            cursor.execute(
                f"DELETE FROM calorie_table WHERE Date='{date}' AND Food_Name='{food}' AND Calories='{calories}' AND Protein='{protein}'")
        except sqlite3.OperationalError as error:
            print(f"\033[91m[ERROR]\033[00m {error}")


if __name__ == '__main__':
    if args.init:
        logo()
        tdee_to_goal()
    if args.w:
        if int(args.w) > 1:
            commit_weight(args.w)
        else:
            display_weight()
    if args.a:
        entry = validate_entry(args.a)
        commit_entry(entry)
    if args.r:
        entry = validate_entry(args.r)
        remove_entry(entry)

    if args.l:
        if int(args.l) > 1:
            print_days(int(args.l))
        else:
            print_daily_log(date)
