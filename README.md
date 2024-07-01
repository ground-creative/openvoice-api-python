# OPENVOICE API

An api engine for openvoice written in python

OpenVoice<br />
https://github.com/myshell-ai/OpenVoice/tree/main

API Client<br />
https://github.com/ground-creative/openvoice-api-client-python

OpenAI sdk example<br />
https://github.com/ground-creative/openvoice-api-python/blob/main/examples/openai_lib_example.py

## Installation

### Docker

Follow instructions here to install with docker<br /> 
https://github.com/ground-creative/openvoice-docker

### Stand Alone Installation

You are going to need to include OpenVoice dependencies manually.

1) Clone the repository
```
git clone https://github.com/ground-creative/openvoice-api-python.git
```

2) Change environment variables in env.sample file and rename it to .env

## Usage

```
#  install packages
pip install -r requirements.txt  # install dependencies

# Run the server
python3 app.py
```

## Services

### 1. Generate speech

**Method:** POST

**Endpoint:** `/{VERSION}/generate-audio`

**Params:**
- `model(required)` the model to use
- `input(required)` the text to convert to speech
- `speed(default: 1.0)` the speed of the voice
- `response_format(url|bytes|base64|stream)(default: url)` the response format
- `voice(default: raw)` the voice to use

**Extra params V1:** 
- `style('default','whispering','shouting','excited','cheerful','terrified','angry','sad','friendly')` a style for the voice

**Extra params V2:**
- `accent(default: default language)` an accent for the voice


### 2. Change voice of audio

**Method:** POST

**Endpoint:** `/{VERSION}/change-voice`

**Params:**
- `model(required)` the model to use
- `audio_data(required)` base64 encoded audio data
- `voice(required)` the voice to use
- `response_format(url|bytes|base64|stream)(default: url)` the response format

### 3. Retrieve a previously generated audio url

**Method:** GET

**Endpoint:** `/audio-file/{FILENAME}`
**Params:** 
- `stream(true|false)(default: false)`

## Examples

Generate speech example
```
import requests, os

SERVER_PORT = os.getenv("SERVER_PORT", 5000)

output_file = 'outputs/generate_audio_url.wav'
if os.path.exists(output_file):
    os.remove(output_file)

version = 'v2'

# Define the URL of the generate_audio endpoint
url = f'http://localhost:{SERVER_PORT}/{version}/generate-audio'

# Define the parameters for the POST request
payload = {
    'model': 'en',
    'input': 'Hello, this is a test. I am here, there and everywhere. Let me know how you feel, perhaps this can be real.',
    'speed': 1.0,
    'voice': 'elon',
    'response_format': 'url',
    #'style': 'excited' # v1 only
    #'accent': 'en-au' #v2 only
}

try:
    # Send the POST request to generate the audio
    response = requests.post(url, json=payload, stream=False)
    if response.status_code == 200:   
        response_data = response.json()
        file_url = response_data['result']['data']['url']
        print(f'Generated url: {file_url}')
        response = requests.get(file_url, stream=False)
        if response.status_code == 200:
            with open(output_file, 'wb') as audio_file:
                audio_file.write(response.content)
            print(f'Audio file saved as {output_file}')
        else:
            print(f'Error getting file url: {response.status_code}')
            print(response.json())
    else:
        print(f'Error: {response.status_code}')
        print(response.json())

except requests.exceptions.RequestException as e:
    print(f'Request failed: {e}')
```
Look inside examples folder for more examples

## Unit Testing

```
cd tests
python -m unittest __FILE__
# or
python -m unittest __FILE__.CLASS__
# or
python -m unittest __FILE__.CLASS__.FUNCTION__
```
