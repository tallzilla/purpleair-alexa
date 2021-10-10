import pytest
import purpleair_alexa as pa
from json import loads, dumps
from ask_sdk_core import response_helper
from ask_sdk_model.services.service_client_factory import DeviceAddressServiceClient
from ask_sdk_model.services.device_address.address import Address
from ask_sdk_model.permission_status import PermissionStatus
from ask_sdk_model.interfaces.geolocation.coordinate import Coordinate
from random import uniform

intent_response = {"canFulfillIntent": {"canFulfill": "NO"}}
can_fulfill_intent_request_type = "CanFulfillIntentRequest"

rb = response_helper.ResponseFactory()

test_coordinate = Coordinate(
    latitude_in_degrees=37.363796,
    longitude_in_degrees=-121.77012,
    accuracy_in_meters=65.0,
)


def mp_get_full_address(self, device_id, **kwargs):
    with open("tests/address.json", "r", encoding="utf8") as file:
        address_dict = loads(file.read())
        return Address(
            address_line1=address_dict["address_line1"],
            address_line2=address_dict["address_line2"],
            address_line3=address_dict["address_line3"],
            country_code=address_dict["country_code"],
            state_or_region=address_dict["state_or_region"],
            city=address_dict["city"],
            district_or_county=address_dict["district_or_county"],
            postal_code=address_dict["postal_code"],
        )


def mp_get_full_address_bad(self, device_id, **kwargs):
    with open("tests/address_bad.json", "r", encoding="utf8") as file:
        address_dict = loads(file.read())
        return Address(
            address_line1=address_dict["address_line1"],
            address_line2=address_dict["address_line2"],
            address_line3=address_dict["address_line3"],
            country_code=address_dict["country_code"],
            state_or_region=address_dict["state_or_region"],
            city=address_dict["city"],
            district_or_county=address_dict["district_or_county"],
            postal_code=address_dict["postal_code"],
        )


def evaluate_handler_for_intents(
    handler, event, context, success_titles=None, permissions=None, intent_response=None
):
    # Given an event handler, an event, and context, evaluate for each
    # Intent request available
    with open("tests/intent_requests.json", "r", encoding="utf8") as file:
        intent_requests = loads(file.read())

    for intent_request in intent_requests:

        event["request"] = intent_request["request"]

        handler_output = handler(event=event, context=context)
        response = handler_output["response"]

        # TODO: This is a hack and could lead to an error (if a handler
        # returns the wrong successful intent)
        try:

            # if this is a can_fulfill_intent_request request
            if intent_request["request"]["type"] == can_fulfill_intent_request_type:
                if response.get("canFulfillIntent") is not None:
                    if response != intent_response:
                        assert False
            else:
                if success_titles is not None:
                    if (
                        response.get("card") is None
                        or response["card"]["title"] not in success_titles
                    ):
                        assert False
                if permissions is not None:
                    if response["card"]["permissions"] not in permissions:
                        assert False
        except Exception as e:
            print(e)
            raise


def test_loc_supported_loc_access(coordinate=test_coordinate):
    # User has geolocation supported and granted access to that data

    try:
        with open("tests/event_shell.json", "r", encoding="utf8") as file:
            event = loads(file.read())

        event["context"]["System"]["user"]["permissions"]["scopes"] = {
            "alexa::devices:all:geolocation:read": {
                "status": PermissionStatus.GRANTED.value
            }
        }

        event["context"]["geolocation"] = {"coordinate": coordinate.to_dict()}

        success_titles = [pa.SWEET_TITLE, pa.SUCCESS_TITLE]
        evaluate_handler_for_intents(
            pa.handler,
            event=event,
            context={},
            success_titles=success_titles,
            intent_response=intent_response,
        )

    except Exception as e:
        print(e)
        raise

    assert True


