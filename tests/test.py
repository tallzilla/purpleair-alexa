import pytest
import purpleair_alexa as pa
from json import loads, dumps
from ask_sdk_core import response_helper
from ask_sdk_model.services.service_client_factory import DeviceAddressServiceClient
from ask_sdk_model.services.device_address.address import Address
from ask_sdk_model.permission_status import PermissionStatus
from ask_sdk_model.interfaces.geolocation.coordinate import Coordinate
from random import uniform

rb = response_helper.ResponseFactory()

test_coordinate = Coordinate(latitude_in_degrees=37.363796, \
            longitude_in_degrees=-121.77012, accuracy_in_meters=65.0)

def mp_get_full_address(self, device_id, **kwargs):
    with open('tests/address.json', 'r', encoding="utf8") as file:
        address_dict = loads(file.read())
        return Address(
            address_line1=address_dict['address_line1'],
            address_line2=address_dict['address_line2'], 
            address_line3=address_dict['address_line3'], 
            country_code=address_dict['country_code'], 
            state_or_region=address_dict['state_or_region'], 
            city=address_dict['city'], 
            district_or_county=address_dict['district_or_county'], 
            postal_code=address_dict['postal_code'])

def mp_get_full_address_bad(self, device_id, **kwargs):
    with open('tests/address_bad.json', 'r', encoding="utf8") as file:
        address_dict = loads(file.read())
        return Address(
            address_line1=address_dict['address_line1'],
            address_line2=address_dict['address_line2'], 
            address_line3=address_dict['address_line3'], 
            country_code=address_dict['country_code'], 
            state_or_region=address_dict['state_or_region'], 
            city=address_dict['city'], 
            district_or_county=address_dict['district_or_county'], 
            postal_code=address_dict['postal_code'])

    # The decision tree here is non-trivial. Here's what it looks like:

        # Are location services supported?
        # Yes
          # Do we have location services access?
          # Yes
            # We're good -> Outcome A: results w/ geo coord
          # No
            # Do we have address access?
            # Yes
              # We're good -> Outcome B: results w/ address coord
            # No
              # Prompt for geolocation access -> Outcome C: prompt for geolocation card
        # No
          # Do we have address access?
          # Yes
            # We're good -> Results with address coord
          # No
            # Prompt for address access -> Outcome D: prompt for address card

#ls = location supported
#

# We're good -> Outcome A: results w/ geo coord
def test_loc_supported_loc_access(coordinate=test_coordinate):
    try:
        with open('tests/event_shell.json', 'r', encoding="utf8") as file:
            event = loads(file.read())

        event['context']['System']['user']['permissions']['scopes'] = \
            {'alexa::devices:all:geolocation:read': {'status': PermissionStatus.GRANTED.value}}

        event['context']['geolocation'] = {'coordinate': coordinate.to_dict()}

        handler_output = pa.handler(event=event, context = {})
        response = handler_output['response']
    except Exception as e:
        print(e)
        assert False

    if response['card']['title'] == pa.SUCCESS_TITLE:
        assert True # We're good -> Outcome A: results w/ geo coord
    else:
        assert False


