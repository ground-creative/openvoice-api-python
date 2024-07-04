import logging, colorlog, os, traceback, base64
from quart import Quart, request, send_file, Response, redirect
from quart_cors import cors
from time import time
from dotenv import load_dotenv
from models.Response import Response as ApiResponse
from models.Request import Request as ApiRequest
from models.Voice import Voice
from init import initialize_globals

load_dotenv()

LOG_LEVEL = os.getenv("LOG_LEVEL", "DEBUG")
SERVER_ADDRESS = os.getenv("SERVER_ADDRESS", "0.0.0.0")
SERVER_PORT = os.getenv("SERVER_PORT", 5000)
AUDIO_FILES_PATH = os.getenv("AUDIO_FILES_PATH", "/tmp")
MODEL_LANGUAGES_V1 = os.getenv("MODEL_LANGUAGES_V1", "EN:English,ZH:Chinese").split(",")
MODEL_LANGUAGES_V2 = os.getenv("MODEL_LANGUAGES_V2", "EN,ES,FR,ZH,JP").split(",")
SPEAKERS_FOLDER = os.getenv("SPEAKERS_FOLDER", "speakers")
SPEAKERS = os.getenv("SPEAKERS", "elon,rachel,kaiwen").split(",")
WATERMARK = os.getenv("WATERMARK", "@OpenVoiceAPI")
DEVICE_V1 = os.getenv("DEVICE_V1", "cuda:0")
DEVICE_V2 = os.getenv("DEVICE_V2", "cuda:0")
SUPPORTED_STYLES_V1 = os.getenv("SUPPORTED_STYLES_V1", "English").split(",")
USE_VAD = os.getenv("USE_VAD", False)
OPENVOICE_PATH = "/app/OpenVoice"
BASE_DIRECTORY = os.path.dirname(os.path.abspath(__file__))

# Initialize Quart app
app = Quart(__name__)
app = cors(app, allow_origin="*")

# Configure colored logging
handler = colorlog.StreamHandler()
formatter = colorlog.ColoredFormatter(
    "%(log_color)s%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    log_colors={
        "DEBUG": "white",
        "INFO": "green",
        "WARNING": "yellow",
        "ERROR": "red",
        "CRITICAL": "bold_red",
    },
)
handler.setFormatter(formatter)
logger = colorlog.getLogger()
logger.addHandler(handler)
logger.setLevel(LOG_LEVEL)

# Call the initialize_globals function
globals_data = initialize_globals(
    app,
    logger,
    OPENVOICE_PATH,
    DEVICE_V1,
    DEVICE_V2,
    AUDIO_FILES_PATH,
    WATERMARK,
    USE_VAD,
)

# Unpack the returned globals
(
    MODEL_LANGUAGES_CODES_V1,
    MODEL_LANGUAGES_NAMES_V1,
    reference_speakers,
    targets_v2,
    targets_v1,
    models,
    speaker_ids,
    ckpt_base,
    base_speaker_tts,
    tone_color_converter_v1,
    tone_color_converter_v2,
    STYLES_V1,
) = globals_data

Voice.set_vars(
    logger,
    MODEL_LANGUAGES_NAMES_V1,
    speaker_ids,
    OPENVOICE_PATH,
    models,
    ckpt_base,
    base_speaker_tts,
    WATERMARK,
)
ApiRequest.set_vars(
    models,
    MODEL_LANGUAGES_CODES_V1,
    MODEL_LANGUAGES_V2,
    SPEAKERS,
    MODEL_LANGUAGES_NAMES_V1,
    STYLES_V1,
    SUPPORTED_STYLES_V1,
    speaker_ids,
    reference_speakers,
)


@app.before_request
def log_request_info():
    logger.debug(
        f"Started processing {request.method} request from {request.remote_addr} => {request.url}"
    )
    if request.path.endswith("/") and request.path != "/":
        return redirect(request.path[:-1], code=308)
    request.start_time = time()


@app.after_request
def add_header(response):
    if hasattr(request, "start_time"):
        elapsed_time = time() - request.start_time
        response.headers["X-Elapsed-Time"] = str(elapsed_time)
        response.headers["Access-Control-Expose-Headers"] = "X-Elapsed-Time"
    return response


