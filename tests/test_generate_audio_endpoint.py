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

class TestV1(IsolatedAsyncioTestCase):

    async def asyncSetUp(self):
        self.client = app.test_client()
        self.url = '/v1/generate-audio'

    async def test_url_response(self):
        out_file = 'outputs/test_url_response_v1.wav'
        if os.path.exists(out_file):
            os.remove(out_file)
        payload = {
            'model': 'en',
            'input': 'Let me know how you feel, we might just have a deal.',
            'response_format': 'url',
        }
        async with self.client as c:
            response = await c.post(self.url, json=payload)
            self.assertEqual(response.status_code, 200)
            response_data = await response.get_json()
            file_url = response_data['result']['data']['url']
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
            'model': 'en',
            'input': 'Let me know how you feel, we might just have a deal.',
            'response_format': 'bytes'
        }
        async with self.client as c:
            response = await c.post(self.url, json=payload)
            self.assertEqual(response.status_code, 200)
            response_data = await response.get_data()
            with open(out_file, 'wb') as audio_file:
                audio_file.write(response_data)
            self.assertTrue(os.path.exists(out_file), f"File {out_file} does not exist.")
            #print(f' > Audio file saved as {out_file}')

    async def test_base64_response(self):
        out_file = 'outputs/test_base64_response_v1.wav'
        if os.path.exists(out_file):
            os.remove(out_file)
        payload = {
            'model': 'en',
            'input': 'Let me know how you feel, we might just have a deal.',
            'response_format': 'base64'
        }
        async with self.client as c:
            response = await c.post(self.url, json=payload)
            self.assertEqual(response.status_code, 200)
            response_data = await response.get_json()
            audio_base64 = response_data['result']['data']['audio_data']
            with open(out_file, 'wb') as audio_file:
                audio_data = base64.b64decode(audio_base64)
                audio_file.write(audio_data)
            self.assertTrue(os.path.exists(out_file), f"File {out_file} does not exist.")
            #print(f' > Audio file saved as {out_file}')

    async def test_stream_response(self):
        #out_file = 'outputs/test_generate_audio_stream.wav'
        #if os.path.exists(out_file):
        #    os.remove(out_file)
        payload = {
            'model': 'en',
            'input': "Let me know how you feel, we might just have a deal.I remember as a child, and as a young budding naturalist, spending all my time observing and testing the world around me—moving pieces, altering the flow of things, and documenting ways the world responded to me. Now, as an adult and a professional naturalist, I approached language in the same way, not from an academic point of view but as a curious child still building little mud dams in creeks and chasing after frogs.",
            'response_format': 'stream'
        }
        async with self.client as c:
            response = await c.post(self.url, json=payload)
            self.assertEqual(response.status_code, 200)

    async def test_style_param(self):
        out_file = 'outputs/test_style_param_v1.wav'
        if os.path.exists(out_file):
            os.remove(out_file)
        payload = {
            'model': 'en',
            'input': 'Let me know how you feel, we might just have a deal.',
            'voice': 'elon',
            'response_format': 'url',
            'style': 'excited'
        }
        async with self.client as c:
            response = await c.post(self.url, json=payload)
            self.assertEqual(response.status_code, 200)
            response_data = await response.get_json()
            file_url = response_data['result']['data']['url']
            response = await c.get(file_url)
            self.assertEqual(response.status_code, 200)
            response_data = await response.get_data()
            with open(out_file, 'wb') as audio_file:
                audio_file.write(response_data)
            self.assertTrue(os.path.exists(out_file), f"File {out_file} does not exist.")
            #print(f'Audio file saved as {out_file}')

    async def test_voice_param(self):
        out_file = 'outputs/test_voice_param_rachel_v1.wav'
        if os.path.exists(out_file):
            os.remove(out_file)
        payload = {
            'model': 'en',
            'input': 'Let me know how you feel, we might just have a deal.',
            'response_format': 'url',
            'voice': 'rachel'
        }
        async with self.client as c:
            response = await c.post(self.url, json=payload)
            self.assertEqual(response.status_code, 200)
            response_data = await response.get_json()
            file_url = response_data['result']['data']['url']
            response = await c.get(file_url)
            self.assertEqual(response.status_code, 200)
            response_data = await response.get_data()
            with open(out_file, 'wb') as audio_file:
                audio_file.write(response_data)
            self.assertTrue(os.path.exists(out_file), f"File {out_file} does not exist.")
            #print(f'Audio file saved as {out_file}')

    async def test_model_param(self):
        out_file = 'outputs/test_model_param_zh_v1.wav'
        if os.path.exists(out_file):
            os.remove(out_file)
        payload = {
            'model': 'zh',
            'input': '今天天气真好，我们一起出去吃饭吧。',
            'response_format': 'url',
        }
        async with self.client as c:
            response = await c.post(self.url, json=payload)
            self.assertEqual(response.status_code, 200)
            response_data = await response.get_json()
            file_url = response_data['result']['data']['url']
            response = await c.get(file_url)
            self.assertEqual(response.status_code, 200)
            response_data = await response.get_data()
            with open(out_file, 'wb') as audio_file:
                audio_file.write(response_data)
            self.assertTrue(os.path.exists(out_file), f"File {out_file} does not exist.")
            #print(f'Audio file saved as {out_file}')

    async def test_raw_voice_param(self):
        out_file = 'outputs/test_raw_voice_param_v1.wav'
        if os.path.exists(out_file):
            os.remove(out_file)
        payload = {
            'model': 'en',
            'input': 'Let me know how you feel, we might just have a deal.',
            'speed': 1.0,
            'response_format': 'url',
            'voice': 'raw'
        }
        async with self.client as c:
            response = await c.post(self.url, json=payload)
            self.assertEqual(response.status_code, 200)
            response_data = await response.get_json()
            file_url = response_data['result']['data']['url']
            response = await c.get(file_url)
            self.assertEqual(response.status_code, 200)
            response_data = await response.get_data()
            with open(out_file, 'wb') as audio_file:
                audio_file.write(response_data)
            self.assertTrue(os.path.exists(out_file), f"File {out_file} does not exist.")
            #print(f'Audio file saved as {out_file}')

    async def test_default_params(self):
        out_file = 'outputs/test_default_params_v1.wav'
        if os.path.exists(out_file):
            os.remove(out_file)
        payload = {
            'model': 'en',
            'input': 'Let me know how you feel, we might just have a deal.'
        }
        async with self.client as c:
            response = await c.post(self.url, json=payload)
            self.assertEqual(response.status_code, 200)
            response_data = await response.get_json()
            file_url = response_data['result']['data']['url']
            response = await c.get(file_url)
            self.assertEqual(response.status_code, 200)
            response_data = await response.get_data()
            with open(out_file, 'wb') as audio_file:
                audio_file.write(response_data)
            self.assertTrue(os.path.exists(out_file), f"File {out_file} does not exist.")
            #print(f'Audio file saved as {out_file}')

    async def test_params_errors(self):
        # Required input error
        payload = {
            'model': 'en',
        }
        async with self.client as c:
            response = await c.post(self.url, json=payload)
            self.assertEqual(response.status_code, 400)
        # Required model error
        payload = {
            'input': 'Let me know how you feel, we might just have a deal.'
        }
        async with self.client as c:
            response = await c.post(self.url, json=payload)
            self.assertEqual(response.status_code, 400)
        # Wrong param error
        payload = {
            'model': 'en',
            'invalid_param': 'error_here',
            'input': 'Let me know how you feel, we might just have a deal.'
        }
        async with self.client as c:
            response = await c.post(self.url, json=payload)
            self.assertEqual(response.status_code, 400)
        # Wrong response_format value error
        payload = {
            'model': 'en',
            'input': 'Let me know how you feel, we might just have a deal.',
            'response_format': 'invalid_value'
        }
        async with self.client as c:
            response = await c.post(self.url, json=payload)
            self.assertEqual(response.status_code, 400)
        # Wrong model value error
        payload = {
            'model': 'en',
            'model': 'invalid_value',
            'input': 'Let me know how you feel, we might just have a deal.'
        }
        async with self.client as c:
            response = await c.post(self.url, json=payload)
            self.assertEqual(response.status_code, 400)
        # Wrong voice value error
        payload = {
            'model': 'en',
            'voice': 'invalid_value',
            'input': 'Let me know how you feel, we might just have a deal.'
        }
        async with self.client as c:
            response = await c.post(self.url, json=payload)
            self.assertEqual(response.status_code, 400)
        # Wrong style value error
        payload = {
            'model': 'en',
            'style': 'invalid_value',
            'input': 'Let me know how you feel, we might just have a deal.'
        }
        async with self.client as c:
            response = await c.post(self.url, json=payload)
            self.assertEqual(response.status_code, 400)
        # model does not support style param error
        payload = {
            'model': 'zh',
            'input': '今天天气真好，我们一起出去吃饭吧。',
            'style': 'invalid_value',
        }
        async with self.client as c:
            response = await c.post(self.url, json=payload)
            self.assertEqual(response.status_code, 400)

