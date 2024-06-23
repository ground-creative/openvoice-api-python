# OPENVOICE API

An api engine for openvoice written in python<br />
https://github.com/myshell-ai/OpenVoice/tree/main

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
