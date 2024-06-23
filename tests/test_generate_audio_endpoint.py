import os, sys
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

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../')))

from app import app

class TestV1(IsolatedAsyncioTestCase):

    async def asyncSetUp(self):
        self.client = app.test_client()

    async def test_url_response(self):
        out_file = 'outputs/test_url_response_v1.wav'
        if os.path.exists(out_file):
            os.remove(out_file)
        payload = {
            'language': 'en',
            'text': 'Let me know how you feel, we might just have a deal.',
            'speed': 1.0,
            'response_format': 'url'
        }
        async with self.client as c:
            response = await c.post('/generate-audio/v1/', json=payload)
            self.assertEqual(response.status_code, 200)
            response_data = await response.get_json()
            file_url = response_data['data']['url']
            response = await c.get(file_url)
            self.assertEqual(response.status_code, 200)
            response_data = await response.get_data()
            with open(out_file, 'wb') as audio_file:
                audio_file.write(response_data)
            self.assertTrue(os.path.exists(out_file), f"File {out_file} does not exist.")
            #print(f'Audio file saved as {out_file}')

    async def test_bytes_response(self):
        out_file = 'outputs/test_bytes_response_v1.wav'
        if os.path.exists(out_file):
            os.remove(out_file)
        payload = {
            'language': 'en',
            'text': 'Let me know how you feel, we might just have a deal.',
            'speed': 1.0,
            'response_format': 'bytes'
        }
        async with self.client as c:
            response = await c.post('/generate-audio/v1/', json=payload)
            self.assertEqual(response.status_code, 200)
            response_data = await response.get_data()
            with open(out_file, 'wb') as audio_file:
                audio_file.write(response_data)
            self.assertTrue(os.path.exists(out_file), f"File {out_file} does not exist.")
            #print(f' > Audio file saved as {out_file}')

    async def test_stream_response(self):
        #out_file = 'outputs/test_generate_audio_stream.wav'
        #if os.path.exists(out_file):
        #    os.remove(out_file)
        payload = {
            'language': 'en',
            'text': "Let me know how you feel, we might just have a deal.I remember as a child, and as a young budding naturalist, spending all my time observing and testing the world around me—moving pieces, altering the flow of things, and documenting ways the world responded to me. Now, as an adult and a professional naturalist, I approached language in the same way, not from an academic point of view but as a curious child still building little mud dams in creeks and chasing after frogs.",
            'speed': 1.0,
            'response_format': 'stream'
        }
        async with self.client as c:
            response = await c.post('/generate-audio/v1/', json=payload)
            self.assertEqual(response.status_code, 200)

    async def test_style_param(self):
        out_file = 'outputs/test_style_param_v1.wav'
        if os.path.exists(out_file):
            os.remove(out_file)
        payload = {
            'language': 'en',
            'text': 'Let me know how you feel, we might just have a deal.',
            'speed': 1.0,
            'response_format': 'url',
            'style': 'excited'
        }
        async with self.client as c:
            response = await c.post('/generate-audio/v1/', json=payload)
            self.assertEqual(response.status_code, 200)
            response_data = await response.get_json()
            file_url = response_data['data']['url']
            response = await c.get(file_url)
            self.assertEqual(response.status_code, 200)
            response_data = await response.get_data()
            with open(out_file, 'wb') as audio_file:
                audio_file.write(response_data)
            self.assertTrue(os.path.exists(out_file), f"File {out_file} does not exist.")
            #print(f'Audio file saved as {out_file}')

    async def test_speaker_param(self):
        out_file = 'outputs/test_speaker_param_rachel_v1.wav'
        if os.path.exists(out_file):
            os.remove(out_file)
        payload = {
            'language': 'en',
            'text': 'Let me know how you feel, we might just have a deal.',
            'speed': 1.0,
            'response_format': 'url',
            'speaker': 'rachel'
        }
        async with self.client as c:
            response = await c.post('/generate-audio/v1/', json=payload)
            self.assertEqual(response.status_code, 200)
            response_data = await response.get_json()
            file_url = response_data['data']['url']
            response = await c.get(file_url)
            self.assertEqual(response.status_code, 200)
            response_data = await response.get_data()
            with open(out_file, 'wb') as audio_file:
                audio_file.write(response_data)
            self.assertTrue(os.path.exists(out_file), f"File {out_file} does not exist.")
            #print(f'Audio file saved as {out_file}')

    async def test_language_param(self):
        out_file = 'outputs/test_language_param_zh_v1.wav'
        if os.path.exists(out_file):
            os.remove(out_file)
        payload = {
            'language': 'zh',
            'text': '今天天气真好，我们一起出去吃饭吧。',
            'speed': 1.0,
            'response_format': 'url',
        }
        async with self.client as c:
            response = await c.post('/generate-audio/v1/', json=payload)
            self.assertEqual(response.status_code, 200)
            response_data = await response.get_json()
            file_url = response_data['data']['url']
            response = await c.get(file_url)
            self.assertEqual(response.status_code, 200)
            response_data = await response.get_data()
            with open(out_file, 'wb') as audio_file:
                audio_file.write(response_data)
            self.assertTrue(os.path.exists(out_file), f"File {out_file} does not exist.")
            #print(f'Audio file saved as {out_file}')

    async def test_params_errors(self):
        # Required text error
        payload = {}
        async with self.client as c:
            response = await c.post('/generate-audio/v1/', json=payload)
            self.assertEqual(response.status_code, 400)
        # Wrong param error
        payload = {
            'invalid_param': 'error_here',
            'text': 'Let me know how you feel, we might just have a deal.'
        }
        async with self.client as c:
            response = await c.post('/generate-audio/v1/', json=payload)
            self.assertEqual(response.status_code, 400)
        # Wrong response_format value error
        payload = {
            'text': 'Let me know how you feel, we might just have a deal.',
            'response_format': 'invalid_value'
        }
        async with self.client as c:
            response = await c.post('/generate-audio/v1/', json=payload)
            self.assertEqual(response.status_code, 400)
        # Wrong language value error
        payload = {
            'language': 'invalid_value',
            'text': 'Let me know how you feel, we might just have a deal.'
        }
        async with self.client as c:
            response = await c.post('/generate-audio/v1/', json=payload)
            response_data = await response.get_json()
            self.assertEqual(response.status_code, 400)
        # Wrong speaker value error
        payload = {
            'speaker': 'invalid_value',
            'text': 'Let me know how you feel, we might just have a deal.'
        }
        async with self.client as c:
            response = await c.post('/generate-audio/v1/', json=payload)
            self.assertEqual(response.status_code, 400)
        # Wrong style value error
        payload = {
            'style': 'invalid_value',
            'text': 'Let me know how you feel, we might just have a deal.'
        }
        async with self.client as c:
            response = await c.post('/generate-audio/v1/', json=payload)
            self.assertEqual(response.status_code, 400)
        # Language does not support style param error
        payload = {
            'language': 'zh',
            'text': '今天天气真好，我们一起出去吃饭吧。',
            'style': 'invalid_value',
            'text': 'Let me know how you feel, we might just have a deal.'
        }
        async with self.client as c:
            response = await c.post('/generate-audio/v1/', json=payload)
            self.assertEqual(response.status_code, 400)

