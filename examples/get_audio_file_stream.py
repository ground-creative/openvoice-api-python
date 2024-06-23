import requests, os

output_file = 'outputs/get_audio_file_stream.wav'
if os.path.exists(output_file):
    os.remove(output_file)

# Define the URL of the generate_audio endpoint
url = 'http://localhost:5001/v2/generate-audio/'

# Define the parameters for the POST request
payload = {
    'language': 'en',
    'text': 'profoundly creative and freeing. And underneath everything, this playful exploration of language is about dissent, about rising up and crying out in support of that which is alive and vital. This book is about imagination, about truth-telling and contemplation; it is an undertaking that is fierce, creative, and honest. My own journey toward language was sparked in 1996 when I discovered Keith Basso’s astonishing book Wisdom Sits in Places. Writing about the unique place-making language of the Western Apache, Basso described language in a way that I’d never considered before, as roots and fragments strung together to sing of the land. This idea intrigued me so much that I began carrying Donald Borror’s classic little book, the Dictionary of Word Roots and Combining Forms.',
    'speed': 1.0,
    'response_format': 'url'
    #'style': 'excited' # v1 only
    #'accent': 'en-au' #v2 only
}

try:
    # Send the POST request to generate the audio
    response = requests.post(url, json=payload, stream=False)
    if response.status_code == 200:
        response_data = response.json()
        file_url = response_data['data']['url']
        data = {'stream': True}
        response = requests.get(file_url, params=data, stream=True)
        if response.status_code == 200:
            with open(output_file, 'wb') as audio_file:
                for chunk in response.iter_content(chunk_size=1024):
                    if chunk:  # filter out keep-alive new chunks
                        audio_file.write(chunk)
            print(f' > Audio file saved as {output_file}')
        else:
            print(f' > Error getting file url: {response.status_code}')
            print(response.json())
    else:
        print(f' > Error: {response.status_code}')
        print(response.json())

except requests.exceptions.RequestException as e:
    print(f' > Request failed: {e}')