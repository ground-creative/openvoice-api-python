import logging, colorlog, os, torch, traceback
from quart import Quart, jsonify, request, redirect, send_file, Response, stream_with_context
from quart_cors import cors
from openvoice import se_extractor
from openvoice.api import ToneColorConverter, BaseSpeakerTTS
from melo.api import TTS
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

LOG_LEVEL = os.getenv("LOG_LEVEL", "DEBUG")
SERVER_ADDRESS = os.getenv("SERVER_ADDRESS", "0.0.0.0")
SERVER_PORT = os.getenv("SERVER_PORT", 5000)
AUDIO_FILES_PATH = os.getenv("AUDIO_FILES_PATH", '/tmp')
MODEL_LANGUAGES_V1 = os.getenv("MODEL_LANGUAGES_V1", "EN:English,ZH:Chinese").split(",")
MODEL_LANGUAGES_V2 = os.getenv("MODEL_LANGUAGES_V2", "EN,ES,FR,ZH,JP").split(",")
SPEAKERS_FOLDER = os.getenv("SPEAKERS_FOLDER", "speakers")
SPEAKERS = os.getenv("SPEAKERS", "elon,rachel,kaiwen").split(",")
WATERMARK = os.getenv("WATERMARK", "@OpenVoiceAPI")
DEVICE_V1 = os.getenv("DEVICE_V1", "cuda:0")
DEVICE_V2 = os.getenv("DEVICE_V2", "cuda:0")
OPENVOICE_PATH = '/app/OpenVoice'
BASE_DIRECTORY = os.path.dirname(os.path.abspath(__file__))

MODEL_LANGUAGES_CODES_V1 = []
MODEL_LANGUAGES_NAMES_V1 = {}
for item in MODEL_LANGUAGES_V1:
    code, name = item.split(":")
    MODEL_LANGUAGES_CODES_V1.append(code)
    MODEL_LANGUAGES_NAMES_V1[code] = name

STYLES_V1 = ['default', 'whispering', 'shouting', 'excited', 'cheerful', 'terrified', 'angry', 'sad', 'friendly']

# Initialize Quart app
app = Quart(__name__)
app = cors(app, allow_origin="*")

# Configure logging
#logging.basicConfig(filename='/logs/api.log', level=logging.INFO, 
#                    format='%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')

# Configure colored logging
handler = colorlog.StreamHandler()
formatter = colorlog.ColoredFormatter(
    '%(log_color)s%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    log_colors={
        'DEBUG': 'white',
        'INFO': 'green',
        'WARNING': 'yellow',
        'ERROR': 'red',
        'CRITICAL': 'bold_red',
    }
)
handler.setFormatter(formatter)
logger = colorlog.getLogger()
logger.addHandler(handler)
logger.setLevel(LOG_LEVEL)

if (not MODEL_LANGUAGES_CODES_V1 or all(lang == '' for lang in MODEL_LANGUAGES_CODES_V1)) and (not MODEL_LANGUAGES_V2 or all(lang == '' for lang in MODEL_LANGUAGES_V2)):
    #app.logger.error(" > Please specify at least one language model (version 1 or version 2) to use")
    raise ValueError("Please specify at least one language model (version 1 or version 2) to use")
SPEAKERS = [lang for lang in SPEAKERS if lang.strip()]
if not SPEAKERS:
    raise ValueError("Please specify at least one speaker from the speakers folder")

