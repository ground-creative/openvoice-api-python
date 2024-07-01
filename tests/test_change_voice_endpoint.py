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
        self.url_v1 = '/v1/change-voice'
        self.url_v2 = '/v2/change-voice'

    async def test_v1_response(self):
        out_file = 'outputs/test_change_voice_v1_response.wav'
        if os.path.exists(out_file):
            os.remove(out_file)
        payload = {
            'model': 'en',
            'input': 'Let me know how you feel, we might just have a deal.',
            'response_format': 'base64'
        }
        async with self.client as c:
            response = await c.post('/v1/generate-audio', json=payload)
            self.assertEqual(response.status_code, 200)
            response_data = await response.get_json()
        payload = {
            'model': 'en',
            'response_format': 'bytes',
            'voice': 'elon',
            'audio_data': response_data['result']['data']['audio_data']
        }
        async with self.client as c:
            response = await c.post(self.url_v1, json=payload)
            self.assertEqual(response.status_code, 200)
            response_data = await response.get_data()
            with open(out_file, 'wb') as audio_file:
                audio_file.write(response_data)
            self.assertTrue(os.path.exists(out_file), f"File {out_file} does not exist.")
            #print(f'Audio file saved as {out_file}')

    async def test_v2_response(self):
        out_file = 'outputs/test_change_voice_v2_response.wav'
        if os.path.exists(out_file):
            os.remove(out_file)
        payload = {
            'model': 'en',
            'input': 'Let me know how you feel, we might just have a deal.',
            'response_format': 'base64'
        }
        async with self.client as c:
            response = await c.post('/v2/generate-audio', json=payload)
            self.assertEqual(response.status_code, 200)
            response_data = await response.get_json()
        payload = {
            'model': 'en',
            'response_format': 'bytes',
            'voice': 'elon',
            'audio_data': response_data['result']['data']['audio_data']
        }
        async with self.client as c:
            response = await c.post(self.url_v2, json=payload)
            self.assertEqual(response.status_code, 200)
            response_data = await response.get_data()
            with open(out_file, 'wb') as audio_file:
                audio_file.write(response_data)
            self.assertTrue(os.path.exists(out_file), f"File {out_file} does not exist.")
            #print(f'Audio file saved as {out_file}')

    async def test_params_errors(self):
        # audio_data required param error
        payload = {
            'model': 'en',
            'response_format': 'bytes',
            'voice': 'elon',
        }
        async with self.client as c:
            response = await c.post(self.url_v1, json=payload)
            self.assertEqual(response.status_code, 400)
        # Unsupported audio file type audio_data param error
        payload = {
            'model': 'en',
            'response_format': 'bytes',
            'audio_data': base64.b64encode(b'123454678').decode('utf-8')
        }
        async with self.client as c:
            response = await c.post(self.url_v1, json=payload)
            self.assertEqual(response.status_code, 400)
        # Get some audio data for testing
        payload = {
            'model': 'en',
            'input': 'Let me know how you feel, we might just have a deal.',
            'response_format': 'base64',
            'voice': 'raw'
        }
        async with self.client as c:
            response = await c.post('/v1/generate-audio', json=payload)
            self.assertEqual(response.status_code, 200)
            response_data = await response.get_json()
            audio_base64 = response_data['result']['data']['audio_data']
        # voice required param error
        payload = {
            'model': 'en',
            'response_format': 'bytes',
            'audio_data': audio_base64
        }
        async with self.client as c:
            response = await c.post(self.url_v2, json=payload)
            self.assertEqual(response.status_code, 400)
        # Not allowed input parameter error
        payload = {
            'model': 'en',
            'response_format': 'bytes',
            'input': 'Let me know how you feel, we might just have a deal.',
            'audio_data': audio_base64
        }
        async with self.client as c:
            response = await c.post(self.url_v1, json=payload)
            self.assertEqual(response.status_code, 400)
        # Unsupported style parameter error v1
        payload = {
            'model': 'en',
            'response_format': 'bytes',
            'style': 'angry',
            'audio_data': audio_base64
        }
        async with self.client as c:
            response = await c.post(self.url_v1, json=payload)
            self.assertEqual(response.status_code, 400)
        # Unsupported speed parameter error
        payload = {
            'model': 'en',
            'response_format': 'bytes',
            'speed': 1.0,
            'audio_data': audio_base64
        }
        async with self.client as c:
            response = await c.post(self.url_v1, json=payload)
            self.assertEqual(response.status_code, 400)