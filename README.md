# purpleair-alexa
 Alexa skill to read out a purpleair sensor

Some useful incantations:
Compress-Archive -Force -Path .env, *.py, *.json, .\env\Lib\site-packages\* -DestinationPath purpleair-alexa.zip

pytest -x --pdb -s .\tests\test.py