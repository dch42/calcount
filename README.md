# calcount
~~~
  ____      _  ____                  _   
 / ___|__ _| |/ ___|___  _   _ _ __ | |_ 
| |   / _` | | |   / _ \| | | | '_ \| __|
| |__| (_| | | |__| (_) | |_| | | | | |_ 
 \____\__,_|_|\____\___/ \__,_|_| |_|\__|
                                         
Keep track of calories, protein, and weight loss/gain.
~~~

CalCount (cals) is a simple python3 CLI app to track calories, protein, and weight progress.

Data persists using a SQLite database, `$HOME/.calorie_log.db`.

*Currently only handles imperial units.*

## Setup 🔧
Clone the repo and change to directory:
~~~
git clone https://github.com/dch42/calcount.git && cd calcount
~~~

### Installation
If running MacOS or Linux, and using bash or zsh, `setup.sh` can be run to quickly make the script available in `$PATH`.

Add exec permissions and run `setup.sh`:
~~~
chmod +x ./setup.sh && ./setup.sh
~~~
This will install dependencies and install the script as `cals` in ~/bin, as well as add to bash or zsh `$PATH`.

## Usage

~~~
usage: cals [-h] [--init] [-a A A A] [-r R R R] [-l [L]] [-w [W]]

cals -- track calories, protein, and weight loss/gain

optional arguments:
  -h, --help  show this help message and exit
  --init      calculate TDEE and set weekly weight loss goal
  -a A A A    add a caloric entry ['food name' calories protein]
  -r R R R    remove a caloric entry ['food name' calories protein]
  -l [L]      list calorie info for day(s)
  -w [W]      input weight into weight log
  -x          export calorie history to csv

Usage examples:

Add bar with 190kcal and 16g protein:
	cals -a 'Protein Bar' 190 16

Remove the entry from previous example:
	cals -r 'Protein Bar' 190 16

Print calorie log tables for past 3 days:
	cals -l 3

Add a weight record of 142.7 to the table:
	cals -w 142.7

Display weight log and total weight loss/gain:
	cals -w
~~~

### Calculating TDEE/BMR/Daily Caloric Goal

On first run, invoke with `--init` to calculate TDEE and BMR, as well as set a weight loss goal:

~~~
cals --init
~~~

The script will prompt user for data such as age, sex, height, weight, daily activity level, and a weight loss goal (lb/week). Currently only handles imperial unit input. 

This information is used to calculate BMR using the [Harris-Benedict Equation](https://en.wikipedia.org/wiki/Harris%E2%80%93Benedict_equation) and TDEE using activity multipliers. 

Caloric goal is calculated assuming a deficit of 500kcal/day results in ~1lb of weight loss/week.

This data can be overridden by repeating this process, as calculations are made using the most recent entry in the table.

### Adding Food to Log

Invoke with `-a` to add a food entry to the daily log.

To add a *protein bar* with *190kcal* and *16g* protein:
~~~
cals -a 'Protein Bar' 190 16
~~~
To add an *egg* with *63kcal* and *7g* protein:
~~~
cals -a egg 63 7
~~~

#### Removing Food from Log

To remove an *egg* with *63kcal* and *7g* protein:
~~~
cals -r egg 63 7
~~~

***Caution***, *if there are multiple entries matching the criteria on the daily log, this will delete those duplicates as well.*

For example, given the following daily log:

~~~
    Calorie Log: 2022-05-04     
┏━━━━━━━━━┳━━━━━━━━━━┳━━━━━━━━━┓
┃    Food ┃ Calories ┃ Protein ┃
┡━━━━━━━━━╇━━━━━━━━━━╇━━━━━━━━━┩
│  Olives │   50kcal │      0g │
│ fabcake │  420kcal │     20g │
│    dupe │   10kcal │     10g │
│    dupe │   10kcal │     10g │
└─────────┴──────────┴─────────┘
~~~

`cals -r dupe 10 10` will yield:

~~~
    Calorie Log: 2022-05-04     
┏━━━━━━━━━┳━━━━━━━━━━┳━━━━━━━━━┓
┃    Food ┃ Calories ┃ Protein ┃
┡━━━━━━━━━╇━━━━━━━━━━╇━━━━━━━━━┩
│  Olives │   50kcal │      0g │
│ fabcake │  420kcal │     20g │
└─────────┴──────────┴─────────┘
~~~

### Viewing Logs

The daily log can be viewed by invoking with `-l`.

To view previous tables, invoke with `-l n`, where *n* is the number of tables to view. 

For example, `cals -l 3` will display tables for the past 3 days. 

~~~
$ cals -l

      Calorie Log: 2022-04-29      
┏━━━━━━━━━━━━┳━━━━━━━━━━┳━━━━━━━━━┓
┃       Food ┃ Calories ┃ Protein ┃
┡━━━━━━━━━━━━╇━━━━━━━━━━╇━━━━━━━━━┩
│ Protein Bar│  190kcal │     16g │
│ egg        │   63kcal │      7g │
└────────────┴──────────┴─────────┘
Total: 253 calories / 23g protein          
1560 calories remaining
~~~

~~~
$ cals -l 2

      Calorie Log: 2022-04-28      
┏━━━━━━━━━━━━┳━━━━━━━━━━┳━━━━━━━━━┓
┃       Food ┃ Calories ┃ Protein ┃
┡━━━━━━━━━━━━╇━━━━━━━━━━╇━━━━━━━━━┩
│ Tofu Salad │  500kcal │      7g │
│ Soup       │  190kcal │     15g │
| Protein Bar|  190kcal |     20g |
│ Beer       │  200kcal │      0g │
└────────────┴──────────┴─────────┘
Total: 1080 calories / 42g protein          
733 calories remaining

      Calorie Log: 2022-04-29      
┏━━━━━━━━━━━━┳━━━━━━━━━━┳━━━━━━━━━┓
┃       Food ┃ Calories ┃ Protein ┃
┡━━━━━━━━━━━━╇━━━━━━━━━━╇━━━━━━━━━┩
│ Protein Bar│  190kcal │     16g │
│ egg        │   63kcal │      7g │
└────────────┴──────────┴─────────┘
Total: 253 calories / 23g protein          
1560 calories remaining
~~~

### Logging and Viewing Weight Progress

Invoke with `-w n`, where *n* is weight to be recorded.

To add a weight entry of 148 lbs to the table:

~~~
cals -w 148
~~~

Invoking without arguments will print a table of weight entries/dates, as well as calculate and display total weight loss/gain.

~~~
$ cals -w

      Weight Log       
┏━━━━━━━━━━━━┳━━━━━━━━┓
┃       Date ┃ Weight ┃
┡━━━━━━━━━━━━╇━━━━━━━━┩
│ 2022-05-03 │    149 │
│ 2022-05-04 │  148.3 │
└────────────┴────────┘

Recorded loss: 0.7 lbs
~~~