import requests
import os
from urllib.parse import quote_plus
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
from dotenv import load_dotenv


load_dotenv()


def get_address(device_id, consent_token):

    base_uri = 'https://api.amazonalexa.com'

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

    api_uri = base_uri + "/v1/devices/{}/settings/address".format(device_id)
    api_headers = {"Accept": "application/json", "Authorization": "Bearer {}".format(consent_token)}

    try:
        response = http.get(api_uri, headers=api_headers)
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
        return response_json
        print("Response is valid json")



def url_encode_address_response(alexa_address_response):
    encoded_address = ""

    if alexa_address_response['addressLine1'] is not None:
       encoded_address += quote_plus(alexa_address_response['addressLine1'])

    if alexa_address_response['addressLine2'] is not None:
       encoded_address += quote_plus(alexa_address_response['addressLine2'])

    if alexa_address_response['addressLine3'] is not None:
       encoded_address += quote_plus(alexa_address_response['addressLine3'])

    encoded_address += ","

    if alexa_address_response['city'] is not None:
       encoded_address += quote_plus(alexa_address_response['city'])

    encoded_address += ","

    if alexa_address_response['stateOrRegion'] is not None:
       encoded_address += quote_plus(alexa_address_response['stateOrRegion'])

    encoded_address += ","

    if alexa_address_response['districtOrCounty'] is not None:
       encoded_address += quote_plus(alexa_address_response['districtOrCounty'])

    encoded_address += ","

    if alexa_address_response['countryCode'] is not None:
       encoded_address += quote_plus(alexa_address_response['countryCode'])

    encoded_address += ","

    if alexa_address_response['postalCode'] is not None:
       encoded_address += quote_plus(alexa_address_response['postalCode'])

    return encoded_address


#https://maps.googleapis.com/maps/api/geocode/json?address=1600+Amphitheatre+Parkway,+Mountain+View,+CA&key=YOUR_API_KEY

#returns a dict containing a lat long coordinate from an alexa address response


def get_coordinate_from_address_response(alexa_address_response):

    base_uri = 'https://maps.googleapis.com'

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

    encoded_address = url_encode_address_response(alexa_address_response)

    api_uri = base_uri + "/maps/api/geocode/json?address={}&key={}".format(encoded_address, os.getenv("MAPS_API_KEY"))
    #api_headers = {"Accept": "application/json", "Authorization": "Bearer {}".format(consent_token)}

    try:
        response = http.get(api_uri)
    except Exception as e:
        print("Retry Exception, need to handle")
        raise
    else:
        print("Response received.")

    try:
        response_json = response.json()
        coordinate = response_json['results'][0]['geometry']['location']
    except Exception as e:
        print("Response isn't valid json or the coordinate was somehow invalid.")
        raise
    else:
        return coordinate
        print("Response is valid json")

