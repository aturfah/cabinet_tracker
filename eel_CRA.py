"""Main Python application file for the EEL-CRA demo."""

import platform
import sys

from tkinter import filedialog
from tkinter import *

import eel
from db.example_db import load_db

# Use latest version of Eel from parent directory
sys.path.insert(1, '../../')

def select_and_load_db():
    root = Tk()
    filename =  filedialog.askdirectory(
        initialdir = ".",
        title = "Select directory")
    root.destroy()

    return filename, load_db(filename)

@eel.expose  # Expose function to JavaScript
def say_hello_py(x):
    """Print message from JavaScript on app initialization, then call a JS function."""
    print('Hello from %s' % x)  # noqa T001
    eel.say_hello_js('Python {from within say_hello_py()}!')

@eel.expose
def get_cabinet_counts():
    dir, DATABASE = select_and_load_db()

    raw_job_units = DATABASE["job_units"]
    kitchen_count_map = DATABASE["kitchen_types"]
    job_dates = DATABASE["schedule"]
    raw_unit_kitchens = DATABASE["unit_types"]

    ## Map from the Jobs to te list of Unit Numbers
    job_units_map = {}
    for row in raw_job_units:
        job_id, unit_num = row.values()
        if job_id not in job_units_map:
            job_units_map[job_id] = []
        job_units_map[job_id].append(unit_num)

    ## Map from the Job to the schedule
    job_schedule = {}
    for row in job_dates:
        job_id, date = row.values()
        job_schedule[job_id] = date

    ## Map from the Unit Number to the Kitchen Type
    unit_kitchens = {}
    for row in raw_unit_kitchens:
        unit_num, kitchen_id = row.values()
        if unit_num not in unit_kitchens:
            unit_kitchens[unit_num] = kitchen_id

    ## Map from the Kitchens to the individual Pieces
    kitchen_component_counts = {}
    for row in kitchen_count_map:
        kitchen_id, cpt_id, count = row.values()
        if kitchen_id not in kitchen_component_counts:
            kitchen_component_counts[kitchen_id] = []

        kitchen_component_counts[kitchen_id].append({
            cpt_id: int(count)
        })

    ## Now we construct the rows for the table
    tbl_rows = []
    for job_id in job_units_map:
        job_units = job_units_map[job_id]
        job_date = job_schedule[job_id]

        job_ktchns = [unit_kitchens[x] for x in job_units]

        consolidated_job_parts = {}
        for jktch in job_ktchns:
            for prt_cnt in kitchen_component_counts[jktch]:
                part_id = list(prt_cnt.keys())[0]
                part_cnt = prt_cnt[part_id]
                if part_id not in consolidated_job_parts:
                    consolidated_job_parts[part_id] = 0

                consolidated_job_parts[part_id] += part_cnt

        total_parts = sum(consolidated_job_parts.values())
        tbl_rows.append([job_id, job_date, total_parts])

        for jb_prt in consolidated_job_parts:
            tbl_rows.append([" ", jb_prt, consolidated_job_parts[jb_prt]])

    return {
        "dir": dir,
        "data": tbl_rows}


def start_eel(develop):
    """Start Eel with either production or development configuration."""

    if develop:
        directory = 'src'
        app = None
        page = {'port': 3000}
    else:
        directory = 'build'
        app = 'chrome-app'
        page = 'index.html'

    eel.init(directory, ['.tsx', '.ts', '.jsx', '.js', '.html'])

    # These will be queued until the first connection is made, but won't be repeated on a page reload
    say_hello_py('Python World!')
    eel.say_hello_js('Python World!')   # Call a JavaScript function (must be after `eel.init()`)

    eel.show_log('https://github.com/samuelhwilliams/Eel/issues/363 (show_log)')

    eel_kwargs = dict(
        host='localhost',
        port=8080,
        size=(1280, 800),
    )
    try:
        eel.start(page, mode=app, **eel_kwargs)
    except EnvironmentError:
        # If Chrome isn't found, fallback to Microsoft Edge on Win10 or greater
        if sys.platform in ['win32', 'win64'] and int(platform.release()) >= 10:
            eel.start(page, mode='edge', **eel_kwargs)
        else:
            raise


if __name__ == '__main__':
    import sys

    # Pass any second argument to enable debugging
    DATABASE = {}
    start_eel(develop=len(sys.argv) == 2)
