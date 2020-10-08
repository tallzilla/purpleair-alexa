# -*- coding: utf-8 -*-

# This is a simple Nearest Air Sensor Alexa Skill, built using
# the implementation of handler classes approach in skill builder

import logging
import get_aqi
from get_geo import get_address, get_coordinate_from_address_response
import requests

from ask_sdk_core.skill_builder import SkillBuilder
from ask_sdk_core.dispatch_components import AbstractRequestHandler
from ask_sdk_core.dispatch_components import AbstractExceptionHandler
from ask_sdk_core.utils import is_request_type, is_intent_name
#from ask_sdk_core.handler_input import HandlerInput TODO: DELETE IF TESTS PASS
from ask_sdk_core.skill_builder import CustomSkillBuilder
from ask_sdk_core.api_client import DefaultApiClient
from ask_sdk_model.ui import SimpleCard
from ask_sdk_model.ui import AskForPermissionsConsentCard
from ask_sdk_model import Response
from ask_sdk_model.permission_status import PermissionStatus

sb = CustomSkillBuilder(api_client=DefaultApiClient())

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

ERROR = "Uh Oh. Looks like something went wrong."
NOTIFY_MISSING_PERMISSIONS = ("Please enable Location permissions in "
                              "the Amazon Alexa app.")
address_permissions = ["read::alexa:device:all:address"]


class LaunchRequestHandler(AbstractRequestHandler):
    """Handler for Skill Launch."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return is_request_type("LaunchRequest")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response

        request_envelope = handler_input.request_envelope
        response_builder = handler_input.response_builder
        user_permissions = request_envelope.context.system.user.permissions

        # get data necessary for address access
        device_id = request_envelope.context.system.device.device_id
        consent_token = request_envelope.context.system.user.permissions.consent_token

        address_access = ( consent_token is not None )


        #TODO: This is a mess. Clean up permissioning

        print(request_envelope.context)

        geolocation_granted = user_permissions.scopes['alexa::devices:all:geolocation:read'].status.value
        location_services_enabled = (request_envelope.context.geolocation is not None)

        geolocation_access = (geolocation_granted == PermissionStatus.GRANTED.value and location_services_enabled)

        print(address_access)
        print(geolocation_granted)
        print(location_services_enabled)

        #If the user has nothing specified ask for address permissions
        if not address_access or geolocation_access:
            response_builder.speak(NOTIFY_MISSING_PERMISSIONS)
            response_builder.set_card(
                AskForPermissionsConsentCard(permissions=address_permissions))
            return response_builder.response

        if geolocation_granted == PermissionStatus.GRANTED and location_services_enabled:
            lat = request_envelope.context.geolocation.coordinate.latitude_in_degrees
            lng = request_envelope.context.geolocation.coordinate.longitude_in_degrees
            coordinate = {'lat': lat, 'lng': lng}
        else:
            #response = get_address(device_id, consent_token)
            service_client_factory = handler_input.service_client_factory
            device_addr_client = service_client_factory.get_device_address_service()
            address = device_addr_client.get_full_address(device_id)
            coordinate = get_coordinate_from_address_response(address)

        readings = get_aqi.get_closest_device_readings(coordinate)

        try:
            aqi = readings['aqi']
        except KeyError as e:
            speech_text = ERROR
            card_text = speech_text

        else:

            #convert the device id into a readable string
            device_id_string = " ".join(str(readings['device_id']))

            #human-readable distance

            if readings['miles_away'] < 2:
                distance_string = "{} feet away".format(int(5280 * readings['miles_away']))
            else:
                distance_string = "{} miles away".format(int(readings['miles_away']))

            speech_text = "Your AQI is {}. <break time= \"0.5s\"/> The nearest PurpleAir device i.d. is {}" \
                "and I think it's about {}.".format(
                    readings['aqi'],
                    device_id_string,
                    distance_string)

            card_text = "Your AQI is {}. <break time= \"0.5s\"/> The nearest PurpleAir device ID is {}. " \
                "I think it's about {}.".format(
                    readings['aqi'],
                    readings['device_id'],
                    distance_string)

        #speech_text = "Welcome to my local air sensor! You can ask what the air quality is."

        response_builder.speak(speech_text).set_card(
            SimpleCard("Nearest Air Sensor", card_text)).set_should_end_session(
            True)
        return response_builder.response


class AQIIntentHandler(AbstractRequestHandler):
    """Handler for Nearest Air Sensor Intent."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return is_intent_name("AQIIntent")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response

        try:
            aqi = get_aqi.get_hardcoded_aqi()
        except Exception as e:
            speech_text = "Sorry, there was a problem getting your AQI. Please try again."
        else:
            speech_text = "The air quality in Berkeley, California is " + str(aqi)
        finally:
            pass
    
        handler_input.response_builder.speak(speech_text).set_card(
            SimpleCard("Your AQI", speech_text)).set_should_end_session(
            True)
        return handler_input.response_builder.response


class HelpIntentHandler(AbstractRequestHandler):
    """Handler for Help Intent."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return is_intent_name("AMAZON.HelpIntent")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        speech_text = "This skill will tell you what your nearest AQI is!"

        handler_input.response_builder.speak(speech_text).ask(
            speech_text).set_card(SimpleCard(
                "Nearest Air Sensor", speech_text))
        return handler_input.response_builder.response


class CancelOrStopIntentHandler(AbstractRequestHandler):
    """Single handler for Cancel and Stop Intent."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return (is_intent_name("AMAZON.CancelIntent")(handler_input) or
                is_intent_name("AMAZON.StopIntent")(handler_input))

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        speech_text = "Goodbye!"

        handler_input.response_builder.speak(speech_text).set_card(
            SimpleCard("Nearest Air Sensor", speech_text))
        return handler_input.response_builder.response


class FallbackIntentHandler(AbstractRequestHandler):
    """
    This handler will not be triggered except in supported locales,
    so it is safe to deploy on any locale.
    """
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return is_intent_name("AMAZON.FallbackIntent")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        speech_text = (
            "This skill can't help you with that.  "
            "You can ask about the air quality!!")
        reprompt = "You can ask about the AQI!!"
        handler_input.response_builder.speak(speech_text).ask(reprompt)
        return handler_input.response_builder.response


class SessionEndedRequestHandler(AbstractRequestHandler):
    """Handler for Session End."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return is_request_type("SessionEndedRequest")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        return handler_input.response_builder.response


class CatchAllExceptionHandler(AbstractExceptionHandler):
    """Catch all exception handler, log exception and
    respond with custom message.
    """
    def can_handle(self, handler_input, exception):
        # type: (HandlerInput, Exception) -> bool
        return True

    def handle(self, handler_input, exception):
        # type: (HandlerInput, Exception) -> Response
        logger.error(exception, exc_info=True)
        handler_input.response_builder.speak(ERROR).ask(ERROR)

        return handler_input.response_builder.response

#Register handlers
sb.add_request_handler(LaunchRequestHandler())
sb.add_request_handler(AQIIntentHandler())
sb.add_request_handler(HelpIntentHandler())
sb.add_request_handler(CancelOrStopIntentHandler())
sb.add_request_handler(FallbackIntentHandler())
sb.add_request_handler(SessionEndedRequestHandler())
sb.add_exception_handler(CatchAllExceptionHandler())
handler = sb.lambda_handler()