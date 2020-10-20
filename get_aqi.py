import logging
import requests
import json
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
from math import floor
from statistics import mean
from geopy.distance import great_circle

def get_closest_device_readings(user_coordinate):
# given a lng, lat coordinate, return the device_id of the closest sensor

    #transform user_coordinate
    lat = user_coordinate["latitude_in_degrees"]
    lng = user_coordinate["longitude_in_degrees"]
    user_coordinate = {"lat": lat, "lng": lng}

    try:
        with open("purpleair.json", "r", encoding="utf8") as file:
            data = file.read()

        response_json = json.loads(data)
    except: #occasionally the json inbound is malformed, so resort to static backup
        json.decoder.JSONDecodeError:
        with open("purpleair_backup.json", "r", encoding="utf8") as file:
            data = file.read()

    shortest_distance = None
    shortest_device_id = None
    shortest_pm_2_5_atm = None

    for sensor in response_json["results"]:
        try:
            sensor_coordinate = {"lat": sensor["Lat"], "lng": sensor["Lon"]}
        except KeyError:
            # there's no long/lat on this sensor, pass it
            continue

        distance = great_circle(
            (user_coordinate["lat"], user_coordinate["lng"]),
            (sensor_coordinate["lat"], sensor_coordinate["lng"]),
        ).miles

        try:
            if shortest_distance is None or shortest_distance > distance:
                shortest_distance = distance
                shortest_device_id = sensor["ID"]
                shortest_pm_2_5_atm = pm_2_5_to_aqi(sensor["PM2_5Value"])

        except:
            logging.error("Something weird about readings returned")
            logging.error(sensor)

    logging.info(
        "Shortest device id is {} and distance is {} miles".format(
            shortest_device_id, shortest_distance
        )
    )

    return {
        "device_id": shortest_device_id,
        "miles_away": shortest_distance,
        "aqi": shortest_pm_2_5_atm,
    }


def get_hardcoded_aqi(device_id):
    #given a hardcoded device_id, return the device's aqi

    if device_id is None:  # default
        device_id = 66407

    url = "https://www.purpleair.com/json?show=" + str(device_id)

    retry_strategy = Retry(
        total=5,
        backoff_factor=10,
        status_forcelist=[302, 429, 500, 502, 503, 504],
        method_whitelist=["HEAD", "GET", "OPTIONS"],
    )

    adapter = HTTPAdapter(max_retries=retry_strategy)
    http = requests.Session()
    http.mount("https://", adapter)
    http.mount("http://", adapter)

    try:
        response = http.get(url, allow_redirects=False)
    except Exception as e:
        logging.error("Retry Exception on " + url)
        raise

    try:
        response_json = response.json()
    except Exception as e:
        logging.warning("Response isn't valid json")
        logging.warning(response_json)
        raise

    try:
        try:
            response_json["results"][1]["pm2_5_atm"] == True
        except KeyError:
            pm_2_5_atm = response_json["results"][0]["pm2_5_atm"]
        else:
            #average the results if there are two sensors (some models)
            pm_2_5_atm = mean(
                [
                    float(response_json["results"][0]["pm2_5_atm"]),
                    float(response_json["results"][1]["pm2_5_atm"]),
                ]
            )

    except Exception as e:
        logging.error("Problem getting pm_2_5_atm")
        logging.error(response_json)
        raise
    return pm_2_5_to_aqi(pm_2_5_atm)


def linear(aqi_high, aqi_low, conc_high, conc_low, concentration):
    return ((concentration - conc_low) / (conc_high - conc_low)) * (
        aqi_high - aqi_low
    ) + aqi_low


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


if __name__ == "__main__":
    main()