@app.teardown_request
def log_teardown(exception=None):
    if exception:
        logger.error(f"Exception occurred: {exception}")
    logger.debug(
        f"Finished processing {request.method} request from {request.remote_addr} => {request.url}"
    )


@app.route("/")
async def home():
    payload_response = ApiResponse.payload(False, 200, "OpenVoice API")
    return await ApiResponse.output(payload_response, 200)


@app.route("/<version>/change-voice", methods=["POST"])
async def change_voice(version):

    args = dict(await request.get_json())
    validation_result = await ApiRequest.validate_change_voice_request(args)

    if validation_result:
        app.logger.debug(f" > Validator error: {validation_result}")
        return await ApiResponse.output(validation_result, validation_result["code"])

    try:
        audio_bytes = args.pop("audio_bytes")
        file_extension = args.pop("file_extension")
        output_filename = Voice.generate_random_filename("", file_extension)
        output_file = f"{AUDIO_FILES_PATH}/{output_filename}"
        with open(output_file, "wb") as audio_file:
            audio_file.write(audio_bytes)

    except Exception as e:
        app.logger.error(f" > Error: {str(e)}")

        if LOG_LEVEL == "DEBUG":
            app.logger.error(traceback.format_exc())

        payload_response = ApiResponse.payload(False, 500, "Internal Server Error")
        return await ApiResponse.output(payload_response, 500)

    return await generate_audio(version, args, output_file)


# OpenAI SDK adaptation
@app.route("/<version>/audio/speech", methods=["POST"])
async def generate_audio_openai(version):

    args = dict(await request.get_json())
    validation_result = await ApiRequest.validate_generate_audio_request(
        args, version, True
    )

    if validation_result:
        app.logger.debug(f" > Validator error: {validation_result}")
        return await ApiResponse.output(validation_result, validation_result["code"])

    args["response_format"] = "stream"
    return await generate_audio(version, args)


@app.route("/<version>/generate-audio", methods=["POST"])
async def generate_audio(version, args=None, source_file=None):

    if args is None:
        args = dict(await request.get_json())
    validation_result = await ApiRequest.validate_generate_audio_request(args, version)

    if validation_result:
        app.logger.debug(f" > Validator error: {validation_result}")
        return await ApiResponse.output(validation_result, validation_result["code"])

    try:

        if version == "v1":
            validation_result = await ApiRequest.validate_generate_audio_v1_params(args)

            if validation_result:
                app.logger.debug(f" > Validator error: {validation_result}")
                return await ApiResponse.output(
                    validation_result, validation_result["code"]
                )

            if source_file:
                source_se = await Voice.build_source_se(args, version, DEVICE_V1)
                prev_output_file = source_file
            else:
                output_filename = Voice.generate_random_filename("", "wav")
                output_file = f"{AUDIO_FILES_PATH}/{output_filename}"
                source_se = await Voice.tts_v1(args, output_file, DEVICE_V1)
                prev_output_file = output_file

            speaker = args.get("voice").lower()

            if speaker != "raw":
                app.logger.debug(f" > Running v1 color converter...")
                output_filename = Voice.generate_random_filename("", "wav")
                output_file = f"{AUDIO_FILES_PATH}/{output_filename}"
                await Voice.convert(
                    src_file=prev_output_file,
                    output_file=output_file,
                    src_se=source_se,
                    tgt_se=targets_v1[speaker],
                    converter=tone_color_converter_v1,
                )

        elif version == "v2":
            validation_result = await ApiRequest.validate_generate_audio_v2_params(args)

            if validation_result:
                app.logger.debug(f" > Validator error: {validation_result}")
                return await ApiResponse.output(
                    validation_result, validation_result["code"]
                )

            if source_file:
                source_se = await Voice.build_source_se(args, version, DEVICE_V2)
                prev_output_file = source_file
            else:
                output_filename = Voice.generate_random_filename("", "wav")
                output_file = f"{AUDIO_FILES_PATH}/{output_filename}"
                source_se = await Voice.tts_v2(args, output_file, DEVICE_V2)
                prev_output_file = output_file

            speaker = args.get("voice").lower()

            if speaker != "raw":
                app.logger.debug(f" > Running v2 color converter...")
                output_filename = Voice.generate_random_filename("", "wav")
                output_file = f"{AUDIO_FILES_PATH}/{output_filename}"
                await Voice.convert(
                    src_file=prev_output_file,
                    output_file=output_file,
                    src_se=source_se,
                    tgt_se=targets_v2[speaker],
                    converter=tone_color_converter_v2,
                )
        else:
            error_message = f" > Version {version} not supported"
            app.logger.error(error_message)
            payload_response = ApiResponse.payload(False, 400, error_message)
            return await ApiResponse.output(payload_response, 400)

        raw_response_format = args.get("response_format")
        response_format = raw_response_format.lower()

        if response_format == "url":
            protocol = request.scheme
            host = request.host
            output_url = f"{protocol}://{host}/audio-file/{output_filename}"
            payload_response = ApiResponse.payload(
                True, 200, "Successfully converted text to audio", {"url": output_url}
            )
            return await ApiResponse.output(payload_response, 200)

        elif response_format == "bytes":
            output_path = f"{AUDIO_FILES_PATH}/{output_filename}"
            with open(output_path, "rb") as audio_file:
                audio_bytes = audio_file.read()
            return Response(audio_bytes, mimetype="audio/wav")

        elif response_format == "base64":
            output_path = f"{AUDIO_FILES_PATH}/{output_filename}"
            with open(output_path, "rb") as audio_file:
                audio_bytes = audio_file.read()
            audio_base64 = base64.b64encode(audio_bytes).decode("utf-8")
            payload_response = ApiResponse.payload(
                True,
                200,
                "Successfully generated base64 audio",
                {"audio_data": audio_base64},
            )
            return await ApiResponse.output(payload_response, 200)

        elif response_format == "stream":
            output_path = f"{AUDIO_FILES_PATH}/{output_filename}"

            async def generate():
                with open(output_path, "rb") as fwav:
                    data = fwav.read(1024)
                    while data:
                        yield data
                        data = fwav.read(1024)

            return Response(generate(), mimetype="audio/wav")

        else:
            payload_response = ApiResponse.payload(
                False, 400, f"Invalid response_format parameter: {raw_response_format}"
            )
            return await ApiResponse.output(payload_response, 400)

    except Exception as e:
        app.logger.error(f" > Error: {str(e)}")

        if LOG_LEVEL == "DEBUG":
            app.logger.error(traceback.format_exc())

        payload_response = ApiResponse.payload(False, 500, "Internal Server Error")
        return await ApiResponse.output(payload_response, 500)


