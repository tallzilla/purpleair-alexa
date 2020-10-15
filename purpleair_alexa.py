# -*- coding: utf-8 -*-

# This is a simple Nearest Air Sensor Alexa Skill, built using
# the implementation of handler classes approach in skill builder

import logging
import get_aqi
import requests
from get_geo import get_address, get_coordinate_from_address_response
from ask_sdk_core.skill_builder import SkillBuilder
from ask_sdk_core.dispatch_components import AbstractRequestHandler
from ask_sdk_core.dispatch_components import AbstractExceptionHandler
from ask_sdk_core.utils import is_request_type, is_intent_name
from ask_sdk_core.skill_builder import CustomSkillBuilder
from ask_sdk_core.api_client import DefaultApiClient
from ask_sdk_model.ui import SimpleCard
from ask_sdk_model.ui import AskForPermissionsConsentCard
from ask_sdk_model import Response
from ask_sdk_model.permission_status import PermissionStatus
from ask_sdk_model.services.service_exception import ServiceException

sb = CustomSkillBuilder(api_client=DefaultApiClient())

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

ERROR_TITLE = "Uh oh"
ERROR = "Looks like something went wrong."
NOTIFY_TITLE = "Permissions needed"
NOTIFY_MISSING_ADDRESS_PERMISSIONS = (
    "Please enable Address permissions in " "the Amazon Alexa app."
)
NOTIFY_MISSING_LOCATION_PERMISSIONS = (
    "Please enable Location permissions in " "the Amazon Alexa app."
)
SUCCESS_TITLE = "Your AQI"
SUCCESS_CARD = (
    "Your AQI is {} at {}. The nearest PurpleAir device ID is {}. "
    "I think it's about {}."
)
SUCCESS_SPEECH = (
    'Your AQI is {} <break time= "0.25s"/> at {}. <break time= "0.25s"/> The nearest PurpleAir device i.d. is {}'
    "and I think it's about {}."
)

HELLA_HOT_SPEECH = (
    "Hi! It's hella hot.")

NOTIFY_BAD_ADDRESS_TITLE = "Unsupported Address"
NOTIFY_BAD_ADDRESS = "Sorry, this skill is having trouble supporting your address."
ADDRESS_PERMISSIONS = ["read::alexa:device:all:address"]
GEOLOCATION_PERMISSIONS = ["read::alexa:device:all:geolocation"]

SKILL_IDS = {
    "HELLA_HOT": ["amzn1.ask.skill.bed75595-ff55-44cb-855f-e25943965996"],
    "NEAREST_SENSOR": ["amzn1.ask.skill.d1b01c78-6fa6-4c07-ae79-b3ae36969b5",
        "amzn1.ask.skill.d1b01c78-6fa6-4c07-ae79-b3ae36969b50"]
}

def get_aqi_string(aqi):
    #returns string representing AQI
    if aqi < 51:
        return "Good"
    elif aqi < 101:
        return "Moderate"
    elif aqi < 151:
        return "Unhealthy for Sensitive Groups"
    elif aqi < 201:
        return "Unhealthy"
    elif aqi < 301:
        return "Very Unealthy"
    else:
        return "Hazardous"

def build_response_for_coordinate(response_builder, coordinate):
    #returns an alexa response given a coordinate
    lat = coordinate["latitude_in_degrees"]
    lng = coordinate["longitude_in_degrees"]
    coordinate = {"lat": lat, "lng": lng}
    readings = get_aqi.get_closest_device_readings(coordinate)
    # convert the device id into a readable string
    device_id_string = " ".join(str(readings["device_id"]))

    # human-readable distance
    if readings["miles_away"] < 2:
        distance_string = "{} feet away".format(int(5280 * readings["miles_away"]))
    else:
        distance_string = "{} miles away".format(int(readings["miles_away"]))

    aqi = get_aqi.get_hardcoded_aqi(readings["device_id"])

    card_body = SUCCESS_CARD.format(
        get_aqi_string(aqi), aqi, readings["device_id"], distance_string
    )
    speech = SUCCESS_SPEECH.format(
        get_aqi_string(aqi), aqi, readings["device_id"], distance_string
    )
    response_builder.speak(speech).set_card(
        SimpleCard(title=SUCCESS_TITLE, content=card_body)
    ).set_should_end_session(True)
    return response_builder.response


