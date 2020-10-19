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
from ask_sdk_model.canfulfill import CanFulfillIntent, CanFulfillIntentValues

#TODO: should be in __init__.py
if len(logging.getLogger().handlers) > 0:
    # The Lambda environment pre-configures a handler logging to stderr. If a handler is already configured,
    # `.basicConfig` does not execute. Thus we set the level directly.
    root = logging.getLogger()
    if root.handlers:
        for handler in root.handlers:
            root.removeHandler(handler)
    logging.basicConfig(format='%(asctime)s %(message)s',level=logging.INFO)
else:
    logging.basicConfig(level=logging.INFO)

sb = CustomSkillBuilder(api_client=DefaultApiClient())

ERROR_TITLE = "Uh oh"
ERROR = "Looks like something went wrong."
NOTIFY_TITLE = "Permissions needed"
NOTIFY_MISSING_ADDRESS_PERMISSIONS = (
    "Please enable Address permissions in " "the Amazon Alexa app."
)
NOTIFY_MISSING_LOCATION_PERMISSIONS = (
    "Please enable Location permissions in " "the Amazon Alexa app."
)

SWEET_TITLE = "Your Air Report"

SWEET_CARD = (
    "I found an air sensor that's {} away. "
    "The air quality is {}. "
    "Your AQI is {}."
)
SWEET_SPEECH = (
    "I found an air sensor that's {} away. <break time= '0.25s'/>"
    "The air quality is {}. <break time= '0.25s'/>"
    "Your AQI is {}. <break time= '0.25s'/>"
)

SUCCESS_TITLE = "Your AQI"
SUCCESS_CARD = (
    "Your AQI is {} at {}. "
    "The nearest PurpleAir device ID is {}. "
    "I think it's about {} away."
)
SUCCESS_SPEECH = (
    "Your AQI is {} <break time= '0.25s'/> at {}. <break time= '0.25s'/> The nearest PurpleAir device i.d. is {}"
    "and I think it's about {} away."
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
        "amzn1.ask.skill.d1b01c78-6fa6-4c07-ae79-b3ae36969b50",
        "amzn1.ask.skill.96430739-946c-4ce3-b5f9-0f85282d3d90"]
}


def sweet_air_handler(handler_input):
    """returns a response for nearest air sensor"""
    response, coordinate = get_response_and_coordinate(handler_input)

    if coordinate is None:
        return response
    else:
        request_envelope = handler_input.request_envelope
        response_builder = handler_input.response_builder
        return build_sweet_air_response_for_coordinate(response_builder, coordinate)

def sensor_detail_handler(handler_input):
    """returns a response for nearest air sensor"""

    response, coordinate = get_response_and_coordinate(handler_input)

    if coordinate is None:
        return response
    else:
        request_envelope = handler_input.request_envelope
        response_builder = handler_input.response_builder
        return build_response_for_coordinate(response_builder, coordinate)

def get_aqi_index_string(aqi):
    """returns string representing AQI"""
    if aqi < 51:
        return "Good"
    elif aqi < 101:
        return "Moderate"
    elif aqi < 151:
        return "Unhealthy for Sensitive Groups"
    elif aqi < 201:
        return "Unhealthy"
    elif aqi < 301:
        return "Very Unhealthy"
    else:
        return "Hazardous"

def humanize_distance(miles_away):
    """human-readable distance"""
    if miles_away < 2:
        distance_string = "{} feet".format(int(5280 * miles_away))
    else:
        distance_string = "{} miles".format(int(miles_away))
    return distance_string

def build_sweet_air_response_for_coordinate(response_builder, coordinate):
    """returns the 'default' response"""
    readings = get_aqi.get_closest_device_readings(coordinate)
    distance = humanize_distance(readings["miles_away"])

    aqi = get_aqi.get_hardcoded_aqi(readings["device_id"])

    card_body = SWEET_CARD.format(
        distance, get_aqi_index_string(aqi), aqi
    )
    speech = SWEET_SPEECH.format(
        distance, get_aqi_index_string(aqi), aqi
    )
    response_builder.speak(speech).set_card(
        SimpleCard(title=SWEET_TITLE, content=card_body)
    ).set_should_end_session(True)

    logging.info(response_builder.response)
    return response_builder.response