class TestV2(IsolatedAsyncioTestCase):

    async def asyncSetUp(self):
        self.client = app.test_client()
        self.url = '/v2/generate-audio'

    async def test_url_response(self):
        out_file = 'outputs/test_url_response_v2.wav'
        if os.path.exists(out_file):
            os.remove(out_file)
        payload = {
            'model': 'en',
            'input': 'Let me know how you feel, we might just have a deal.',
            'speed': 1.0,
            'response_format': 'url'
        }
        async with self.client as c:
            response = await c.post(self.url, json=payload)
            self.assertEqual(response.status_code, 200)
            response_data = await response.get_json()
            file_url = response_data['result']['data']['url']
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
            'model': 'en',
            'input': 'Let me know how you feel, we might just have a deal.',
            'speed': 1.0,
            'response_format': 'bytes'
        }
        async with self.client as c:
            response = await c.post(self.url, json=payload)
            self.assertEqual(response.status_code, 200)
            response_data = await response.get_data()
            with open(out_file, 'wb') as audio_file:
                audio_file.write(response_data)
            self.assertTrue(os.path.exists(out_file), f"File {out_file} does not exist.")
            #print(f' > Audio file saved as {out_file}')

    async def test_base64_response(self):
        out_file = 'outputs/test_base64_response_v2.wav'
        if os.path.exists(out_file):
            os.remove(out_file)
        payload = {
            'model': 'en',
            'input': 'Let me know how you feel, we might just have a deal.',
            'response_format': 'base64'
        }
        async with self.client as c:
            response = await c.post(self.url, json=payload)
            self.assertEqual(response.status_code, 200)
            response_data = await response.get_json()
            audio_base64 = response_data['result']['data']['audio_data']
            with open(out_file, 'wb') as audio_file:
                audio_data = base64.b64decode(audio_base64)
                audio_file.write(audio_data)
            self.assertTrue(os.path.exists(out_file), f"File {out_file} does not exist.")
            #print(f' > Audio file saved as {out_file}')

    async def test_stream_response(self):
        out_file = 'outputs/test_generate_audio_stream.wav'
        if os.path.exists(out_file):
            os.remove(out_file)
        payload = {
            'model': 'en',
            'input': "Let me know how you feel, we might just have a deal.I remember as a child, and as a young budding naturalist, spending all my time observing and testing the world around me—moving pieces, altering the flow of things, and documenting ways the world responded to me. Now, as an adult and a professional naturalist, I approached language in the same way, not from an academic point of view but as a curious child still building little mud dams in creeks and chasing after frogs.",
            'speed': 1.0,
            'response_format': 'stream'
        }
        async with self.client as c:
            response = await c.post(self.url, json=payload)
            self.assertEqual(response.status_code, 200)

    async def test_accent_param(self):
        out_file = 'outputs/test_accent_param_v2.wav'
        if os.path.exists(out_file):
            os.remove(out_file)
        payload = {
            'model': 'en',
            'input': 'Let me know how you feel, we might just have a deal.',
            'speed': 1.0,
            'response_format': 'url',
            'accent': 'en-au'
        }
        async with self.client as c:
            response = await c.post(self.url, json=payload)
            self.assertEqual(response.status_code, 200)
            response_data = await response.get_json()
            file_url = response_data['result']['data']['url']
            response = await c.get(file_url)
            self.assertEqual(response.status_code, 200)
            response_data = await response.get_data()
            with open(out_file, 'wb') as audio_file:
                audio_file.write(response_data)
            self.assertTrue(os.path.exists(out_file), f"File {out_file} does not exist.")
            #print(f'Audio file saved as {out_file}')

    async def test_voice_param(self):
        out_file = 'outputs/test_voice_param_kaiwen_v2.wav'
        if os.path.exists(out_file):
            os.remove(out_file)
        payload = {
            'model': 'en',
            'input': 'Let me know how you feel, we might just have a deal.',
            'speed': 1.0,
            'response_format': 'url',
            'voice': 'kaiwen'
        }
        async with self.client as c:
            response = await c.post(self.url, json=payload)
            self.assertEqual(response.status_code, 200)
            response_data = await response.get_json()
            file_url = response_data['result']['data']['url']
            response = await c.get(file_url)
            self.assertEqual(response.status_code, 200)
            response_data = await response.get_data()
            with open(out_file, 'wb') as audio_file:
                audio_file.write(response_data)
            self.assertTrue(os.path.exists(out_file), f"File {out_file} does not exist.")
            #print(f'Audio file saved as {out_file}')

    async def test_model_param(self):
        out_file = 'outputs/test_model_param_es_v2.wav'
        if os.path.exists(out_file):
            os.remove(out_file)
        payload = {
            'model': 'es',
            'input': 'En veramo, las olas son mas fuertes.',
            'speed': 1.0,
            'response_format': 'url',
        }
        async with self.client as c:
            response = await c.post(self.url, json=payload)
            self.assertEqual(response.status_code, 200)
            response_data = await response.get_json()
            file_url = response_data['result']['data']['url']
            response = await c.get(file_url)
            self.assertEqual(response.status_code, 200)
            response_data = await response.get_data()
            with open(out_file, 'wb') as audio_file:
                audio_file.write(response_data)
            self.assertTrue(os.path.exists(out_file), f"File {out_file} does not exist.")
            #print(f'Audio file saved as {out_file}')

    async def test_raw_voice_param(self):
        out_file = 'outputs/test_raw_voice_param_v2.wav'
        if os.path.exists(out_file):
            os.remove(out_file)
        payload = {
            'model': 'en',
            'input': 'Let me know how you feel, we might just have a deal.',
            'speed': 1.0,
            'response_format': 'url',
            'voice': 'raw'
        }
        async with self.client as c:
            response = await c.post(self.url, json=payload)
            self.assertEqual(response.status_code, 200)
            response_data = await response.get_json()
            file_url = response_data['result']['data']['url']
            response = await c.get(file_url)
            self.assertEqual(response.status_code, 200)
            response_data = await response.get_data()
            with open(out_file, 'wb') as audio_file:
                audio_file.write(response_data)
            self.assertTrue(os.path.exists(out_file), f"File {out_file} does not exist.")
            #print(f'Audio file saved as {out_file}')

    async def test_default_params(self):
        out_file = 'outputs/test_default_params_v2.wav'
        if os.path.exists(out_file):
            os.remove(out_file)
        payload = {
            'model': 'en',
            'input': 'Let me know how you feel, we might just have a deal.'
        }
        async with self.client as c:
            response = await c.post(self.url, json=payload)
            self.assertEqual(response.status_code, 200)
            response_data = await response.get_json()
            file_url = response_data['result']['data']['url']
            response = await c.get(file_url)
            self.assertEqual(response.status_code, 200)
            response_data = await response.get_data()
            with open(out_file, 'wb') as audio_file:
                audio_file.write(response_data)
            self.assertTrue(os.path.exists(out_file), f"File {out_file} does not exist.")
            #print(f'Audio file saved as {out_file}')

    async def test_params_errors(self):
        # Required input error
        payload = {
            'model': 'en',
        }
        async with self.client as c:
            response = await c.post(self.url, json=payload)
            self.assertEqual(response.status_code, 400)
        # Required model error
        payload = {
            'input': 'Let me know how you feel, we might just have a deal.'
        }
        async with self.client as c:
            response = await c.post(self.url, json=payload)
            self.assertEqual(response.status_code, 400)
        # Wrong param error
        payload = {
            'model': 'en',
            'invalid_param': 'error_here',
            'input': 'Let me know how you feel, we might just have a deal.'
        }
        async with self.client as c:
            response = await c.post(self.url, json=payload)
            self.assertEqual(response.status_code, 400)
        # Wrong response_format value error
        payload = {
            'model': 'en',
            'input': 'Let me know how you feel, we might just have a deal.',
            'response_format': 'invalid_value'
        }
        async with self.client as c:
            response = await c.post(self.url, json=payload)
            self.assertEqual(response.status_code, 400)
        # Wrong model value error
        payload = {
            'model': 'en',
            'model': 'invalid_value',
            'input': 'Let me know how you feel, we might just have a deal.'
        }
        async with self.client as c:
            response = await c.post(self.url, json=payload)
            self.assertEqual(response.status_code, 400)
        # Wrong voice value error
        payload = {
            'model': 'en',
            'voice': 'invalid_value',
            'input': 'Let me know how you feel, we might just have a deal.'
        }
        async with self.client as c:
            response = await c.post(self.url, json=payload)
            self.assertEqual(response.status_code, 400)
        # Wrong accent param error
        payload = {
            'model': 'en',
            'accent': 'invalid_value',
            'input': 'Let me know how you feel, we might just have a deal.'
        }
        async with self.client as c:
            response = await c.post(self.url, json=payload)
            self.assertEqual(response.status_code, 400)
