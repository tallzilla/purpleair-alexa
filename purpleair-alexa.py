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
from ask_sdk_core.handler_input import HandlerInput

from ask_sdk_model.ui import SimpleCard
from ask_sdk_model import Response

sb = SkillBuilder()

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

class LaunchRequestHandler(AbstractRequestHandler):
    """Handler for Skill Launch."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return is_request_type("LaunchRequest")(handler_input)


    #TODO - probably should pass off launch handle to AQI intent if that's possible
    def handle(self, handler_input):
        # type: (HandlerInput) -> Response

        request = handler_input.request_envelope.to_dict()

        #TODO: will need for storage
        user_id = request['context']['system']['user']['user_id']


        # get data necessary for address access
        device_id = request['context']['system']['device']['device_id']
        consent_token = request['context']['system']['user']['permissions']['consent_token']

        address_access = ( request['context']['system']['user']['permissions']['consent_token'] != None )
        geolocation_access = (request['context']['geolocation'] != None)

        if not address_access and not geolocation_access:
            #TODO: If the user doesn't have any geo-ish permissions do something
            pass
        elif geolocation_access:
            lat = input['context']['geolocation']['coordinate']['latitude_in_degrees']
            lng = input['context']['geolocation']['coordinate']['longitude_in_degrees']
            coordinate = {lat: lat, lng: lng}
            # preference is to act on geolocation data
            pass
        else:
            response = get_address(device_id, consent_token)
            coordinate = get_coordinate_from_address_response(response)

            # act on address_access
            pass

        readings = get_aqi.get_closest_device_readings(coordinate)


        try:
            aqi = readings['aqi']
        except KeyError as e:
            speech_text = "Sorry, there was a problem getting your AQI. Please try again."
        else:

            #convert the device id into a readable string
            device_id_string = " ".join(str(readings['device_id']))

            #human-readable distance

            if readings['miles_away'] < 1:
                distance_string = "{} feet away".format(int(5280 * readings['miles_away']))
            else:
                distance_string = "{} miles away".format(int(reading['miles_away']))

            speech_text = "Your AQI is {}, your PurpleAir device i.d. is {}" \
                "and I think it's about {}".format(
                    readings['aqi'],
                    device_id_string,
                    distance_string)

        #speech_text = "Welcome to my local air sensor! You can ask what the air quality is."

        handler_input.response_builder.speak(speech_text).set_card(
            SimpleCard("Nearest Air Sensor", speech_text)).set_should_end_session(
            True)
        return handler_input.response_builder.response


class AQIIntentHandler(AbstractRequestHandler):
    """Handler for Nearest Air Sensor Intent."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return is_intent_name("AQIIntent")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response

        try:
            aqi = get_aqi.main()
        except Exception as e:
            speech_text = "Sorry, there was a problem getting your AQI. Please try again."
        else:
            speech_text = "Jeff Bezos can eat a D. I did this from my computer. Hey sexy, your AQI is " + str(aqi)
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
        speech_text = "You can ask me what the AQI is!"

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

        speech = "Sorry, there was some problem. Please try again!!"
        handler_input.response_builder.speak(speech).ask(speech)

        return handler_input.response_builder.response


sb.add_request_handler(LaunchRequestHandler())
sb.add_request_handler(AQIIntentHandler())
sb.add_request_handler(HelpIntentHandler())
sb.add_request_handler(CancelOrStopIntentHandler())
sb.add_request_handler(FallbackIntentHandler())
sb.add_request_handler(SessionEndedRequestHandler())

sb.add_exception_handler(CatchAllExceptionHandler())

handler = sb.lambda_handler()