@app.route("/audio-file/<filename>", methods=["GET"])
async def serve_audio(filename):

    try:
        audio_file_path = os.path.join(AUDIO_FILES_PATH, filename)

        if not os.path.exists(audio_file_path):
            payload_response = ApiResponse.payload(False, 404, "Audio file not found")
            return await ApiResponse.output(payload_response, 404)

        stream_param = request.args.get("stream", False)

        if stream_param == True:
            return await stream_audio(audio_file_path)

        else:
            return await send_file(audio_file_path, mimetype="audio/wav")

    except Exception as e:
        error_message = f" > An error occurred while serving audio: {e}"
        app.logger.error(error_message)
        payload_response = ApiResponse.payload(False, 500, "Internal Server Error")
        return await ApiResponse.output(payload_response, 500)


async def stream_audio(file_path):

    try:

        async def generate():
            with open(file_path, "rb") as fwav:
                data = fwav.read(1024)
                while data:
                    yield data
                    data = fwav.read(1024)

        return Response(generate(), mimetype="audio/wav")

    except FileNotFoundError:
        payload_response = ApiResponse.payload(False, 404, "Audio file not found")
        return await ApiResponse.output(payload_response, 404)

    except Exception as e:
        app.logger.error(f" > An error occurred while streaming audio: {e}")
        payload_response = ApiResponse.payload(False, 500, "Internal Server Error")
        return await ApiResponse.output(payload_response, 500)


# Handle 404 errors
@app.errorhandler(404)
async def page_not_found(error):

    msg = f" > No service is associated with the url => {request.method}:{request.url}"
    app.logger.error(msg)
    payload_response = ApiResponse.not_found(msg, {})
    return await ApiResponse.output(payload_response, 404)


# Run the app
if __name__ == "__main__":
    app.run(host=SERVER_ADDRESS, port=SERVER_PORT, debug=True)