# Load version 1
MODEL_LANGUAGES_CODES_V1 = [lang for lang in MODEL_LANGUAGES_CODES_V1 if lang.strip()]
if MODEL_LANGUAGES_CODES_V1:
    app.logger.info(" > Loading v1 tone color converter.")
    ckpt_converter = f'{OPENVOICE_PATH}/checkpoints/converter'
    tone_color_converter_v1 = ToneColorConverter(f'{ckpt_converter}/config.json', device=DEVICE_V1)
    tone_color_converter_v1.load_ckpt(f'{ckpt_converter}/checkpoint.pth')
    ckpt_base = {}
    base_speaker_tts = {}
    app.logger.info(" > Loading v1 models: " + ", ".join(MODEL_LANGUAGES_CODES_V1))
    for lang in MODEL_LANGUAGES_CODES_V1:
        lang = lang.upper()
        ckpt_base[lang] = f'{OPENVOICE_PATH}/checkpoints/base_speakers/{lang}'
        base_speaker_tts[lang] = BaseSpeakerTTS(f"{ckpt_base[lang]}/config.json", device=DEVICE_V1)
        base_speaker_tts[lang].load_ckpt(f"{ckpt_base[lang]}/checkpoint.pth")

# Load version 2
MODEL_LANGUAGES_V2 = [lang for lang in MODEL_LANGUAGES_V2 if lang.strip()]
if MODEL_LANGUAGES_V2:
    app.logger.info(" > Loading v2 tone color converter.")
    ckpt_converter_v2 = f'{OPENVOICE_PATH}/checkpoints_v2/converter'
    tone_color_converter_v2 = ToneColorConverter(f'{ckpt_converter_v2}/config.json', device=DEVICE_V2)
    tone_color_converter_v2.load_ckpt(f'{ckpt_converter_v2}/checkpoint.pth')
    models = {}
    speaker_ids = {}
    app.logger.info(" > Loading v2 models: " + ", ".join(MODEL_LANGUAGES_V2))
    for lang in MODEL_LANGUAGES_V2:
        lang = lang.upper()
        models[lang] = TTS(language=lang, device=DEVICE_V2)
        speaker_ids[lang] = models[lang].hps.data.spk2id

# Load speakers
reference_speakers = {}
targets_v2 = {}
targets_v1 = {}
for speaker in SPEAKERS:
    reference_speakers[speaker] = f'{BASE_DIRECTORY}/{SPEAKERS_FOLDER}/{speaker}.mp3'
    if MODEL_LANGUAGES_CODES_V1:
        app.logger.info(f" > Loading SE extractors v1 for speaker {speaker}")
        targets_v1[speaker], audio_name = se_extractor.get_se(reference_speakers[speaker], tone_color_converter_v1, vad=False)
    if MODEL_LANGUAGES_V2:
        app.logger.info(f" > Loading SE extractors v2 for speaker {speaker}")
        targets_v2[speaker], audio_name = se_extractor.get_se(reference_speakers[speaker], tone_color_converter_v2, vad=False)

def generate_random_filename(prefix='', ext='wav'):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")[:-3]
    random_filename = f"{prefix}{timestamp}.{ext}"
    return random_filename

@app.before_request
def log_request_info():
    logger.debug(f"Started processing {request.method} request from {request.remote_addr} => {request.url}")
    if not request.path.endswith('/') and request.path != '/' and not request.path.startswith('/audio-file/'):
        return redirect(f"{request.url}/", code=301)
    
@app.teardown_request
def log_teardown(exception=None):
    if exception:
        logger.error(f"Exception occurred: {exception}")
    logger.debug(f"Finished processing {request.method} request from {request.remote_addr} => {request.url}")

@app.route('/')
def home():
    return jsonify(data={"message": "OpenVoice API"})

