import logging, os
from openai import OpenAI

SERVER_PORT = os.getenv("SERVER_PORT", 5000)
version = 'v2'
output_file = 'outputs/openai_lib_example.wav'
if os.path.exists(output_file):
    os.remove(output_file)

try:
    # Initialize OpenAI client
    client = OpenAI(
        base_url=f'http://localhost:{SERVER_PORT}/{version}',
        api_key='not-needed',  # Required but ignored by OpenAI
    )
    # Make request to OpenAI API
    with client.audio.speech.with_streaming_response.create(
        input='Hello, this is a test. I am here, there and everywhere',
        model='en',
        voice="elon",
        #extra_body={"accent": "en-au"} , # v2 only
        #extra_body={"style": "angry"} , # v1 only
        response_format="wav"
    ) as response:
        response.stream_to_file(output_file)

except Exception as e:
    logging.error(f"Unexpected error: {e}")
