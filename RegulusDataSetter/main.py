import requests
import json
import datetime
from apscheduler.schedulers.blocking import BlockingScheduler
import yaml
import time
import os

DEF_FODLER = 'usr/src/app/'

def read_json(filepath):
    try:
        with open(DEF_FODLER + filepath, 'r') as file:
            data = json.load(file)
            return data
    except (FileNotFoundError, json.JSONDecodeError, Exception) as e:
        print_log(f"Failed to read JSON file: {e}", "set_value")
        return None

def set_actual_actions():
    date = datetime.datetime.now()
    actions = download_schedule(date)
    set_value(actions)

def set_value(actions):
    print_log("Setting value", "set_value")
    for action in actions:
        url = action["URL"]
        data = action["body"]
        try:
            # print_log("--- Setted value " + url + " " + data, "set_value")
            response = requests.post(url, data=data)
            if response.status_code == 200:
                print_log("Setted value " + url + " " + data, "set_value")
            else:
                print_log("POST request failed " + url + " " + data, "set_value")
        except:
            print_log("POST request failed with exeption " + url + " " + data, "set_value")
            continue

def download_schedule(date):
    guid = read_config('guid')
    #guid = '8b12dfe1-6e3b-46e8-af38-e1c0e73c2558'
    url = read_config('url')
    #url = 'https://dphajek-windows.azurewebsites.net/Api/Regulus/GetActualActions'
    print_log("Downloading schedule ", "download_schedule")
    try:
        params = {
            'guid': guid,
            'time': time.strftime("%H:%M"),
        }
        response = requests.get(url, params=params)
        response.raise_for_status()
        return json.loads(response.text)
    except (requests.RequestException, IOError) as e:
        print_log(f"Failed to download schedule {e}", "download_schedule")
        return None

def read_config(value_name):
    try:
        print_log("Reading config " + value_name, "read_config")
        file_path = 'data/' + 'options.json'
        
        with open(file_path) as file:
            data = json.load(file)
            if value_name in data:
                value = data[value_name]
                print_log("Config " + value_name + " = " + value, "read_config")
                return value
            else:
                raise Exception("Value not found")
    except Exception as e:
        print_log("Failed to read config: " + str(e), "read_config")
        return None

def print_log(message, method):
    string = "[ " + datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") + " ] " + method + " " + message
    create_log_file()
    
    log_file = DEF_FODLER + 'logs/' + datetime.datetime.now().strftime("%Y-%m-%d") + '.log'
    with open(log_file, 'a') as file:
        file.write(string + '\n')
    
def create_log_file():
    log_folder = DEF_FODLER + 'logs/'
    if not os.path.exists(log_folder):
        os.makedirs(log_folder)
    
    log_file = log_folder + datetime.datetime.now().strftime("%Y-%m-%d") + '.log'
    if not os.path.exists(log_file):
        with open(log_file, 'w') as file:
            pass

if __name__ == '__main__':
    print_log("Starting RegulusDataSetter", "main")

    scheduler = BlockingScheduler()
    scheduler.add_job(set_actual_actions, 'cron', minute='0,5,10,15,20,25,30,35,40,45,50,55')

    scheduler.start()
    