import requests, os, base64

SERVER_PORT = os.getenv("SERVER_PORT", 5000)

output_file = 'outputs/generate_audio_base64.wav'
if os.path.exists(output_file):
    os.remove(output_file)

version = 'v1'

# Define the URL of the generate_audio endpoint
url = f'http://localhost:{SERVER_PORT}/{version}/generate-audio'

# Define the parameters for the POST request
payload = {
    'model': 'en',
    'input': 'Hello, this is a test. I am here, there and everywhere',
    'speed': 1.0,
    'response_format': 'base64',
    'voice': 'elon',
    #'style': 'excited' # v1 only
    #'accent': 'en-au' #v2 only
}
try:
    # Send the POST request to generate the audio
    response = requests.post(url, json=payload)

    # Check if the request was successful
    if response.status_code == 200:
        # Save the received bytes as a .wav file
        response_data = response.json()
        audio_base64 = response_data['result']['data']['audio_data']
        with open(output_file, 'wb') as audio_file:
            audio_data = base64.b64decode(audio_base64)
            audio_file.write(audio_data)
        print(f'Audio file saved as {output_file}')
    else:
        print(f'Error: {response.status_code}')
        print(response.json())

except requests.exceptions.RequestException as e:
    print(f'Request failed: {e}')