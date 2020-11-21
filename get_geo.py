import logging
import requests
import os
import json
from urllib.parse import quote_plus
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

##TODO if tests pass delete
#from dotenv import load_dotenv
#grab the environment file (contains juicy secrets like API keys)
#load_dotenv()

def get_address(device_id, consent_token):
    #get the user's address from an alexa device ID and consent token

    base_uri = "https://api.amazonalexa.com"

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

    api_uri = base_uri + "/v1/devices/{}/settings/address".format(device_id)
    api_headers = {
        "Accept": "application/json",
        "Authorization": "Bearer {}".format(consent_token),
    }

    try:
        response = http.get(api_uri, headers=api_headers)
    except Exception as e:
        logging.error("Retry Exception on " + api_uri)
        raise

    try:
        response_json = response.json()
    except Exception as e:
        logging.error("Response isn't valid json")
        logging.error(response_json)
        raise
    else:
        return response_json


def url_encode_address_response(alexa_address_response):

    encoded_address = ""

    if alexa_address_response.address_line1 is not None:
        encoded_address += quote_plus(alexa_address_response.address_line1)

    if alexa_address_response.address_line2 is not None:
        encoded_address += quote_plus(alexa_address_response.address_line2)

    if alexa_address_response.address_line3 is not None:
        encoded_address += quote_plus(alexa_address_response.address_line3)

    encoded_address += ","

    if alexa_address_response.city is not None:
        encoded_address += quote_plus(alexa_address_response.city)

    encoded_address += ","

    if alexa_address_response.state_or_region is not None:
        encoded_address += quote_plus(alexa_address_response.state_or_region)

    encoded_address += ","

    if alexa_address_response.district_or_county is not None:
        encoded_address += quote_plus(alexa_address_response.district_or_county)

    encoded_address += ","

    if alexa_address_response.country_code is not None:
        encoded_address += quote_plus(alexa_address_response.country_code)

    encoded_address += ","

    if alexa_address_response.postal_code is not None:
        encoded_address += quote_plus(alexa_address_response.postal_code)

    return encoded_address

def get_coordinate_from_address_response(alexa_address_response):

    logging.info(alexa_address_response)

    # returns a dict containing a lat long coordinate from an alexa address response

    base_uri = "https://maps.googleapis.com"

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

    encoded_address = url_encode_address_response(alexa_address_response)

    api_uri = base_uri + "/maps/api/geocode/json?address={}&key={}".format(
        encoded_address, os.getenv("MAPS_API_KEY")
    )

    try:
        response = http.get(api_uri)
    except Exception as e:
        logging.error("Retry Exception, need to handle")
        logging.error(response)
        return None

    try:
        response_json = response.json()
        coordinate_google = response_json["results"][0]["geometry"]["location"]
    except Exception as e:
        logging.warning("Response isn't valid json or the coordinate was somehow invalid.")
        logging.warning(response_json)
        return None
    else:
        return {
            "latitude_in_degrees": coordinate_google["lat"],
            "longitude_in_degrees": coordinate_google["lng"],
        }
