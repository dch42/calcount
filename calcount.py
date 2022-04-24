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
    "-f", "--food", type=str, help='name of food consumed (e.g. eggs)')
parser.add_argument(
    "-c", "--calories", type=int, help='calories in food')
parser.add_argument(
    "-p", "--protein", type=int, help='protein in food')
parser.add_argument(
    "-l", "--list", help='list calorie info for the day', action="store_true")
parser.add_argument(
    "-a", "--add", help='add a caloric entry', action="store_true")
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
        entry = [
            str(args.food),
            int(args.calories),
            int(args.protein),
            str(time),
            str(date)
        ]
        log_entry(entry)
    else:
        os.system('./calcount.py -h')