def test_loc_supported_no_loc_access_address_access():

    #Need to monkey patch function to return address 
    saved_method = DeviceAddressServiceClient.get_full_address
    DeviceAddressServiceClient.get_full_address = mp_get_full_address

    try:
        with open('tests/event_shell.json', 'r', encoding="utf8") as file:
            event = loads(file.read())

        event_permissions = event['context']['System']['user']['permissions']

        event_permissions['scopes'] = \
            {'alexa::devices:all:geolocation:read': {'status': PermissionStatus.DENIED.value}}

        event['context']['geolocation'] = 'blahblah'
                    
        event['context']['System']['apiAccessToken'] = "eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiIsImtpZCI6IjEifQ.eyJhdWQiOiJodHRwczovL2FwaS5hbWF6b25hbGV4YS5jb20iLCJpc3MiOiJBbGV4YVNraWxsS2l0Iiwic3ViIjoiYW16bjEuYXNrLnNraWxsLmQxYjAxYzc4LTZmYTYtNGMwNy1hZTc5LWIzYWUzNjk2OWI1MCIsImV4cCI6MTYwMjExMDcxMSwiaWF0IjoxNjAyMTEwNDExLCJuYmYiOjE2MDIxMTA0MTEsInByaXZhdGVDbGFpbXMiOnsiY29udGV4dCI6IkFBQUFBQUFBQUFDc1dvalFEMjJ6UWFVbUJ0WUg5OWhrVVFFQUFBQUFBQUF4MzBWT09adTVwY0xsZHRJTE9YSytnWW1SN0VNK0tTRlQyVGlvQXoyd1VuNmlMb3hQaTdMOXpPRFFzazdTazR0SDZuVEJGMllMWm00RGJyZVpMdGFZcDRWb1FBQUNLZDhFaXE0L1htOWtPZ0kvK0tmQTRWQzZkMlNhVnZTWXYxbXJIYXZCS1FGWFpSODBGRnQxNkh5bDBOdEpVdXBpZ2tvaXhybG1RMDBRS1NWVVdRbFJueE9xRjUrWXB5OEdnQTZ1QzFEdXFkTklsTUkvL2FpVDg5S2ZrbEFKN1JmZWdnMzRxa3lkNnQ3ME4zRFN3aEJpSXRaL21idkZ1dVhIOFlZMHRVM1E1aXgyVzlrOEJvbkwxTSs0Q3R3dUtBRXJYaGtKYzRzb1FaOWJMWDJWQjNid05udjZuWW04Q1RxbVFQUFdYL0pkU0tpc0gvYzJmS2tQZHZJRlgxMnRXU2pncmxFMTE2WU5QRmNKZmFOa1NqSVpLaGtiaHJTYStURi9hbUdDWGNhNnFSN3BJSDhNSDBkY1Jld09MQzRleUc1YlRWK2o0eVNKbnBNRytGWDJwQ3VBRFA0MGJJcUY5aDdYdnJSdiIsImNvbnNlbnRUb2tlbiI6IkF0emF8SXdFQklBX25xX2pYdHdBMnlBSk9iaTZqcUxMYmlFcGJHQnNvaTNPNzB5S2hjNUh2UDRZTF90ZFV6dlc1QkRvU0U1OTU0UTFxby03WkJXOHBWbHA4M1o2d0dXWjFpYXA0LXk4dHpVa3dSOUJZVlRJRVo0V09WUmZ3bzNwWHRhdlM1MG54T1Y2QWVUd012TTYwMW9aS0ZMWEdfanhLM0NRVEhaNDg5amdUb0RQdlpkTXJkdmFkdm5yVVh6MXpiUHFwalducHNOOEpPNjVvSVIyWnJwMkYxRGQ2Y3U0U0tBQjljclg1a3JEOVp6Z0ZleXQ5RGVGd3IzU29Tb3BhQWJvZEtJUlFqU1BhR3RJM1l2bGN0WXpBbG1ZdHVTdmhma0MzN1RfQ0EtR1NlZjdXbFBpbkJRIiwiZGV2aWNlSWQiOiJhbXpuMS5hc2suZGV2aWNlLkFIV1pZVE1UTUNNR1hWTkZXQjRPNzJURlBEVFpFVlRSRlZMSkRPRVM3Rkk2M1JHSFdEQ0FQSUFUQUJSQ1VJRzJWRDdIVUNEVVFTSlZRS1dLWURVWVA2MzVVV0VDU0FaRlBUTTVNSUhRRFFUWUI3S1Q3RlZCSzNGVlNJRDZPTVJGU0tPTlk1V1k1TEFUVTVTVFBVMzVFV1NSNkRQRk40S1NYV1ZaUDdRR0ZHWkpKNjNaS0FQNDQiLCJ1c2VySWQiOiJhbXpuMS5hc2suYWNjb3VudC5BRVQ1UVlIM1gyREJMNUxWSkJON04yQldTNUU0T0lURDZIN1IyN0ZSRFdSS0NHNEpOU0NHWkpKWldKUDdCMkpLVFNYTEJHUzdCT05KTk5KRUpFWDJURFU2MldVWFRXN0RTQ0RDWVRCS1pFUEhCUkdPWjI3Q1RaNkhMWFRBQ09LQUVXQ0hCS1BTTjVHQUROQ0RXVFY0NlUzQ1c2VU82U09TNzdLT1paMllHM0FOTlNWNDdFWU9NM1NRUVdZU0I2VVdXTkpBTE02UldJUFlSRlkifX0.QK9mxalr7hwgE_qiSvuLc9V8HKMIaa9uXF2EV3VLHWaSbhHJDvLpYU5SWAyOE6iAhJtjKxrBOcGBlNHReKkSauHpagQkkUruL7-KvboSl67ZvLNuNCBaTa_ePDyePeDygfEmgPFvKsc5muzmdhhxmy5USWMbzF8kTnUlMJSlnGZaaxY41Ifeg2_w3nahyvW6YkG9AtN6h2uZzeFYwTZ0H7uxolKkSEyksKmcyst5XzCh-hSRP9TymjekR7mHlAjcFkpDxEjbwGiWQNRHRPeYcnTd3saD5E47StUhM0zBQ1g8Hc5nGiXV7_GoPeJa_qPx2gJ_cxRb541ITTKcJNUw7g",

        handler_output = pa.handler(event=event, context = {})
        response = handler_output['response']
 
    except Exception as e:
        print(e)
        assert False

    #un-monkey patch
    DeviceAddressServiceClient.get_full_address = saved_method

    if response['card']['title'] == pa.SUCCESS_TITLE:
        assert True  # We're good -> Outcome B: results w/ address coord
    else:
        assert False


