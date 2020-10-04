import requests

from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
from math import floor
from statistics import mean

def main():
    device_id = 66407
    url = 'https://www.purpleair.com/json?show=' + str(device_id)

    #response = requests.get('https://api.github.com/user', auth=('user', 'pass'))

    retry_strategy = Retry(
        total=5,
        backoff_factor=10,
        status_forcelist=[302, 429, 500, 502, 503, 504],
        method_whitelist=["HEAD", "GET", "OPTIONS"]
    )

    adapter = HTTPAdapter(max_retries=retry_strategy)
    http = requests.Session()
    http.mount("https://", adapter)
    http.mount("http://", adapter)

    try:
        response = http.get(url, allow_redirects=False)
    except Exception as e:
        print("Retry Exception, need to handle")
        raise
    else:
        print("Response received.")

    try:
        response_json = response.json()
    except Exception as e:
        print("Response isn't valid json")
        raise
    else:
        print("Reponse is valid json")

    #import pdb; pdb.set_trace()

    # get the pm2_5_atm 
    try:
        pm_2_5_atm = mean([\
            float(response_json['results'][0]['pm2_5_atm']),
            float(response_json['results'][1]['pm2_5_atm'])])

    except Exception as e:
        print("Problem getting pm_2_5_atm")
        raise

    print(pm_2_5_atm)
    return pm_2_5_to_aqi(pm_2_5_atm)

def linear(aqi_high, aqi_low, conc_high, conc_low, concentration):
    return ((concentration - conc_low) / (conc_high - conc_low)) \
        * (aqi_high - aqi_low) + aqi_low

def pm_2_5_to_aqi(pm_2_5):
    aqi = 0
    c = (floor(10 * float(pm_2_5))) / 10
    
    if c < 12.1:
        aqi = linear(50, 0, 12, 0, c)
    elif c < 35.5:
        aqi = linear(100, 51, 35.4, 12.1, c)
    elif c < 55.5:
        aqi = linear(150, 101, 55.4, 35.5, c)
    elif c < 150.5:
        aqi = linear(200, 151, 150.4, 55.5, c)
    elif c < 250.5:
        aqi = linear(300, 201, 250.4, 150.5, c)
    elif c < 350.5:
        aqi = linear(400, 301, 350.4, 250.5, c)
    elif c < 500.5:
        aqi = linear(500, 401, 500.4, 350.5, c)
    else:
        aqi = -1
    return round(aqi)

if __name__ == '__main__':
    main()