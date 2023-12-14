import requests

def set_value():
    # Your POST request code here
    url = "http://192.168.0.116/HOME.XML"
    data = "__T4B9BD0CF_BOOL_i%3D1"
    response = requests.post(url, data=data)
    print(response.text)
    if response.status_code == 200:
        print("POST request successful")
    else:
        print("POST request failed")

if __name__ == '__main__':
    set_value()
    