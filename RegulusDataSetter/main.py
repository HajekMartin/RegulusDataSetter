import requests
import json
import datetime
from apscheduler.schedulers.blocking import BlockingScheduler
import yaml
import time
import os

def read_json(filepath):
    try:
        with open(filepath, 'r') as file:
            data = json.load(file)
            return data
    except (FileNotFoundError, json.JSONDecodeError, Exception) as e:
        print_log(f"Failed to read JSON file: {e}", "set_value")
        return None

def read_actual_time_actions():
    print_log("Reading actual time actions", "set_value")
    current_date = datetime.date.today().strftime("%Y-%m-%d")
    schedule = read_json("./RegulusDataSetter/" + current_date + ".txt")
    if schedule is None:
        return
    # Key
    now = datetime.datetime.now()
    current_hour = now.hour
    current_minute = now.minute
    # Get actions
    try:
        actions = schedule[f"{current_hour:02d}" + ":" + f"{current_minute:02d}" + ":00"]
    except KeyError:
        print_log("No actions for this time " + f"{current_hour:02d}" + ":" + f"{current_minute:02d}" + ":00", "set_value")
        return
    set_value(actions)
    
def set_value(actions):
    print_log("Setting value", "set_value")
    for action in actions:
        url = action["URL"]
        data = action["Body"]
        try:
            print_log("--- Setted value " + url + " " + data, "set_value")
            """
            response = requests.post(url, data=data)
            if response.status_code == 200:
                print_log("Setted value " + url + " " + data, "set_value")
            else:
                print_log("POST request failed " + url + " " + data, "set_value")
            """
        except:
            print_log("POST request failed with exeption " + url + " " + data, "set_value")
            continue

def download_schedule():
    print_log("Download schedule starting", "download_schedule")
    guid = read_config('guid')
    #guid = "8B12DFE1-6E3B-46E8-AF38-E1C0E73C2558"
    url = read_config('url')
    #url = "https://dphajek-windows.azurewebsites.net/Api/Regulus/GetSchedule"
    next_date = (datetime.date.today() + datetime.timedelta(days=1)).strftime("%Y-%m-%d")
    actual_date = datetime.date.today().strftime("%Y-%m-%d")
    date = next_date

    current_time = datetime.datetime.now().time()
    if current_time > datetime.time(19, 00) and schedule_file_exists(next_date + ".txt"):
        print_log("Schedule for " + next_date, "download_schedule")
        return
    
    if current_time < datetime.time(18, 59) and schedule_file_exists(actual_date + ".txt"):
        print_log("Schedule for " + actual_date, "download_schedule")
        return
    else:
        date = actual_date

    file_name = date + ".txt"
    if os.path.exists(file_name):
        print_log(f"File {file_name} already exists", "download_schedule")
        return

    while True:
        print_log("Downloading schedule " + date, "download_schedule")
        try:
            params = {
                'date': date,
                'guid': guid
            }
            response = requests.get(url, params=params)
            response.raise_for_status()
            json_data = response.json()
            file_name = date + ".txt"
            with open(file_name, 'w') as file:
                file.write(str(json_data))
            print_log(f"JSON data downloaded and saved to {file_name}", "download_schedule")
            return
        except (requests.RequestException, IOError) as e:
            print_log(f"Failed to download schedule {e}", "download_schedule")
            time.sleep(300)  # Wait for 5 minutes before next attempt

def schedule_file_exists(file_name):
    if os.path.exists(file_name):
        return True
    return False

def read_config(value_name):
    try:
        print_log("Reading config " + value_name, "read_config")
        file_path = '/usr/src/app/config.yaml'
        
        with open(file_path, 'r') as config_file:
            config = yaml.safe_load(config_file)

        value = config['options'].get(value_name)
        print_log("Config " + value_name + " = " + value, "read_config")
        return value
    except Exception as e:
        print_log("Failed to read config: " + str(e), "read_config")
        return None

def print_log(message, method):
    print("[", datetime.datetime.now(), method, "]", message)

if __name__ == '__main__':
    print_log("Starting RegulusDataSetter", "main")
    
    scheduler = BlockingScheduler()
    scheduler.add_job(read_actual_time_actions, 'cron', minute='0,15,30,45')
    scheduler.add_job(download_schedule, 'cron', hour=19, minute=0)
    # Zapnu hned aby se kdyžtak stáhnul aktuiální rozvrh
    current_time = datetime.datetime.now().time()
    scheduler.add_job(download_schedule, 'date', run_date=datetime.datetime.now() + datetime.timedelta(seconds=5))

    scheduler.start()
    scheduler.start()

    
    
    