def test_loc_supported_no_loc_access_no_address_access():

    #Need to monkey patch function to return address 
    #saved_method = DeviceAddressServiceClient.get_full_address
    #DeviceAddressServiceClient.get_full_address = mp_get_full_address

    try:
        with open('tests/event_shell.json', 'r', encoding="utf8") as file:
            event = loads(file.read())

        event_permissions = event['context']['System']['user']['permissions']
        event['context']['geolocation'] = 'blahblah' # loc supported

        #no loc access
        event_permissions['scopes'] = \
            {'alexa::devices:all:geolocation:read': {'status': PermissionStatus.DENIED.value}}

        #no address access           
        #event['context']['System']['apiAccessToken'] = "eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiIsImtpZCI6IjEifQ.eyJhdWQiOiJodHRwczovL2FwaS5hbWF6b25hbGV4YS5jb20iLCJpc3MiOiJBbGV4YVNraWxsS2l0Iiwic3ViIjoiYW16bjEuYXNrLnNraWxsLmQxYjAxYzc4LTZmYTYtNGMwNy1hZTc5LWIzYWUzNjk2OWI1MCIsImV4cCI6MTYwMjExMDcxMSwiaWF0IjoxNjAyMTEwNDExLCJuYmYiOjE2MDIxMTA0MTEsInByaXZhdGVDbGFpbXMiOnsiY29udGV4dCI6IkFBQUFBQUFBQUFDc1dvalFEMjJ6UWFVbUJ0WUg5OWhrVVFFQUFBQUFBQUF4MzBWT09adTVwY0xsZHRJTE9YSytnWW1SN0VNK0tTRlQyVGlvQXoyd1VuNmlMb3hQaTdMOXpPRFFzazdTazR0SDZuVEJGMllMWm00RGJyZVpMdGFZcDRWb1FBQUNLZDhFaXE0L1htOWtPZ0kvK0tmQTRWQzZkMlNhVnZTWXYxbXJIYXZCS1FGWFpSODBGRnQxNkh5bDBOdEpVdXBpZ2tvaXhybG1RMDBRS1NWVVdRbFJueE9xRjUrWXB5OEdnQTZ1QzFEdXFkTklsTUkvL2FpVDg5S2ZrbEFKN1JmZWdnMzRxa3lkNnQ3ME4zRFN3aEJpSXRaL21idkZ1dVhIOFlZMHRVM1E1aXgyVzlrOEJvbkwxTSs0Q3R3dUtBRXJYaGtKYzRzb1FaOWJMWDJWQjNid05udjZuWW04Q1RxbVFQUFdYL0pkU0tpc0gvYzJmS2tQZHZJRlgxMnRXU2pncmxFMTE2WU5QRmNKZmFOa1NqSVpLaGtiaHJTYStURi9hbUdDWGNhNnFSN3BJSDhNSDBkY1Jld09MQzRleUc1YlRWK2o0eVNKbnBNRytGWDJwQ3VBRFA0MGJJcUY5aDdYdnJSdiIsImNvbnNlbnRUb2tlbiI6IkF0emF8SXdFQklBX25xX2pYdHdBMnlBSk9iaTZqcUxMYmlFcGJHQnNvaTNPNzB5S2hjNUh2UDRZTF90ZFV6dlc1QkRvU0U1OTU0UTFxby03WkJXOHBWbHA4M1o2d0dXWjFpYXA0LXk4dHpVa3dSOUJZVlRJRVo0V09WUmZ3bzNwWHRhdlM1MG54T1Y2QWVUd012TTYwMW9aS0ZMWEdfanhLM0NRVEhaNDg5amdUb0RQdlpkTXJkdmFkdm5yVVh6MXpiUHFwalducHNOOEpPNjVvSVIyWnJwMkYxRGQ2Y3U0U0tBQjljclg1a3JEOVp6Z0ZleXQ5RGVGd3IzU29Tb3BhQWJvZEtJUlFqU1BhR3RJM1l2bGN0WXpBbG1ZdHVTdmhma0MzN1RfQ0EtR1NlZjdXbFBpbkJRIiwiZGV2aWNlSWQiOiJhbXpuMS5hc2suZGV2aWNlLkFIV1pZVE1UTUNNR1hWTkZXQjRPNzJURlBEVFpFVlRSRlZMSkRPRVM3Rkk2M1JHSFdEQ0FQSUFUQUJSQ1VJRzJWRDdIVUNEVVFTSlZRS1dLWURVWVA2MzVVV0VDU0FaRlBUTTVNSUhRRFFUWUI3S1Q3RlZCSzNGVlNJRDZPTVJGU0tPTlk1V1k1TEFUVTVTVFBVMzVFV1NSNkRQRk40S1NYV1ZaUDdRR0ZHWkpKNjNaS0FQNDQiLCJ1c2VySWQiOiJhbXpuMS5hc2suYWNjb3VudC5BRVQ1UVlIM1gyREJMNUxWSkJON04yQldTNUU0T0lURDZIN1IyN0ZSRFdSS0NHNEpOU0NHWkpKWldKUDdCMkpLVFNYTEJHUzdCT05KTk5KRUpFWDJURFU2MldVWFRXN0RTQ0RDWVRCS1pFUEhCUkdPWjI3Q1RaNkhMWFRBQ09LQUVXQ0hCS1BTTjVHQUROQ0RXVFY0NlUzQ1c2VU82U09TNzdLT1paMllHM0FOTlNWNDdFWU9NM1NRUVdZU0I2VVdXTkpBTE02UldJUFlSRlkifX0.QK9mxalr7hwgE_qiSvuLc9V8HKMIaa9uXF2EV3VLHWaSbhHJDvLpYU5SWAyOE6iAhJtjKxrBOcGBlNHReKkSauHpagQkkUruL7-KvboSl67ZvLNuNCBaTa_ePDyePeDygfEmgPFvKsc5muzmdhhxmy5USWMbzF8kTnUlMJSlnGZaaxY41Ifeg2_w3nahyvW6YkG9AtN6h2uZzeFYwTZ0H7uxolKkSEyksKmcyst5XzCh-hSRP9TymjekR7mHlAjcFkpDxEjbwGiWQNRHRPeYcnTd3saD5E47StUhM0zBQ1g8Hc5nGiXV7_GoPeJa_qPx2gJ_cxRb541ITTKcJNUw7g",

        handler_output = pa.handler(event=event, context = {})
        response = handler_output['response']
 
    except Exception as e:
        print(e)
        assert False

    #un-monkey patch
    #DeviceAddressServiceClient.get_full_address = saved_method

    if response['card']['permissions'] == pa.geolocation_permissions:
        assert True   # Prompt for geolocation access -> Outcome C: prompt for geolocation card
    else:
        assert False