def test_loc_supported_no_loc_access_address_access():
    # User has geolocation supported, hasn't granted access, but has address access

    # Need to monkey patch function to return address
    saved_method = DeviceAddressServiceClient.get_full_address
    DeviceAddressServiceClient.get_full_address = mp_get_full_address

    try:
        with open("tests/event_shell.json", "r", encoding="utf8") as file:
            event = loads(file.read())

        event_permissions = event["context"]["System"]["user"]["permissions"]

        event_permissions["scopes"] = {
            "alexa::devices:all:geolocation:read": {
                "status": PermissionStatus.DENIED.value
            }
        }

        event["context"]["geolocation"] = "blahblah"

        event["context"]["System"]["apiAccessToken"] = (
            "eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiIsImtpZCI6IjEifQ.eyJhdWQiOiJodHRwczovL2FwaS5hbWF6b25hbGV4YS5jb20iLCJpc3MiOiJBbGV4YVNraWxsS2l0Iiwic3ViIjoiYW16bjEuYXNrLnNraWxsLmQxYjAxYzc4LTZmYTYtNGMwNy1hZTc5LWIzYWUzNjk2OWI1MCIsImV4cCI6MTYwMjExMDcxMSwiaWF0IjoxNjAyMTEwNDExLCJuYmYiOjE2MDIxMTA0MTEsInByaXZhdGVDbGFpbXMiOnsiY29udGV4dCI6IkFBQUFBQUFBQUFDc1dvalFEMjJ6UWFVbUJ0WUg5OWhrVVFFQUFBQUFBQUF4MzBWT09adTVwY0xsZHRJTE9YSytnWW1SN0VNK0tTRlQyVGlvQXoyd1VuNmlMb3hQaTdMOXpPRFFzazdTazR0SDZuVEJGMllMWm00RGJyZVpMdGFZcDRWb1FBQUNLZDhFaXE0L1htOWtPZ0kvK0tmQTRWQzZkMlNhVnZTWXYxbXJIYXZCS1FGWFpSODBGRnQxNkh5bDBOdEpVdXBpZ2tvaXhybG1RMDBRS1NWVVdRbFJueE9xRjUrWXB5OEdnQTZ1QzFEdXFkTklsTUkvL2FpVDg5S2ZrbEFKN1JmZWdnMzRxa3lkNnQ3ME4zRFN3aEJpSXRaL21idkZ1dVhIOFlZMHRVM1E1aXgyVzlrOEJvbkwxTSs0Q3R3dUtBRXJYaGtKYzRzb1FaOWJMWDJWQjNid05udjZuWW04Q1RxbVFQUFdYL0pkU0tpc0gvYzJmS2tQZHZJRlgxMnRXU2pncmxFMTE2WU5QRmNKZmFOa1NqSVpLaGtiaHJTYStURi9hbUdDWGNhNnFSN3BJSDhNSDBkY1Jld09MQzRleUc1YlRWK2o0eVNKbnBNRytGWDJwQ3VBRFA0MGJJcUY5aDdYdnJSdiIsImNvbnNlbnRUb2tlbiI6IkF0emF8SXdFQklBX25xX2pYdHdBMnlBSk9iaTZqcUxMYmlFcGJHQnNvaTNPNzB5S2hjNUh2UDRZTF90ZFV6dlc1QkRvU0U1OTU0UTFxby03WkJXOHBWbHA4M1o2d0dXWjFpYXA0LXk4dHpVa3dSOUJZVlRJRVo0V09WUmZ3bzNwWHRhdlM1MG54T1Y2QWVUd012TTYwMW9aS0ZMWEdfanhLM0NRVEhaNDg5amdUb0RQdlpkTXJkdmFkdm5yVVh6MXpiUHFwalducHNOOEpPNjVvSVIyWnJwMkYxRGQ2Y3U0U0tBQjljclg1a3JEOVp6Z0ZleXQ5RGVGd3IzU29Tb3BhQWJvZEtJUlFqU1BhR3RJM1l2bGN0WXpBbG1ZdHVTdmhma0MzN1RfQ0EtR1NlZjdXbFBpbkJRIiwiZGV2aWNlSWQiOiJhbXpuMS5hc2suZGV2aWNlLkFIV1pZVE1UTUNNR1hWTkZXQjRPNzJURlBEVFpFVlRSRlZMSkRPRVM3Rkk2M1JHSFdEQ0FQSUFUQUJSQ1VJRzJWRDdIVUNEVVFTSlZRS1dLWURVWVA2MzVVV0VDU0FaRlBUTTVNSUhRRFFUWUI3S1Q3RlZCSzNGVlNJRDZPTVJGU0tPTlk1V1k1TEFUVTVTVFBVMzVFV1NSNkRQRk40S1NYV1ZaUDdRR0ZHWkpKNjNaS0FQNDQiLCJ1c2VySWQiOiJhbXpuMS5hc2suYWNjb3VudC5BRVQ1UVlIM1gyREJMNUxWSkJON04yQldTNUU0T0lURDZIN1IyN0ZSRFdSS0NHNEpOU0NHWkpKWldKUDdCMkpLVFNYTEJHUzdCT05KTk5KRUpFWDJURFU2MldVWFRXN0RTQ0RDWVRCS1pFUEhCUkdPWjI3Q1RaNkhMWFRBQ09LQUVXQ0hCS1BTTjVHQUROQ0RXVFY0NlUzQ1c2VU82U09TNzdLT1paMllHM0FOTlNWNDdFWU9NM1NRUVdZU0I2VVdXTkpBTE02UldJUFlSRlkifX0.QK9mxalr7hwgE_qiSvuLc9V8HKMIaa9uXF2EV3VLHWaSbhHJDvLpYU5SWAyOE6iAhJtjKxrBOcGBlNHReKkSauHpagQkkUruL7-KvboSl67ZvLNuNCBaTa_ePDyePeDygfEmgPFvKsc5muzmdhhxmy5USWMbzF8kTnUlMJSlnGZaaxY41Ifeg2_w3nahyvW6YkG9AtN6h2uZzeFYwTZ0H7uxolKkSEyksKmcyst5XzCh-hSRP9TymjekR7mHlAjcFkpDxEjbwGiWQNRHRPeYcnTd3saD5E47StUhM0zBQ1g8Hc5nGiXV7_GoPeJa_qPx2gJ_cxRb541ITTKcJNUw7g",
        )

        success_titles = [pa.SWEET_TITLE, pa.SUCCESS_TITLE]
        evaluate_handler_for_intents(
            pa.handler,
            event=event,
            context={},
            success_titles=success_titles,
            intent_response=intent_response,
        )

    except Exception as e:
        print(e)
        raise

    # un-monkey patch
    DeviceAddressServiceClient.get_full_address = saved_method
    assert True


