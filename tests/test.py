# from purpleair_alexa import handler
# from tests import new_request, context


# def test_intent():
#     request = new_request('LaunchRequestHandler', {'SlotName': 'slot value'})
#     response = handler(request, context)

#     expected_response = 'Your intent was reached. My response is, "slot value".'
#     assert expected_response in response['response']['outputSpeech']['ssml']
#     assert expected_response in response['response']['reprompt']['outputSpeech']['ssml']


from __future__ import print_function
import pytest
from lib import purpleair_alexa
#from rx import Observable

class MockDeviceAddressServiceClient:
	class DeviceAddressServiceClient:
		 def get_full_address(self, device_id, **kwargs):
		 	return {}

def test_handler(event, context):
	print("TEST TIME!!!")
	#print(event)
	#print(dir(event))
	#print(dir(context))
	#print(context.client_context)

#	event.setattr(service_client_factory.get_device_address_service, MockDeviceAddressServiceClient)

	#try:
	#	print("Hi")
		#response = LaunchRequestHandler(event=event, context=context)
	#except Exception as e:
	#	print(e)