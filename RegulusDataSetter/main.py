import requests

def set_value(data):
    # Your POST request code here
    url = "http://192.168.0.116/HOME.XML"
    
    response = requests.post(url, data=data)
    print(response.text)
    if response.status_code == 200:
        print("POST request successful")
    else:
        print("POST request failed")

if __name__ == '__main__':
    set_value("__T70BDAE66_REAL_.1f=20.0")
    set_value("__T14B807DC_BOOL_i=1")
    