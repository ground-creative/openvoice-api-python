import requests, os, base64

SERVER_PORT = os.getenv("SERVER_PORT", 5000)

output_file = 'outputs/generate_audio_bytes.wav'
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
    'response_format': 'bytes',
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
        with open(output_file, 'wb') as audio_file:
            audio_file.write(response.content)
        print(f'Audio file saved as {output_file}')
    else:
        print(f'Error: {response.status_code}')
        print(response.json())

except requests.exceptions.RequestException as e:
    print(f'Request failed: {e}')