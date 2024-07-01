import requests, os, subprocess, time

SERVER_PORT = os.getenv("SERVER_PORT", 5000)

output_file_stream = 'outputs/test_serve_audio_stream.wav'
if os.path.exists(output_file_stream):
    os.remove(output_file_stream)

output_file_bytes = 'outputs/test_serve_audio_bytes.wav'
if os.path.exists(output_file_bytes):
    os.remove(output_file_bytes)

version = 'v2'

# Define the URL of the generate_audio endpoint
url = f'http://localhost:{SERVER_PORT}/{version}/generate-audio'

# Command to start the server using subprocess
server_command = ['python', '/app/api/app.py']

# Define the parameters for the POST request
payload = {
    'model': 'en',
    'input': 'profoundly creative and freeing. And underneath everything, this playful exploration of language is about dissent, about rising up and crying out in support of that which is alive and vital. This book is about imagination, about truth-telling and contemplation; it is an undertaking that is fierce, creative, and honest. My own journey toward language was sparked in 1996 when I discovered Keith Basso’s astonishing book Wisdom Sits in Places. Writing about the unique place-making language of the Western Apache, Basso described language in a way that I’d never considered before, as roots and fragments strung together to sing of the land. This idea intrigued me so much that I began carrying Donald Borror’s classic little book, the Dictionary of Word Roots and Combining Forms.',
    'speed': 1.0,
    'response_format': 'url'
    #'style': 'excited' # v1 only
    #'accent': 'en-au' #v2 only
}

try:
    print(" > Starting server...")
    server_process = subprocess.Popen(server_command)
    time.sleep(40)  # Wait to let the server start up
    print(" > Generating audio url...")
    response = requests.post(url, json=payload, stream=False)

    if response.status_code == 200:
        response_data = response.json()
        file_url = response_data['result']['data']['url']
        print(f' > Generated url: {file_url}')
        data = {'stream': True}
        print(' > Getting stream...')
        response = requests.get(file_url, params=data, stream=True)

        if response.status_code == 200:
            with open(output_file_stream, 'wb') as audio_file:
                for chunk in response.iter_content(chunk_size=1024):
                    if chunk:  # filter out keep-alive new chunks
                        audio_file.write(chunk)
            print(f' > Audio stream file saved as {output_file_stream}')
        else:
            print(f' > Error getting file stream: {response.status_code}')
            print(response.json())

        print(' > Getting bytes...')
        response = requests.get(file_url)
        print(len(response.content))
        if response.status_code == 200:
            # Save the received bytes as a .wav file
            with open(output_file_bytes, 'wb') as audio_file:
                audio_file.write(response.content)
            print(f' > Audio file bytes saved as {output_file_bytes}')
        else:
            print(f' > Error getting file bytes: {response.status_code}')
            print(response.json())

except requests.exceptions.RequestException as e:
    print(f'Request failed: {e}')

finally:
    if 'server_process' in locals():
        server_process.terminate()
        server_process.wait()