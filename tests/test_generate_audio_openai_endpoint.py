import os, sys, base64
from unittest import IsolatedAsyncioTestCase
from dotenv import load_dotenv

load_dotenv()

os.environ['LOG_LEVEL'] = os.getenv("LOG_LEVEL", "DEBUG")
os.environ['SERVER_ADDRESS'] = os.getenv("SERVER_ADDRESS", "0.0.0.0")
os.environ['SERVER_PORT'] = os.getenv("SERVER_PORT", 5000)
os.environ['AUDIO_FILES_PATH'] = os.getenv("AUDIO_FILES_PATH", '/tmp')
os.environ['MODEL_LANGUAGES_V1'] = os.getenv("MODEL_LANGUAGES_V1", "EN:English,ZH:Chinese")
os.environ['MODEL_LANGUAGES_V2'] = os.getenv("MODEL_LANGUAGES_V2", "EN,ES,FR,ZH,JP")
os.environ['SPEAKERS_FOLDER'] = os.getenv("SPEAKERS_FOLDER", "speakers")
os.environ['SPEAKERS'] = os.getenv("SPEAKERS", "elon,rachel,kaiwen")
os.environ['WATERMARK'] = os.getenv("WATERMARK", "@OpenVoiceAPI")
os.environ['DEVICE_V1'] = os.getenv("DEVICE_V1", "cuda:0")
os.environ['DEVICE_V2'] = os.getenv("DEVICE_V2", "cuda:0")
os.environ['SUPPORTED_STYLES_V1'] = os.getenv("SUPPORTED_STYLES_V1", "English")
os.environ['USE_VAD'] = os.getenv("USE_VAD", False)

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../')))

from app import app

class Test(IsolatedAsyncioTestCase):

    async def asyncSetUp(self):
        self.client = app.test_client()

    async def test_stream_response(self):
        #out_file = 'outputs/test_generate_audio_stream.wav'
        #if os.path.exists(out_file):
        #    os.remove(out_file)
        payload = {
            'model': 'en',
            'input': "Let me know how you feel, we might just have a deal.I remember as a child, and as a young budding naturalist, spending all my time observing and testing the world around me—moving pieces, altering the flow of things, and documenting ways the world responded to me. Now, as an adult and a professional naturalist, I approached language in the same way, not from an academic point of view but as a curious child still building little mud dams in creeks and chasing after frogs.",
            'speed': 1.0,
            'response_format': 'wav'
        }
        async with self.client as c:
            response = await c.post('/v1/audio/speech', json=payload)
            self.assertEqual(response.status_code, 200)

    async def test_params_errors(self):
        # Wrong response_format value error
        payload = {
            'model': 'en',
            'input': 'Let me know how you feel, we might just have a deal.',
            'response_format': 'invalid_value'
        }
        async with self.client as c:
            response = await c.post('/v1/audio/speech', json=payload)
            self.assertEqual(response.status_code, 400)