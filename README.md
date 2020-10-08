# purpleair-alexa
 Alexa skill to read out a purpleair sensor

Some useful incantations:
Compress-Archive -Force -Path .env, *.py, .\env\Lib\site-packages\* -DestinationPath purpleair-alexa.zip



10/7
Was following these instructions:


https://github.com/alexa/alexa-cookbook/tree/master/tools/LocalDebugger/python
https://github.com/alexa/alexa-skills-kit-sdk-for-python/tree/master/ask-sdk-local-debug
https://developer.amazon.com/en-US/docs/alexa/custom-skills/device-address-api.html
https://developer.amazon.com/en-US/docs/alexa/custom-skills/location-services-for-alexa-skills.html
https://data-dive.com/alexa-get-device-location-from-custom-skill

10/8
in tests.py

def test_no_address_has_geo():

I'm at the point where this test result is asking for location permissions. Which:
1) Isn't correct (we have geo permissions)
2) Need to refactor geo permissions a bit to follow amazon's standard anyway

 pytest -x --pdb -s .\tests\test.py