class TestV2(IsolatedAsyncioTestCase):

    async def asyncSetUp(self):
        self.client = app.test_client()

    async def test_url_response(self):
        out_file = 'outputs/test_url_response_v2.wav'
        if os.path.exists(out_file):
            os.remove(out_file)
        payload = {
            'language': 'en',
            'text': 'Let me know how you feel, we might just have a deal.',
            'speed': 1.0,
            'response_format': 'url'
        }
        async with self.client as c:
            response = await c.post('/generate-audio/v2/', json=payload)
            self.assertEqual(response.status_code, 200)
            response_data = await response.get_json()
            file_url = response_data['data']['url']
            response = await c.get(file_url)
            self.assertEqual(response.status_code, 200)
            response_data = await response.get_data()
            with open(out_file, 'wb') as audio_file:
                audio_file.write(response_data)
            self.assertTrue(os.path.exists(out_file), f"File {out_file} does not exist.")
            #print(f'Audio file saved as {out_file}')

    async def test_bytes_response(self):
        out_file = 'outputs/test_bytes_response_v2.wav'
        if os.path.exists(out_file):
            os.remove(out_file)
        payload = {
            'language': 'en',
            'text': 'Let me know how you feel, we might just have a deal.',
            'speed': 1.0,
            'response_format': 'bytes'
        }
        async with self.client as c:
            response = await c.post('/generate-audio/v2/', json=payload)
            self.assertEqual(response.status_code, 200)
            response_data = await response.get_data()
            with open(out_file, 'wb') as audio_file:
                audio_file.write(response_data)
            self.assertTrue(os.path.exists(out_file), f"File {out_file} does not exist.")
            #print(f' > Audio file saved as {out_file}')

    async def test_stream_response(self):
        #out_file = 'outputs/test_generate_audio_stream.wav'
        #if os.path.exists(out_file):
        #    os.remove(out_file)
        payload = {
            'language': 'en',
            'text': "Let me know how you feel, we might just have a deal.I remember as a child, and as a young budding naturalist, spending all my time observing and testing the world around me—moving pieces, altering the flow of things, and documenting ways the world responded to me. Now, as an adult and a professional naturalist, I approached language in the same way, not from an academic point of view but as a curious child still building little mud dams in creeks and chasing after frogs.",
            'speed': 1.0,
            'response_format': 'stream'
        }
        async with self.client as c:
            response = await c.post('/generate-audio/v2/', json=payload)
            self.assertEqual(response.status_code, 200)

    async def test_accent_param(self):
        out_file = 'outputs/test_accent_param_v2.wav'
        if os.path.exists(out_file):
            os.remove(out_file)
        payload = {
            'language': 'en',
            'text': 'Let me know how you feel, we might just have a deal.',
            'speed': 1.0,
            'response_format': 'url',
            'accent': 'en-au'
        }
        async with self.client as c:
            response = await c.post('/generate-audio/v2/', json=payload)
            self.assertEqual(response.status_code, 200)
            response_data = await response.get_json()
            file_url = response_data['data']['url']
            response = await c.get(file_url)
            self.assertEqual(response.status_code, 200)
            response_data = await response.get_data()
            with open(out_file, 'wb') as audio_file:
                audio_file.write(response_data)
            self.assertTrue(os.path.exists(out_file), f"File {out_file} does not exist.")
            #print(f'Audio file saved as {out_file}')

    async def test_speaker_param(self):
        out_file = 'outputs/test_speaker_param_kaiwen_v2.wav'
        if os.path.exists(out_file):
            os.remove(out_file)
        payload = {
            'language': 'en',
            'text': 'Let me know how you feel, we might just have a deal.',
            'speed': 1.0,
            'response_format': 'url',
            'speaker': 'kaiwen'
        }
        async with self.client as c:
            response = await c.post('/generate-audio/v2/', json=payload)
            self.assertEqual(response.status_code, 200)
            response_data = await response.get_json()
            file_url = response_data['data']['url']
            response = await c.get(file_url)
            self.assertEqual(response.status_code, 200)
            response_data = await response.get_data()
            with open(out_file, 'wb') as audio_file:
                audio_file.write(response_data)
            self.assertTrue(os.path.exists(out_file), f"File {out_file} does not exist.")
            #print(f'Audio file saved as {out_file}')

    async def test_language_param(self):
        out_file = 'outputs/test_language_param_es_v2.wav'
        if os.path.exists(out_file):
            os.remove(out_file)
        payload = {
            'language': 'es',
            'text': 'En veramo, las olas son mas fuertes.',
            'speed': 1.0,
            'response_format': 'url',
        }
        async with self.client as c:
            response = await c.post('/generate-audio/v2/', json=payload)
            self.assertEqual(response.status_code, 200)
            response_data = await response.get_json()
            file_url = response_data['data']['url']
            response = await c.get(file_url)
            self.assertEqual(response.status_code, 200)
            response_data = await response.get_data()
            with open(out_file, 'wb') as audio_file:
                audio_file.write(response_data)
            self.assertTrue(os.path.exists(out_file), f"File {out_file} does not exist.")
            #print(f'Audio file saved as {out_file}')

    async def test_params_errors(self):
        # Required text error
        payload = {}
        async with self.client as c:
            response = await c.post('/generate-audio/v2/', json=payload)
            self.assertEqual(response.status_code, 400)
        # Wrong param error
        payload = {
            'invalid_param': 'error_here',
            'text': 'Let me know how you feel, we might just have a deal.'
        }
        async with self.client as c:
            response = await c.post('/generate-audio/v2/', json=payload)
            self.assertEqual(response.status_code, 400)
        # Wrong response_format param error
        payload = {
            'text': 'Let me know how you feel, we might just have a deal.',
            'response_format': 'invalid_value'
        }
        async with self.client as c:
            response = await c.post('/generate-audio/v2/', json=payload)
            self.assertEqual(response.status_code, 400)
        # Wrong language param error
        payload = {
            'language': 'invalid_value',
            'text': 'Let me know how you feel, we might just have a deal.'
        }
        async with self.client as c:
            response = await c.post('/generate-audio/v2/', json=payload)
            response_data = await response.get_json()
            self.assertEqual(response.status_code, 400)
        # Wrong speaker param error
        payload = {
            'speaker': 'invalid_value',
            'text': 'Let me know how you feel, we might just have a deal.'
        }
        async with self.client as c:
            response = await c.post('/generate-audio/v2/', json=payload)
            self.assertEqual(response.status_code, 400)
        # Wrong accent param error
        payload = {
            'accent': 'invalid_value',
            'text': 'Let me know how you feel, we might just have a deal.'
        }
        async with self.client as c:
            response = await c.post('/generate-audio/v2/', json=payload)
            self.assertEqual(response.status_code, 400)
