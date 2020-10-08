import pytest
import purpleair_alexa as pa
from json import loads, dumps
from ask_sdk_core import response_helper
from ask_sdk_model.services.service_client_factory import DeviceAddressServiceClient
from ask_sdk_model.services.device_address.address import Address
from ask_sdk_model.permission_status import PermissionStatus

rb = response_helper.ResponseFactory()


def mp_get_full_address(self, device_id, **kwargs):
    with open('tests/address.json', 'r', encoding="utf8") as file:
        address_dict = loads(file.read())
        return Address(
            address_line1=address_dict['address_line1'],
            address_line2=address_dict['address_line2'], 
            address_line3=address_dict['address_line1'], 
            country_code=address_dict['country_code'], 
            state_or_region=address_dict['state_or_region'], 
            city=address_dict['city'], 
            district_or_county=address_dict['district_or_county'], 
            postal_code=address_dict['postal_code'])


def test_has_address_no_geo():

    DeviceAddressServiceClient.get_full_address = mp_get_full_address

    with open('tests/event.json', 'r', encoding="utf8") as file:
        event = loads(file.read())

    try:
        response = pa.handler(event=event, context = {})
    except Exception as e:
        print(e)
        assert False

    if response['response']['outputSpeech']['ssml'] == \
        rb.speak(pa.ERROR).response.output_speech.ssml:
        assert False

    print(response)

    assert True

def test_no_address_has_geo():
    with open('tests/event.json', 'r', encoding="utf8") as file:
        event = loads(file.read())

    event['context']['System']['user']['permissions']['consent_token'] = None

    event['context']['System']['user']['permissions']['scopes']\
        ['alexa::devices:all:geolocation:read']['status'] = PermissionStatus.GRANTED.value

    try:
        response = pa.handler(event=event, context = {})
    except Exception as e:
        print(e)
        assert False

    if response['response']['outputSpeech']['ssml'] == \
        rb.speak(pa.ERROR).response.output_speech.ssml:
        assert False

    print(response)

    assert True

def test_no_address_no_geo():
    with open('tests/event.json', 'r', encoding="utf8") as file:
        event = loads(file.read())

    event['context']['System']['user']['permissions']['consent_token'] = None

    event['context']['System']['user']['permissions']['scopes']\
        ['alexa::devices:all:geolocation:read']['status'] = PermissionStatus.DENIED.value

    try:
        response = pa.handler(event=event, context = {})
    except Exception as e:
        print(e)
        assert False

    if response['response']['outputSpeech']['ssml'] == \
        rb.speak(pa.NOTIFY_MISSING_PERMISSIONS).response.output_speech.ssml:
        assert True
    else:
        print(response)
        assert False

#def test_has_address_has_geo():
#    assert True==True

