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
You'll also have to fetch the list of sensors at https://www.purpleair.com/json and save it to purpleair.json in the root directory.
```
curl https://www.purpleair.com/json > purpleair.json
```

## Useful local incantations:
1. Pack everything up for lambda upload (Windows):
```
Compress-Archive -Force -Path .env, *.py, *.json, .\env\Lib\site-packages\* -DestinationPath purpleair-alexa.zip
```
2. Run tests
```
python -m pytest -x --pdb -s --log-cli-level=50 .\tests\test.py
```
3. Lint me
```
python -m black .
```
4. Get the latest sensor list locally
```
curl https://www.purpleair.com/json > purpleair.json
```
or on Windows
```
curl https://www.purpleair.com/json -OutFile purpleair.json
```