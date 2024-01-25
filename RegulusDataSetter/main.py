import requests
import json
import datetime
from apscheduler.schedulers.blocking import BlockingScheduler
import yaml

def read_json(filepath):
    with open(filepath, 'r') as file:
        data = json.load(file)
        return data

def read_actual_time_actions():
    current_date = datetime.date.today().strftime("%Y-%m-%d")
    schedule = read_json("./RegulusDataSetter/" + current_date + ".txt")
    # Key
    now = datetime.datetime.now()
    current_hour = now.hour
    current_minute = now.minute
    # Get actions
    try:
        actions = schedule[f"{current_hour:02d}" + ":" + f"{current_minute:02d}" + ":00"]
        #actions = schedule["12:00:00"]
    except KeyError:
        return
    
    set_value(actions)
    
def set_value(actions):
    current_datetime = datetime.datetime.now()
    print("[", current_datetime, "]", " Setting values")
    
    for action in actions:
        url = action["URL"]
        data = action["Body"]
        try:
            response = requests.post(url, data=data)
            if response.status_code == 200:
                print("POST request successful")
            else:
                print("POST request failed " + url + " " + data)
        except:
            print("POST request failed " + url + " " + data)
            continue

def download_schedule():
    guid = read_config('guid')
    url = read_config('url')
    next_date = (datetime.date.today() + datetime.timedelta(days=1)).strftime("%Y-%m-%d")
    try:
        params = {
            'date': next_date,
            'guid': guid
        }
        response = requests.get(url, params=params)
        response.raise_for_status()
        json_data = response.json()
        file_name = next_date + ".txt"
        with open(file_name, 'w') as file:
            file.write(str(json_data))

        print(f"JSON data downloaded and saved to {file_name}")
    except requests.RequestException as e:
        print(f"Error occurred while downloading the JSON: {e}")
    except IOError as e:
        print(f"Error occurred while writing to the file: {e}")

def read_config(value_name):
    file_path = '/usr/src/app/config.yaml'
    with open(file_path, 'r') as config_file:
        config = yaml.safe_load(config_file)

    value = config['options'].get(value_name)
    return value

if __name__ == '__main__':
    scheduler = BlockingScheduler()
    scheduler.add_job(read_actual_time_actions, 'cron', minute='0,15,30,45')
    scheduler.add_job(download_schedule, 'cron', hour=19, minute=0)
    scheduler.start()
    