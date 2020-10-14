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

## You'll need to know to run locally
You'll have to create a .env file in the root directory of the project with the format
```
MAPS_API_KEY=<your Google Maps api key>
```
You'll also have to fetch the list of sensors at https://www.purpleair.com/json and save it to purpleair.json in the root directory.
 
## Some useful incantations:
1. Pack everything up for lambda upload (windows):
```
Compress-Archive -Force -Path .env, *.py, *.json, .\env\Lib\site-packages\* -DestinationPath purpleair-alexa.zip
```
2. Run tests
```
pytest -x --pdb -s .\tests\test.py
```