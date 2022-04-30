# calcount
A simple CLI calorie tracker.
Data persists using a SQLite database.

## Setup 🔧
Clone the repo and change to directory:
~~~
git clone https://github.com/dch42/calcount.git && cd calcount
~~~

If running MacOS, add exec permissions and run `setup.sh`:
~~~
chmod +x ./setup.sh && ./setup.sh
~~~
This will install dependencies and install the script as `calcount` in /Users/$USER/bin, as well as add to bash or zsh $PATH.
## Usage

### Calculating TDEE/BMR/Daily Caloric Goal

On first run, invoke with `--init` to calculate TDEE and BMR, as well as set a weight loss goal:

~~~
calcount --init
~~~

The script will prompt user for data such as age, sex, height, weight, daily activity level, and a weight loss goal (lb/week). This information is used to calculate BMR using the [Harris-Benedict Equation](https://en.wikipedia.org/wiki/Harris%E2%80%93Benedict_equation) and TDEE using activity multipliers. Caloric goal is calculated assuming a deficit of 500kcal/day results in ~1lb of weight loss/week.

This data can be overridden by repeating this process, as calculations are made using the most recent entry in the table.

### Adding Food to Log

Invoking with `-a` or `--add` will add a food entry to the daily log.

For example, to add a protein bar with 190kcal and 16g protein to the log, pass the data like so:

~~~
calcount -a 'Protein Bar' 190 16
~~~

### Viewing Logs

The daily log can be viewed by invoking with `-l` or `--list`

~~~
calcount -l
~~~

### Options
- `-h, --help`
    - show this help message and exit
- `--init`
    - initialize TDEE/BMR and set weight loss goal
- `-a, --add ['food' kcal protein]` str int int
    - add a caloric entry to the log
- `-l, --list`
    - print a table with daily caloric data 