@app.route('/generate-audio/<version>/', methods=['POST'])
async def generate_audio(version):

    if version not in ["v1", "v2"]:
        return jsonify({"error": "Invalid version"}), 400
    
    VALID_PARAMS = ['language', 'speed', 'text', "response_format", "speaker"]

    if version == 'v1':

        if 'ckpt_base' not in globals():
            return jsonify(data={"message": 'version 1 module is not loaded'}), 500
        
        VALID_PARAMS.append('style')
        
    elif version == 'v2':

        if 'models' not in globals():
            return jsonify(data={"message": 'version 2 module is not loaded'}), 500
        
        VALID_PARAMS.append('accent')

    try:
        args = await request.get_json()
        invalid_params = [param for param in args if param not in VALID_PARAMS]
        raw_response_format = args.get('response_format', 'url')
        response_format = raw_response_format.lower()
        valid_response_formats = ['url', 'bytes', 'stream']
        
        if response_format not in valid_response_formats:
            error_message = f"Invalid response_format sent: {raw_response_format}. valid params are: {', '.join(valid_response_formats)}"
            app.logger.error(error_message)
            return jsonify(data={"message": error_message}), 400
        
        if invalid_params:
            error_message = f"Invalid parameter(s) sent: {', '.join(invalid_params)}. valid params are: {', '.join(VALID_PARAMS)}"
            app.logger.error(error_message)
            return jsonify(data={"message": error_message}), 400
        
        raw_lang = args.get('language', 'en')
        language = raw_lang.upper()
        
        if language not in models:

            if version == 'v1':
                valid_lang_keys = ", ".join(MODEL_LANGUAGES_CODES_V1).lower()
            elif version == 'v2':
                valid_lang_keys = ", ".join(MODEL_LANGUAGES_V2).lower()
            else:
                return jsonify(data={"message": f"Version {version} not supported"}), 500
            error_message = f"Invalid language key, valid values are: " + valid_lang_keys
            app.logger.error(error_message)
            return jsonify(data={"message": error_message}), 400

        speed = float(args.get('speed', 1.0))
        text = args.get('text')

        if text is None or text == '':
            error_message = "Parameter 'text' is required"
            app.logger.error(error_message)
            return jsonify(data={"message": error_message}), 400

        if version == 'v1':
            speaker = args.get('speaker', SPEAKERS[0]).lower()
            
            if speaker not in SPEAKERS:
                joined_keys = ' '.join(SPEAKERS)
                error_message = f"Invalid speaker '{speaker}', valid values are: " + joined_keys
                app.logger.error(error_message)
                return jsonify(data={"message": error_message}), 400
           
            style = args.get('style', 'default').lower()
            
            if style not in STYLES_V1:
                joined_keys = ' '.join(STYLES_V1)
                error_message = f"Invalid style '{style}', valid values are: " + joined_keys
                app.logger.error(error_message)
                return jsonify(data={"message": error_message}), 400

            output_filename = generate_random_filename('', 'wav')
            output_path = f'{AUDIO_FILES_PATH}/{output_filename}' 
            app.logger.info(f' > Loading speaker v1 model for {speaker}...')
            source_se = torch.load(f'{ckpt_base[language]}/{raw_lang}_default_se.pth').to(DEVICE_V1)
            app.logger.info(f' > Converting text to audio...')
            base_speaker_tts[language].tts(text, output_path, speaker=style, language=MODEL_LANGUAGES_NAMES_V1[language], speed=speed)
            if speaker != 'raw':
                output_filename = generate_random_filename('', 'wav')
                save_path = f'{AUDIO_FILES_PATH}/{output_filename}'
                target_se = targets_v1[speaker]
                tone_color_converter_v1.convert(
                audio_src_path=output_path, 
                    src_se=source_se, 
                    tgt_se=target_se, 
                    output_path=save_path,
                    message=WATERMARK)
                output_path = save_path

        elif version == 'v2':    
            default_speaker_key = list(speaker_ids[language].keys())[-1].lower()
            speaker_key = args.get('accent', default_speaker_key).lower()
            format_speaker_key = 'EN-Default' if speaker_key == 'en-default' else speaker_key.upper()
            final_speaker_key = speaker_key.replace('_', '-')
            
            if format_speaker_key not in speaker_ids[language]:
                joined_keys = ', '.join([key.lower() for key in speaker_ids[language].keys()])
                error_message = f"Invalid accent '{speaker_key}', valid values are: " + joined_keys
                app.logger.error(error_message)
                return jsonify(data={"message": error_message}), 400
            
            speaker_id = speaker_ids[language][format_speaker_key]
            speaker = args.get('speaker', SPEAKERS[0]).lower()

            if speaker not in reference_speakers and speaker != 'raw':
                error_message = f"Invalid speaker '{speaker}', valid values are: " + ", ".join(reference_speakers) + ", raw"
                app.logger.error(error_message)
                return jsonify(data={"message": error_message}), 400

            output_filename = generate_random_filename('', 'wav')
            output_path = f'{AUDIO_FILES_PATH}/{output_filename}' 
            app.logger.info(f' > Loading speaker v2 model for {final_speaker_key}...')
            source_se = torch.load(f'{OPENVOICE_PATH}/checkpoints_v2/base_speakers/ses/{final_speaker_key}.pth', map_location=DEVICE_V2)
            app.logger.info(f' > Converting text to audio...')
            models[language].tts_to_file(text, speaker_id, output_path, speed=speed)
            
            if speaker != 'raw':
                output_filename = generate_random_filename('', 'wav')
                save_path = f'{AUDIO_FILES_PATH}/{output_filename}'
                target_se = targets_v2[speaker]
                try:
                    app.logger.info(f'  > Saving final file in {save_path}')
                    tone_color_converter_v2.convert(
                        audio_src_path=output_path, 
                        src_se=source_se, 
                        tgt_se=target_se, 
                        output_path=save_path,
                        message=WATERMARK)
                    output_path = save_path
                    
                except Exception as e:
                    app.logger.error(f'Error: {str(e)}')
                    return jsonify(data={"message": "Internal Server Error"}), 500
        else:
            return jsonify(data={"message": f"Version {version} not supported"}), 500
        
        if response_format == 'url':
            protocol = request.scheme
            host = request.host
            output_url = f'{protocol}://{host}/audio-file/{output_filename}'
            return jsonify(data={"message": "Successfully converted text to audio", "url": output_url})
        elif response_format == 'bytes':
            with open(output_path, 'rb') as audio_file:
                audio_bytes = audio_file.read()
            return Response(audio_bytes, mimetype='audio/wav')
        elif response_format == 'stream':
            async def generate():
                with open(output_path, "rb") as fwav:
                    data = fwav.read(1024)
                    while data:
                        yield data
                        data = fwav.read(1024)                         
            return Response(generate(), mimetype='audio/wav')
        else:
            return jsonify(data={"message": f"Invalid response_format parameter: {raw_response_format}"}), 400
        
    except Exception as e:
        app.logger.error(f'Error: {str(e)}')
        app.logger.error(traceback.format_exc())
        return jsonify(data={"message": "Internal Server Error"}), 500
    