def test_loc_unsupported_address_access():

    #Need to monkey patch function to return address
    saved_method = DeviceAddressServiceClient.get_full_address
    DeviceAddressServiceClient.get_full_address = mp_get_full_address

    try:
        with open('tests/event_shell.json', 'r', encoding="utf8") as file:
            event = loads(file.read())

        event_permissions = event['context']['System']['user']['permissions']
        event['context']['geolocation'] = None # loc unsupported

        #address access
        #event['context']['System']['apiAccessToken'] = "eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiIsImtpZCI6IjEifQ.eyJhdWQiOiJodHRwczovL2FwaS5hbWF6b25hbGV4YS5jb20iLCJpc3MiOiJBbGV4YVNraWxsS2l0Iiwic3ViIjoiYW16bjEuYXNrLnNraWxsLmQxYjAxYzc4LTZmYTYtNGMwNy1hZTc5LWIzYWUzNjk2OWI1MCIsImV4cCI6MTYwMjExMDcxMSwiaWF0IjoxNjAyMTEwNDExLCJuYmYiOjE2MDIxMTA0MTEsInByaXZhdGVDbGFpbXMiOnsiY29udGV4dCI6IkFBQUFBQUFBQUFDc1dvalFEMjJ6UWFVbUJ0WUg5OWhrVVFFQUFBQUFBQUF4MzBWT09adTVwY0xsZHRJTE9YSytnWW1SN0VNK0tTRlQyVGlvQXoyd1VuNmlMb3hQaTdMOXpPRFFzazdTazR0SDZuVEJGMllMWm00RGJyZVpMdGFZcDRWb1FBQUNLZDhFaXE0L1htOWtPZ0kvK0tmQTRWQzZkMlNhVnZTWXYxbXJIYXZCS1FGWFpSODBGRnQxNkh5bDBOdEpVdXBpZ2tvaXhybG1RMDBRS1NWVVdRbFJueE9xRjUrWXB5OEdnQTZ1QzFEdXFkTklsTUkvL2FpVDg5S2ZrbEFKN1JmZWdnMzRxa3lkNnQ3ME4zRFN3aEJpSXRaL21idkZ1dVhIOFlZMHRVM1E1aXgyVzlrOEJvbkwxTSs0Q3R3dUtBRXJYaGtKYzRzb1FaOWJMWDJWQjNid05udjZuWW04Q1RxbVFQUFdYL0pkU0tpc0gvYzJmS2tQZHZJRlgxMnRXU2pncmxFMTE2WU5QRmNKZmFOa1NqSVpLaGtiaHJTYStURi9hbUdDWGNhNnFSN3BJSDhNSDBkY1Jld09MQzRleUc1YlRWK2o0eVNKbnBNRytGWDJwQ3VBRFA0MGJJcUY5aDdYdnJSdiIsImNvbnNlbnRUb2tlbiI6IkF0emF8SXdFQklBX25xX2pYdHdBMnlBSk9iaTZqcUxMYmlFcGJHQnNvaTNPNzB5S2hjNUh2UDRZTF90ZFV6dlc1QkRvU0U1OTU0UTFxby03WkJXOHBWbHA4M1o2d0dXWjFpYXA0LXk4dHpVa3dSOUJZVlRJRVo0V09WUmZ3bzNwWHRhdlM1MG54T1Y2QWVUd012TTYwMW9aS0ZMWEdfanhLM0NRVEhaNDg5amdUb0RQdlpkTXJkdmFkdm5yVVh6MXpiUHFwalducHNOOEpPNjVvSVIyWnJwMkYxRGQ2Y3U0U0tBQjljclg1a3JEOVp6Z0ZleXQ5RGVGd3IzU29Tb3BhQWJvZEtJUlFqU1BhR3RJM1l2bGN0WXpBbG1ZdHVTdmhma0MzN1RfQ0EtR1NlZjdXbFBpbkJRIiwiZGV2aWNlSWQiOiJhbXpuMS5hc2suZGV2aWNlLkFIV1pZVE1UTUNNR1hWTkZXQjRPNzJURlBEVFpFVlRSRlZMSkRPRVM3Rkk2M1JHSFdEQ0FQSUFUQUJSQ1VJRzJWRDdIVUNEVVFTSlZRS1dLWURVWVA2MzVVV0VDU0FaRlBUTTVNSUhRRFFUWUI3S1Q3RlZCSzNGVlNJRDZPTVJGU0tPTlk1V1k1TEFUVTVTVFBVMzVFV1NSNkRQRk40S1NYV1ZaUDdRR0ZHWkpKNjNaS0FQNDQiLCJ1c2VySWQiOiJhbXpuMS5hc2suYWNjb3VudC5BRVQ1UVlIM1gyREJMNUxWSkJON04yQldTNUU0T0lURDZIN1IyN0ZSRFdSS0NHNEpOU0NHWkpKWldKUDdCMkpLVFNYTEJHUzdCT05KTk5KRUpFWDJURFU2MldVWFRXN0RTQ0RDWVRCS1pFUEhCUkdPWjI3Q1RaNkhMWFRBQ09LQUVXQ0hCS1BTTjVHQUROQ0RXVFY0NlUzQ1c2VU82U09TNzdLT1paMllHM0FOTlNWNDdFWU9NM1NRUVdZU0I2VVdXTkpBTE02UldJUFlSRlkifX0.QK9mxalr7hwgE_qiSvuLc9V8HKMIaa9uXF2EV3VLHWaSbhHJDvLpYU5SWAyOE6iAhJtjKxrBOcGBlNHReKkSauHpagQkkUruL7-KvboSl67ZvLNuNCBaTa_ePDyePeDygfEmgPFvKsc5muzmdhhxmy5USWMbzF8kTnUlMJSlnGZaaxY41Ifeg2_w3nahyvW6YkG9AtN6h2uZzeFYwTZ0H7uxolKkSEyksKmcyst5XzCh-hSRP9TymjekR7mHlAjcFkpDxEjbwGiWQNRHRPeYcnTd3saD5E47StUhM0zBQ1g8Hc5nGiXV7_GoPeJa_qPx2gJ_cxRb541ITTKcJNUw7g",
        handler_output = pa.handler(event=event, context = {})
        response = handler_output['response']
 
    except Exception as e:
        print(e)
        assert False

    #un-monkey patch
    DeviceAddressServiceClient.get_full_address = saved_method

    if response['card']['title'] == pa.SUCCESS_TITLE:
        assert True # Outcome D: We're good -> Results with address coord
    else:
        assert False

