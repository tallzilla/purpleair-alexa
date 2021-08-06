# purpleair-alexa
Alexa skill to read out the nearest PurpleAir sensor

## To run hosted on github
Will need the following secrets setup to make the workflows work. Should be self-explanatory.
```
AWS_ACCESS_KEY_ID=<your key>
AWS_SECRET_ACCESS_KEY=<your key>
AWS_REGION=<your key>
MAPS_API_KEY=<your key>
```

## To run locally
You'll have to create a .env file in the root directory of the project with the format
```
MAPS_API_KEY=<your Google Maps api key>
PURPLEAIR_READ_KEY=<your PurpleAir read api key>
PURPLEAIR_WRITE_KEY=<your PurpleAir write api key>
```
You'll also have to fetch the list of sensors at https://api.purpleair.com/v1/sensors and save it to purpleair.json in the root directory (see step #4 below).

## Useful local commands 

1. Local debugging commands. Follow these instructions generally: https://github.com/alexa/alexa-cookbook/blob/master/tools/LocalDebugger/python/README.md. But specifically
```
ngrok http 3001
python -m pdb -c continue .\local_debugger.py -p 3001 -f .\purpleair_alexa.py -l handler
```
2. Pack everything up for lambda upload (Windows):
```
Compress-Archive -Force -Path .env, *.py, *.json, .\env\Lib\site-packages\* -DestinationPath purpleair-alexa.zip
```
3. Lint me
```
python -m black .
```
4. Run tests
```
python -m pytest -x --pdb -s --log-cli-level=50 .\tests\test.py
```
5. Get the latest sensor list locally
```
curl https://api.purpleair.com/v1/sensors?api_key=YOUR_PURPLEAIR_READ_KEY_HERE"&"fields=latitude%2Clongitude%2Cpm2.5 > purpleair.json
```
or on Windows
```
curl https://api.purpleair.com/v1/sensors?api_key=YOUR_PURPLEAIR_READ_KEY_HERE"&"fields=latitude%2Clongitude%2Cpm2.5 -OutFile purpleair.json
```