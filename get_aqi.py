import logging
import requests
import json
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
from math import floor
from statistics import mean
from geopy.distance import great_circle
from os import getenv
from dotenv import load_dotenv

# grab the environment file (contains juicy secrets like API keys)
load_dotenv()


def get_closest_device_readings(user_coordinate):
    # given a lng, lat coordinate, return the device_id of the closest sensor

    # transform user_coordinate
    lat = user_coordinate["latitude_in_degrees"]
    lng = user_coordinate["longitude_in_degrees"]
    user_coordinate = {"lat": lat, "lng": lng}

    with open("purpleair.json", "r", encoding="utf8") as file:
        data = file.read()

    response_json = json.loads(data)

    shortest_distance = None
    shortest_device_id = None
    shortest_pm_2_5_atm = None

    for datum in response_json["data"]:
        sensor_index, sensor_latitude, sensor_longitude, sensor_pm2_5 = datum

        # try:
        #     sensor_coordinate = {"lat": sensor["Lat"], "lng": sensor["Lon"]}
        # except KeyError:
        #     # there's no long/lat on this sensor, pass it
        #     continue

        distance = great_circle(
            (user_coordinate["lat"], user_coordinate["lng"]),
            (sensor_latitude, sensor_longitude),
        ).miles

        try:
            if shortest_distance is None or shortest_distance > distance:
                shortest_distance = distance
                shortest_device_id = sensor_index
                shortest_pm_2_5_atm = sensor_pm2_5

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
    # given a hardcoded device_id, return the device's aqi

    if device_id is None:  # default
        device_id = 66407

    url = "https://api.purpleair.com/v1/sensors/" + str(device_id)

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
    headers = {"X-API-Key": getenv("PURPLEAIR_READ_KEY")}

    try:
        response = http.get(url, allow_redirects=False, headers=headers)
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
        sensor = response_json["sensor"]
        try:
            sensor["pm2.5_a"] == True
        except KeyError:
            logging.warning("Sensor doesn't have a pm2.5 meter")
            raise

        try:
            sensor["pm2.5_b"] == True
        except KeyError:
            pm_2_5_atm = sensor["pm2.5_a"]
        else:
            # average the results if there are two sensors (some models)
            logging.warning(
                "A and B readings are {}, {}".format(
                    sensor["pm2.5_a"], sensor["pm2.5_b"]
                )
            )
            pm_2_5_atm = mean(
                [
                    float(sensor["pm2.5_a"]),
                    float(sensor["pm2.5_b"]),
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

    logging.warning("pm_2_5 reading is {}".format(pm_2_5))

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
    elif c >= 500.5:
        aqi = 500
    else:
        aqi = -1
    return round(aqi)


if __name__ == "__main__":
    main()
