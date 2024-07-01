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

### 1. Generate an audio file

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


### 2. Change voice

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

Look inside examples folder

## Unit Testing

```
cd tests
python -m unittest __FILE__
# or
python -m unittest __FILE__.CLASS__
# or
python -m unittest __FILE__.CLASS__.FUNCTION__
```