def nearest_air_sensor_handler(handler_input):
    # returns a reponse for nearest air sensor

    request_envelope = handler_input.request_envelope
    response_builder = handler_input.response_builder
    user_permissions = request_envelope.context.system.user.permissions

    # get data necessary for geolocation access

    location_services_supported = request_envelope.context.geolocation is not None

    try:
        geolocation_granted = (
            user_permissions.scopes["alexa::devices:all:geolocation:read"].status.value
            == PermissionStatus.GRANTED.value
        )
    except KeyError:
        geolocation_granted = False

    # get data necessary for address access
    device_id = request_envelope.context.system.device.device_id
    api_access_token = request_envelope.context.system.api_access_token

    try:
        service_client_factory = handler_input.service_client_factory
        device_addr_client = service_client_factory.get_device_address_service()
        address = device_addr_client.get_full_address(device_id)
        address_access = True
    except ServiceException:
        address_access = False
        address = None

    if location_services_supported:  # if geo location services are supported
        if geolocation_granted:  # if we have permissions we've got a coordinate!
            try:  # TODO I can't figure out how to pass a subscriptable object in test
                coordinate = request_envelope.context.geolocation["coordinate"]
            except TypeError:
                coordinate = request_envelope.context.geolocation.coordinate.to_dict()
            return build_response_for_coordinate(response_builder, coordinate)
        else:  # if not and we don't have access to address, we'll have to ask for something
            if not address_access:
                response_builder.speak(NOTIFY_MISSING_LOCATION_PERMISSIONS)
                response_builder.set_card(
                    AskForPermissionsConsentCard(permissions=GEOLOCATION_PERMISSIONS)
                )
                return response_builder.response

    if address_access:  # if we haven't returned somethng and do have address access
        coordinate = get_coordinate_from_address_response(address)
        if coordinate is None:
            response_builder.speak(NOTIFY_BAD_ADDRESS).set_card(
                SimpleCard(title=NOTIFY_BAD_ADDRESS_TITLE, content=NOTIFY_BAD_ADDRESS)
            ).set_should_end_session(True)
            return response_builder.response
        else:
            return build_response_for_coordinate(response_builder, coordinate)
    else:  # if we don't have access to anything thus far we'll need address permissions
        response_builder.speak(NOTIFY_MISSING_ADDRESS_PERMISSIONS)
        response_builder.set_card(
            AskForPermissionsConsentCard(permissions=ADDRESS_PERMISSIONS)
        )
        return response_builder.response

def hella_hot_handler(handler_input):
    request_envelope = handler_input.request_envelope
    response_builder = handler_input.response_builder 

    response_builder.speak(HELLA_HOT_SPEECH).set_card(
        SimpleCard("Nearest Air Sensor", HELLA_HOT_SPEECH)
    )
    return response_builder.response

class LaunchRequestHandler(AbstractRequestHandler):
    """Handler for Skill Launch."""

    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return is_request_type("LaunchRequest")(handler_input)

    def handle(self, handler_input):

        application_id = handler_input.request_envelope.session.application.application_id
        print(application_id)

        if application_id in SKILL_IDS['NEAREST_SENSOR']:
            return nearest_air_sensor_handler(handler_input)
        elif application_id in SKILL_IDS['HELLA_HOT']:
            return hella_hot_handler(handler_input)
        else:
            raise


class AQIIntentHandler(AbstractRequestHandler):
    """Handler for Nearest Air Sensor Intent."""

    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return is_intent_name("AQIIntent")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        return nearest_air_sensor_handler(handler_input)


class HelpIntentHandler(AbstractRequestHandler):
    """Handler for Help Intent."""

    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return is_intent_name("AMAZON.HelpIntent")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        speech_text = "This skill will tell you what your nearest AQI is!"

        handler_input.response_builder.speak(speech_text).ask(speech_text).set_card(
            SimpleCard("Nearest Air Sensor", speech_text)
        )
        return handler_input.response_builder.response


class CancelOrStopIntentHandler(AbstractRequestHandler):
    """Single handler for Cancel and Stop Intent."""

    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return is_intent_name("AMAZON.CancelIntent")(handler_input) or is_intent_name(
            "AMAZON.StopIntent"
        )(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        speech_text = "Goodbye!"

        handler_input.response_builder.speak(speech_text).set_card(
            SimpleCard("Nearest Air Sensor", speech_text)
        )
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
        speech_text = "This skill will help you find your nearest air sensor."
        handler_input.response_builder.speak(speech_text).set_should_end_session(True)
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
        handler_input.response_builder.speak(ERROR).set_should_end_session(True)

        return handler_input.response_builder.response


# Register handlers
sb.add_request_handler(LaunchRequestHandler())
sb.add_request_handler(AQIIntentHandler())
sb.add_request_handler(HelpIntentHandler())
sb.add_request_handler(CancelOrStopIntentHandler())
sb.add_request_handler(FallbackIntentHandler())
sb.add_request_handler(SessionEndedRequestHandler())
sb.add_exception_handler(CatchAllExceptionHandler())
handler = sb.lambda_handler()
