from builtins import max
from datetime import datetime, timezone
from MotherRunner import MotherRunner
from os import path

def parse_new_publications(input_path, output_path):
    '''
    Script that should be run once a day. It will parse the article for 
    the current date, if it exists. If not, it will be added to todo.txt.
    The todo.txt is also loaded and checked. 
    '''
    dates = []
    dates_to_parse = []

    # load all dates from todo in dates list
    with open('todo.txt', 'r') as f:
        for l in f:
            if l != "":
                l = l.strip()
                dates.append(datetime.strptime(l, '%m/%d/%Y %H:%M:%S').replace(hour=0, minute=0, second=0, microsecond=0, tzinfo=timezone.utc))
    
    # deletes all content of txt file
    open('todo.txt', 'w').close()
    
    #add current date
    current_date = datetime.today().replace(hour=0, minute=0, second=0, microsecond=0, tzinfo=timezone.utc)
    dates.append(current_date)

    #if the date exists as a folder, it can be parsed
    # if not, it will be be written to the todo.txt
    for date in dates:
        if path.exists(input_path+"/"+date.strftime('%Y-%m-%d')):
            dates_to_parse.append(date)
        else:
            with open('todo.txt', 'a') as f:
                date_str = date.strftime("%m/%d/%Y %H:%M:%S")
                f.write(f"{date_str}\n")

    #find from and to date params, by taking min and max of dates_to_be_parsed
    from_date = min(dates_to_parse)
    to_date = max(dates_to_parse)
    
    MotherRunner(input_path, from_date, to_date, output_path).start()

if __name__ == "__main__":
    parse_new_publications()