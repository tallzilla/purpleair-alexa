# purpleair-alexa
Alexa skill to read out the nearest PurpleAir sensor

##You'll need to know
You'll have to create a .env file in the root directory of the project with the format
```
MAPS_API_KEY=<your Google Maps api key>
```

##Some useful incantations:
1. Pack everything up for lambda upload (windows):
```
Compress-Archive -Force -Path .env, *.py, *.json, .\env\Lib\site-packages\* -DestinationPath purpleair-alexa.zip
```
2. Run tests
```
pytest -x --pdb -s .\tests\test.py
```