def test_loc_unsupported_no_address_access():

    try:
        with open('tests/event_shell.json', 'r', encoding="utf8") as file:
            event = loads(file.read())

        event_permissions = event['context']['System']['user']['permissions']
        event['context']['geolocation'] = None # loc unsupported

        #no address access
        #event['context']['System']['apiAccessToken'] = "eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiIsImtpZCI6IjEifQ.eyJhdWQiOiJodHRwczovL2FwaS5hbWF6b25hbGV4YS5jb20iLCJpc3MiOiJBbGV4YVNraWxsS2l0Iiwic3ViIjoiYW16bjEuYXNrLnNraWxsLmQxYjAxYzc4LTZmYTYtNGMwNy1hZTc5LWIzYWUzNjk2OWI1MCIsImV4cCI6MTYwMjExMDcxMSwiaWF0IjoxNjAyMTEwNDExLCJuYmYiOjE2MDIxMTA0MTEsInByaXZhdGVDbGFpbXMiOnsiY29udGV4dCI6IkFBQUFBQUFBQUFDc1dvalFEMjJ6UWFVbUJ0WUg5OWhrVVFFQUFBQUFBQUF4MzBWT09adTVwY0xsZHRJTE9YSytnWW1SN0VNK0tTRlQyVGlvQXoyd1VuNmlMb3hQaTdMOXpPRFFzazdTazR0SDZuVEJGMllMWm00RGJyZVpMdGFZcDRWb1FBQUNLZDhFaXE0L1htOWtPZ0kvK0tmQTRWQzZkMlNhVnZTWXYxbXJIYXZCS1FGWFpSODBGRnQxNkh5bDBOdEpVdXBpZ2tvaXhybG1RMDBRS1NWVVdRbFJueE9xRjUrWXB5OEdnQTZ1QzFEdXFkTklsTUkvL2FpVDg5S2ZrbEFKN1JmZWdnMzRxa3lkNnQ3ME4zRFN3aEJpSXRaL21idkZ1dVhIOFlZMHRVM1E1aXgyVzlrOEJvbkwxTSs0Q3R3dUtBRXJYaGtKYzRzb1FaOWJMWDJWQjNid05udjZuWW04Q1RxbVFQUFdYL0pkU0tpc0gvYzJmS2tQZHZJRlgxMnRXU2pncmxFMTE2WU5QRmNKZmFOa1NqSVpLaGtiaHJTYStURi9hbUdDWGNhNnFSN3BJSDhNSDBkY1Jld09MQzRleUc1YlRWK2o0eVNKbnBNRytGWDJwQ3VBRFA0MGJJcUY5aDdYdnJSdiIsImNvbnNlbnRUb2tlbiI6IkF0emF8SXdFQklBX25xX2pYdHdBMnlBSk9iaTZqcUxMYmlFcGJHQnNvaTNPNzB5S2hjNUh2UDRZTF90ZFV6dlc1QkRvU0U1OTU0UTFxby03WkJXOHBWbHA4M1o2d0dXWjFpYXA0LXk4dHpVa3dSOUJZVlRJRVo0V09WUmZ3bzNwWHRhdlM1MG54T1Y2QWVUd012TTYwMW9aS0ZMWEdfanhLM0NRVEhaNDg5amdUb0RQdlpkTXJkdmFkdm5yVVh6MXpiUHFwalducHNOOEpPNjVvSVIyWnJwMkYxRGQ2Y3U0U0tBQjljclg1a3JEOVp6Z0ZleXQ5RGVGd3IzU29Tb3BhQWJvZEtJUlFqU1BhR3RJM1l2bGN0WXpBbG1ZdHVTdmhma0MzN1RfQ0EtR1NlZjdXbFBpbkJRIiwiZGV2aWNlSWQiOiJhbXpuMS5hc2suZGV2aWNlLkFIV1pZVE1UTUNNR1hWTkZXQjRPNzJURlBEVFpFVlRSRlZMSkRPRVM3Rkk2M1JHSFdEQ0FQSUFUQUJSQ1VJRzJWRDdIVUNEVVFTSlZRS1dLWURVWVA2MzVVV0VDU0FaRlBUTTVNSUhRRFFUWUI3S1Q3RlZCSzNGVlNJRDZPTVJGU0tPTlk1V1k1TEFUVTVTVFBVMzVFV1NSNkRQRk40S1NYV1ZaUDdRR0ZHWkpKNjNaS0FQNDQiLCJ1c2VySWQiOiJhbXpuMS5hc2suYWNjb3VudC5BRVQ1UVlIM1gyREJMNUxWSkJON04yQldTNUU0T0lURDZIN1IyN0ZSRFdSS0NHNEpOU0NHWkpKWldKUDdCMkpLVFNYTEJHUzdCT05KTk5KRUpFWDJURFU2MldVWFRXN0RTQ0RDWVRCS1pFUEhCUkdPWjI3Q1RaNkhMWFRBQ09LQUVXQ0hCS1BTTjVHQUROQ0RXVFY0NlUzQ1c2VU82U09TNzdLT1paMllHM0FOTlNWNDdFWU9NM1NRUVdZU0I2VVdXTkpBTE02UldJUFlSRlkifX0.QK9mxalr7hwgE_qiSvuLc9V8HKMIaa9uXF2EV3VLHWaSbhHJDvLpYU5SWAyOE6iAhJtjKxrBOcGBlNHReKkSauHpagQkkUruL7-KvboSl67ZvLNuNCBaTa_ePDyePeDygfEmgPFvKsc5muzmdhhxmy5USWMbzF8kTnUlMJSlnGZaaxY41Ifeg2_w3nahyvW6YkG9AtN6h2uZzeFYwTZ0H7uxolKkSEyksKmcyst5XzCh-hSRP9TymjekR7mHlAjcFkpDxEjbwGiWQNRHRPeYcnTd3saD5E47StUhM0zBQ1g8Hc5nGiXV7_GoPeJa_qPx2gJ_cxRb541ITTKcJNUw7g",
        handler_output = pa.handler(event=event, context = {})
        response = handler_output['response']
 
    except Exception as e:
        print(e)
        assert False

    if response['card']['permissions'] == pa.address_permissions:
        assert True   # Prompt for geolocation access -> Outcome C: prompt for geolocation card
    else:
        assert False


