import requests, os, base64

SERVER_PORT = os.getenv("SERVER_PORT", 5000)

output_file = 'outputs/change_voice.wav'
if os.path.exists(output_file):
    os.remove(output_file)

version = 'v2'

# Define the URL of the generate_audio endpoint
url = f'http://localhost:{SERVER_PORT}/{version}/generate-audio'

# Define the parameters for the POST request
payload = {
    'model': 'en',
    'input': 'Hello, this is a test. I am here, there and everywhere',
    'speed': 1.0,
    'response_format': 'base64',
    'voice': 'raw',
}
try:
    # Send the POST request to generate the audio
    response = requests.post(url, json=payload)
    # Check if the request was successful
    if response.status_code == 200:
        url = f'http://localhost:{SERVER_PORT}/{version}/change-voice'
        response_data = response.json()
        audio_data = response_data['result']['data']['audio_data']
        payload = {
            'model': 'en',
            'response_format': 'bytes',
            'audio_data': audio_data,
            'voice': 'elon'
        }
        try:
            response = requests.post(url, json=payload)
            if response.status_code == 200:
                with open(output_file, 'wb') as audio_file:
                    audio_file.write(response.content)
                print(f'Audio file saved as {output_file}')
            else:
                print(f'Error getting file url: {response.status_code}')
                print(response.json())
    
        except requests.exceptions.RequestException as e:
            print(f'Request failed: {e}')
    
    else:
        print(f'Error: {response.status_code}')
        print(response.json()) 

except requests.exceptions.RequestException as e:
            print(f'Request failed: {e}')