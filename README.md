# OPENVOICE API

An api engine for openvoice written in python<br />
https://github.com/myshell-ai/OpenVoice/tree/main

## Services

http(s):://{SERVER_ADDRESS}:{SERVER_PORT}/generate-audio/{VERSION}/
Description: Generate an audio wav file
Method: POST 
Params: language(default 0), speed(default 1.0), text(required), response_format(url|bytes|stream)(default url), speaker(any speaker you have configured)(default is first speaker configured)
Extra params V1: style('default', 'whispering', 'shouting', 'excited', 'cheerful', 'terrified', 'angry', 'sad', 'friendly')
Extra params V2: accent

http(s):://{SERVER_ADDRESS}:{SERVER_PORT}'/audio-file/{FILENAME}}'
Description: Retrieve a generate audio url
Method: GET
Params: stream(true|false)(default false)


## Installation

### Docker

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