def test_random_coordinates():
    coords = (Coordinate(latitude_in_degrees=uniform(-90, 90), \
            longitude_in_degrees=uniform(-180,180)) \
            for x in range(10))

    for coord in coords: 
        test_loc_supported_loc_access(coord)


def test_loc_unsupported_address_access_bad():

    #Need to monkey patch function to return address
    saved_method = DeviceAddressServiceClient.get_full_address
    DeviceAddressServiceClient.get_full_address = mp_get_full_address_bad

    try:
        with open('tests/event_shell.json', 'r', encoding="utf8") as file:
            event = loads(file.read())

        event_permissions = event['context']['System']['user']['permissions']
        event['context']['geolocation'] = None # loc unsupported

        #address access
        #event['context']['System']['apiAccessToken'] = "eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiIsImtpZCI6IjEifQ.eyJhdWQiOiJodHRwczovL2FwaS5hbWF6b25hbGV4YS5jb20iLCJpc3MiOiJBbGV4YVNraWxsS2l0Iiwic3ViIjoiYW16bjEuYXNrLnNraWxsLmQxYjAxYzc4LTZmYTYtNGMwNy1hZTc5LWIzYWUzNjk2OWI1MCIsImV4cCI6MTYwMjExMDcxMSwiaWF0IjoxNjAyMTEwNDExLCJuYmYiOjE2MDIxMTA0MTEsInByaXZhdGVDbGFpbXMiOnsiY29udGV4dCI6IkFBQUFBQUFBQUFDc1dvalFEMjJ6UWFVbUJ0WUg5OWhrVVFFQUFBQUFBQUF4MzBWT09adTVwY0xsZHRJTE9YSytnWW1SN0VNK0tTRlQyVGlvQXoyd1VuNmlMb3hQaTdMOXpPRFFzazdTazR0SDZuVEJGMllMWm00RGJyZVpMdGFZcDRWb1FBQUNLZDhFaXE0L1htOWtPZ0kvK0tmQTRWQzZkMlNhVnZTWXYxbXJIYXZCS1FGWFpSODBGRnQxNkh5bDBOdEpVdXBpZ2tvaXhybG1RMDBRS1NWVVdRbFJueE9xRjUrWXB5OEdnQTZ1QzFEdXFkTklsTUkvL2FpVDg5S2ZrbEFKN1JmZWdnMzRxa3lkNnQ3ME4zRFN3aEJpSXRaL21idkZ1dVhIOFlZMHRVM1E1aXgyVzlrOEJvbkwxTSs0Q3R3dUtBRXJYaGtKYzRzb1FaOWJMWDJWQjNid05udjZuWW04Q1RxbVFQUFdYL0pkU0tpc0gvYzJmS2tQZHZJRlgxMnRXU2pncmxFMTE2WU5QRmNKZmFOa1NqSVpLaGtiaHJTYStURi9hbUdDWGNhNnFSN3BJSDhNSDBkY1Jld09MQzRleUc1YlRWK2o0eVNKbnBNRytGWDJwQ3VBRFA0MGJJcUY5aDdYdnJSdiIsImNvbnNlbnRUb2tlbiI6IkF0emF8SXdFQklBX25xX2pYdHdBMnlBSk9iaTZqcUxMYmlFcGJHQnNvaTNPNzB5S2hjNUh2UDRZTF90ZFV6dlc1QkRvU0U1OTU0UTFxby03WkJXOHBWbHA4M1o2d0dXWjFpYXA0LXk4dHpVa3dSOUJZVlRJRVo0V09WUmZ3bzNwWHRhdlM1MG54T1Y2QWVUd012TTYwMW9aS0ZMWEdfanhLM0NRVEhaNDg5amdUb0RQdlpkTXJkdmFkdm5yVVh6MXpiUHFwalducHNOOEpPNjVvSVIyWnJwMkYxRGQ2Y3U0U0tBQjljclg1a3JEOVp6Z0ZleXQ5RGVGd3IzU29Tb3BhQWJvZEtJUlFqU1BhR3RJM1l2bGN0WXpBbG1ZdHVTdmhma0MzN1RfQ0EtR1NlZjdXbFBpbkJRIiwiZGV2aWNlSWQiOiJhbXpuMS5hc2suZGV2aWNlLkFIV1pZVE1UTUNNR1hWTkZXQjRPNzJURlBEVFpFVlRSRlZMSkRPRVM3Rkk2M1JHSFdEQ0FQSUFUQUJSQ1VJRzJWRDdIVUNEVVFTSlZRS1dLWURVWVA2MzVVV0VDU0FaRlBUTTVNSUhRRFFUWUI3S1Q3RlZCSzNGVlNJRDZPTVJGU0tPTlk1V1k1TEFUVTVTVFBVMzVFV1NSNkRQRk40S1NYV1ZaUDdRR0ZHWkpKNjNaS0FQNDQiLCJ1c2VySWQiOiJhbXpuMS5hc2suYWNjb3VudC5BRVQ1UVlIM1gyREJMNUxWSkJON04yQldTNUU0T0lURDZIN1IyN0ZSRFdSS0NHNEpOU0NHWkpKWldKUDdCMkpLVFNYTEJHUzdCT05KTk5KRUpFWDJURFU2MldVWFRXN0RTQ0RDWVRCS1pFUEhCUkdPWjI3Q1RaNkhMWFRBQ09LQUVXQ0hCS1BTTjVHQUROQ0RXVFY0NlUzQ1c2VU82U09TNzdLT1paMllHM0FOTlNWNDdFWU9NM1NRUVdZU0I2VVdXTkpBTE02UldJUFlSRlkifX0.QK9mxalr7hwgE_qiSvuLc9V8HKMIaa9uXF2EV3VLHWaSbhHJDvLpYU5SWAyOE6iAhJtjKxrBOcGBlNHReKkSauHpagQkkUruL7-KvboSl67ZvLNuNCBaTa_ePDyePeDygfEmgPFvKsc5muzmdhhxmy5USWMbzF8kTnUlMJSlnGZaaxY41Ifeg2_w3nahyvW6YkG9AtN6h2uZzeFYwTZ0H7uxolKkSEyksKmcyst5XzCh-hSRP9TymjekR7mHlAjcFkpDxEjbwGiWQNRHRPeYcnTd3saD5E47StUhM0zBQ1g8Hc5nGiXV7_GoPeJa_qPx2gJ_cxRb541ITTKcJNUw7g",
        handler_output = pa.handler(event=event, context = {})
        response = handler_output['response']
 
    except Exception as e:
        print(e)
        assert False

    #un-monkey patch
    DeviceAddressServiceClient.get_full_address = saved_method

    if response['card']['title'] == pa.NOTIFY_BAD_ADDRESS_TITLE:
        assert True # Outcome D: We're good -> Results with address coord
    else:
        assert False