def build_response_for_coordinate(response_builder, coordinate):
    """returns an alexa response given a coordinate"""

    readings = get_aqi.get_closest_device_readings(coordinate)
    # convert the device id into a readable string
    device_id_string = " ".join(str(readings["device_id"]))

    distance_string = humanize_distance(readings["miles_away"])

    aqi = get_aqi.get_hardcoded_aqi(readings["device_id"])

    card_body = SUCCESS_CARD.format(
        get_aqi_index_string(aqi), aqi, readings["device_id"], distance_string
    )
    speech = SUCCESS_SPEECH.format(
        get_aqi_index_string(aqi), aqi, readings["device_id"], distance_string
    )
    response_builder.speak(speech).set_card(
        SimpleCard(title=SUCCESS_TITLE, content=card_body)
    ).set_should_end_session(True)

    logging.info(response_builder.response)
    return response_builder.response

def get_response_and_coordinate(handler_input):
    """returns response_builder, Coordinate (optional)"""

    coordinate = None
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
            return response_builder.response, coordinate
            #return build_response_for_coordinate(response_builder, coordinate)
        else:  # if not and we don't have access to address, we'll have to ask for something
            if not address_access:
                response_builder.speak(NOTIFY_MISSING_LOCATION_PERMISSIONS)
                response_builder.set_card(
                    AskForPermissionsConsentCard(permissions=GEOLOCATION_PERMISSIONS)
                )
                return response_builder.response, coordinate

    if address_access:  # if we haven't returned somethng and do have address access
        coordinate = get_coordinate_from_address_response(address)
        if coordinate is None:
            response_builder.speak(NOTIFY_BAD_ADDRESS).set_card(
                SimpleCard(title=NOTIFY_BAD_ADDRESS_TITLE, content=NOTIFY_BAD_ADDRESS)
            ).set_should_end_session(True)
            return response_builder.response, coordinate
        else:
            return response_builder.response, coordinate
    else:  # if we don't have access to anything thus far we'll need address permissions
        response_builder.speak(NOTIFY_MISSING_ADDRESS_PERMISSIONS)
        response_builder.set_card(
            AskForPermissionsConsentCard(permissions=ADDRESS_PERMISSIONS)
        )
        return response_builder.response, coordinate

    return response_builder.response, coordinate

class LaunchRequestHandler(AbstractRequestHandler):
    """Handler for Skill Launch."""

    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return is_request_type("LaunchRequest")(handler_input)

    def handle(self, handler_input):
        application_id = handler_input.request_envelope.session.application.application_id

        if application_id in SKILL_IDS['NEAREST_SENSOR']:
            return sweet_air_handler(handler_input)
        elif application_id in SKILL_IDS['HELLA_HOT']:
            return hella_hot_handler(handler_input)
        else:
            raise

class CanFulfillIntentRequestHandler(AbstractRequestHandler):
    """Handler for CanFulfillIntentRequest."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return is_request_type('CanFulfillIntentRequest')(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response

        logging.info("Here comes some sweet intent requests:")
        logging.info(handler_input)

        #TODO: check this out
        #can_fulfill = CanFulfillIntent(CanFulfillIntentValues.YES)
        #if is_intent_name("ChangePlatformsIntent")(handler_input):
        can_fulfill = CanFulfillIntent(CanFulfillIntentValues.NO)

        return (
            handler_input.response_builder
                         .set_can_fulfill_intent(can_fulfill)
                         .response
        )

class AirQualityHandler(AbstractRequestHandler):
    """Handler for Nearest Air Sensor Intent."""

    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return is_intent_name("AirQualityIntent")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        return sweet_air_handler(handler_input)

class SensorDetailHandler(AbstractRequestHandler):
    """Handler for Nearest Air Sensor Intent."""

    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return is_intent_name("SensorDetailIntent")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        return sensor_detail_handler(handler_input)


class HelpIntentHandler(AbstractRequestHandler):
    """Handler for Help Intent."""

    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return is_intent_name("AMAZON.HelpIntent")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        speech_text = "You can open this skill for basic information, or ask for detailed sensor information for more!"

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
sb.add_request_handler(CanFulfillIntentRequestHandler())
sb.add_request_handler(LaunchRequestHandler())
sb.add_request_handler(SensorDetailHandler())
sb.add_request_handler(AirQualityHandler())
sb.add_request_handler(HelpIntentHandler())
sb.add_request_handler(CancelOrStopIntentHandler())
sb.add_request_handler(FallbackIntentHandler())
sb.add_request_handler(SessionEndedRequestHandler())
sb.add_exception_handler(CatchAllExceptionHandler())
handler = sb.lambda_handler()