def test_loc_supported_no_loc_access_no_address_access():
    # user has geolocation supported, hasn't granted access to that or address

    try:
        with open("tests/event_shell.json", "r", encoding="utf8") as file:
            event = loads(file.read())

        event_permissions = event["context"]["System"]["user"]["permissions"]
        event["context"]["geolocation"] = "blahblah"  # loc supported
        event_permissions["scopes"] = {
            "alexa::devices:all:geolocation:read": {
                "status": PermissionStatus.DENIED.value
            }
        }

        evaluate_handler_for_intents(
            pa.handler,
            event=event,
            context={},
            permissions=[pa.GEOLOCATION_PERMISSIONS],
            intent_response=intent_response,
        )

    except Exception as e:
        print(e)
        raise

    assert True


def test_loc_unsupported_address_access():
    # user has no geolocation support, but we have address access
    saved_method = DeviceAddressServiceClient.get_full_address
    DeviceAddressServiceClient.get_full_address = mp_get_full_address

    try:
        with open("tests/event_shell.json", "r", encoding="utf8") as file:
            event = loads(file.read())

        event_permissions = event["context"]["System"]["user"]["permissions"]
        event["context"]["geolocation"] = None  # loc unsupported

        success_titles = [pa.SWEET_TITLE, pa.SUCCESS_TITLE]
        evaluate_handler_for_intents(
            pa.handler,
            event=event,
            context={},
            success_titles=success_titles,
            intent_response=intent_response,
        )

    except Exception as e:
        print(e)
        raise

    # un-monkey patch
    DeviceAddressServiceClient.get_full_address = saved_method

    assert True  # Outcome D: We're good -> Results with address coord


def test_loc_unsupported_no_address_access():
    # user has no geolocation support, and we have no address access
    try:
        with open("tests/event_shell.json", "r", encoding="utf8") as file:
            event = loads(file.read())

        event_permissions = event["context"]["System"]["user"]["permissions"]
        event["context"]["geolocation"] = None

        evaluate_handler_for_intents(
            pa.handler,
            event=event,
            context={},
            permissions=[pa.ADDRESS_PERMISSIONS],
            intent_response=intent_response,
        )

    except Exception as e:
        print(e)
        raise

    assert True


def test_random_coordinates():
    # test a few random places in the world for kicks
    coords = (
        Coordinate(
            latitude_in_degrees=uniform(-90.0, 90.0),
            longitude_in_degrees=uniform(-180.0, 180.0),
        )
        for x in range(3)
    )

    for coord in coords:
        test_loc_supported_loc_access(coord)

    assert True


def test_loc_unsupported_address_access_bad():
    # we have no geolocation access, and the address input is bad somehow

    # Need to monkey patch function to return address
    saved_method = DeviceAddressServiceClient.get_full_address
    DeviceAddressServiceClient.get_full_address = mp_get_full_address_bad

    try:
        with open("tests/event_shell.json", "r", encoding="utf8") as file:
            event = loads(file.read())

        event_permissions = event["context"]["System"]["user"]["permissions"]
        event["context"]["geolocation"] = None  # loc unsupported

        success_titles = [pa.NOTIFY_BAD_ADDRESS_TITLE]
        evaluate_handler_for_intents(
            pa.handler,
            event=event,
            context={},
            success_titles=success_titles,
            intent_response=intent_response,
        )

    except Exception as e:
        print(e)
        raise

    # un-monkey patch
    DeviceAddressServiceClient.get_full_address = saved_method
