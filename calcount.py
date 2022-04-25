#!/usr/bin/env python3
"""Track caloric intake"""

import os
import argparse
import sqlite3
from datetime import datetime

date = datetime.now().date()
time = datetime.now().time().strftime('%H:%M:%S')

db = sqlite3.connect("./calorie_log.db")
cursor = db.cursor()

parser = argparse.ArgumentParser(
    description="Track caloric intake")

parser.add_argument(
    "-a", "--add", nargs="+", help="add a caloric entry ('STR food' INT calories INT protein)")
parser.add_argument(
    "-l", "--list", help='list calorie info for the day', action="store_true")

args = parser.parse_args()


def log_entry(entry):
    """Insert calorie info into database"""
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


def print_daily_log():
    cursor.execute(f"SELECT * FROM calorie_table WHERE Date='{date}'")
    rows = cursor.fetchall()
    for row in rows:
        print(f"{row[0]}: {row[1]}kcal, {row[2]}g protein")


def count_cals():
    with db:
        cals = 0
        cursor.execute(
            f"SELECT Calories FROM calorie_table WHERE Date='{date}'")
        rows = (cursor.fetchall())
        for row in rows:
            cals = cals + row[0]
        return cals


def count_protein():
    with db:
        protein = 0
        cursor.execute(
            f"SELECT Protein FROM calorie_table WHERE Date='{date}'")
        rows = (cursor.fetchall())
        for row in rows:
            protein = protein + row[0]
        return protein


if __name__ == '__main__':
    if args.list:
        print_daily_log()
        cals = count_cals()
        protein = count_protein()
        print(
            f"You've consumed {cals} calories and {protein}g protein for the day.")
    elif args.add:
        if len(args.add) == 3 and str(args.add[1:]).isdigit:
            entry = [
                str(args.add[0]),
                int(args.add[1]),
                int(args.add[2]),
                str(time),
                str(date)
            ]
            log_entry(entry)
        else:
            os.system('./calcount.py -h')
    else:
        os.system('./calcount.py -h')
