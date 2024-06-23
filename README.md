# OPENVOICE API

An api engine for openvoice written in python<br />
https://github.com/myshell-ai/OpenVoice/tree/main

## Services

http(s):://{SERVER_ADDRESS}:{SERVER_PORT}/generate-audio/{VERSION}/<br />
Description: Generate an audio wav file<br />
Method: POST <br />
Params:<br />
\tlanguage(default 0)<br />
    speed(default 1.0), text(required)<br /> 
    response_format(url|bytes|stream)(default url)<br /> 
    speaker(any speaker you have configured)(default is first speaker configured)<br />

Extra params V1:<br /> 
    style('default','whispering','shouting','excited','cheerful','terrified','angry','sad','friendly')
Extra params V2:<br /> 
    accent<br />

http(s):://{SERVER_ADDRESS}:{SERVER_PORT}'/audio-file/{FILENAME}<br />
Description: Retrieve a generate audio url<br />
Method: GET<br />
Params: stream(true|false)(default false)


## Installation

### Docker

Follow instructions here to install with docker<br /> 
https://github.com/ground-creative/openvoice-docker

### Stand Alone Installation

1) Clone the repository
```
git clone https://github.com/ground-creative/openvoice-api-python.git
```

2) Change environment variables in env.sample file and rename it to .env

## Usage

```
# Step 1: Create the virtual environment
python3 -m venv myenv  # Use python on Windows

# Step 2: Activate the virtual environment
source myenv/bin/activate  # Use myenv\Scripts\activate on Windows

# Now your venv is activated, and you can install packages
pip install -r requirements.txt  # if you have a requirements file

# Run the server
python3 app.py
```

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