@app.route('/audio-file/<filename>', methods=['GET'])
async def serve_audio(filename):
    try:
        audio_file_path = os.path.join(AUDIO_FILES_PATH, filename)
        
        if not os.path.exists(audio_file_path):
            return jsonify(data={"message": "Audio file not found"}), 404
        
        stream_param = request.args.get('stream', 'false').lower()
        
        if stream_param == 'true':
            return await stream_audio(audio_file_path)
        else:
            return await send_file(audio_file_path, mimetype='audio/wav')
    
    except Exception as e:
        error_message = f"An error occurred while serving audio: {e}"
        app.logger.error(error_message)
        return jsonify(data={"message": "Internal Server Error"}), 500

async def stream_audio(file_path):
    """Stream audio file."""
    try:
        async def generate():
                with open(file_path, "rb") as fwav:
                    data = fwav.read(1024)
                    while data:
                        yield data
                        data = fwav.read(1024)                         
        return Response(generate(), mimetype='audio/wav')

    except FileNotFoundError:
        return jsonify(data={"message": "Audio file not found"}), 404
    except Exception as e:
        app.logger.error(f"An error occurred while streaming audio: {e}")
        return jsonify(data={"message": "Internal Server Error"}), 500

# Run the app
if __name__ == '__main__':
    app.run(host=SERVER_ADDRESS, port=SERVER_PORT, debug=True)
