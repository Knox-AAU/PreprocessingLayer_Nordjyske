from datetime import datetime, timezone
from consume_folders import MotherRunner
from os import path

def parse_new_publications():
    input_path = "/home/aau/Desktop/input"
    output_path = "/home/aau/Desktop/newoutput"
    dates = []

    with open('todo.txt', 'r') as f:
        for l in f:
            dates.append(datetime.strptime(l, '%m/%d/%Y %H:%M:%S'))

    print(dates[0].strftime("%m/%d/%Y %H:%M:%S"))
    current_date = datetime.today().replace(hour=0, minute=0, second=0, microsecond=0, tzinfo=timezone.utc)
    dates.append(current_date)

    print(input_path+"/"+current_date.strftime('%Y-%m-%d'))
    print(not path.exists(input_path+"/"+current_date.strftime('%Y-%m-%d')))
    if not path.exists(input_path+"/"+current_date.strftime('%Y-%m-%d')):
        with open('todo.txt', 'a') as f:
            f.write(current_date.strftime("%m/%d/%Y %H:%M:%S"))
    
    MotherRunner(input_path, current_date, current_date, output_path).start()

parse_new_publications()