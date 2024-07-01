# init.py
import os
from openvoice.api import ToneColorConverter, BaseSpeakerTTS
from melo.api import TTS
from openvoice import se_extractor

def initialize_globals(app, logger, OPENVOICE_PATH, DEVICE_V1, DEVICE_V2, AUDIO_FILES_PATH, WATERMARK, USE_VAD):
    MODEL_LANGUAGES_CODES_V1 = []
    MODEL_LANGUAGES_NAMES_V1 = {}
    reference_speakers = {}
    targets_v2 = {}
    targets_v1 = {}
    models = {}
    speaker_ids = {}
    ckpt_base = {}
    base_speaker_tts = {}
    tone_color_converter_v1 = ''
    tone_color_converter_v2 = ''
    STYLES_V1 = ['default', 'whispering', 'shouting', 'excited', 'cheerful', 'terrified', 'angry', 'sad', 'friendly']

    MODEL_LANGUAGES_V1 = os.getenv("MODEL_LANGUAGES_V1", "EN:English,ZH:Chinese").split(",")
    MODEL_LANGUAGES_V2 = os.getenv("MODEL_LANGUAGES_V2", "EN,ES,FR,ZH,JP").split(",")
    SPEAKERS_FOLDER = os.getenv("SPEAKERS_FOLDER", "speakers")
    SPEAKERS = os.getenv("SPEAKERS", "elon,rachel,kaiwen").split(",")
    BASE_DIRECTORY = os.path.dirname(os.path.abspath(__file__))

    if MODEL_LANGUAGES_V1 and any(MODEL_LANGUAGES_V1): 
        for item in MODEL_LANGUAGES_V1:
            code, name = item.split(":")
            MODEL_LANGUAGES_CODES_V1.append(code)
            MODEL_LANGUAGES_NAMES_V1[code] = name

    if (not MODEL_LANGUAGES_CODES_V1 or all(lang == '' for lang in MODEL_LANGUAGES_CODES_V1)) and (not MODEL_LANGUAGES_V2 or all(lang == '' for lang in MODEL_LANGUAGES_V2)):
        raise ValueError("Please specify at least one language model (version 1 or version 2) to use")

    SPEAKERS = [lang for lang in SPEAKERS if lang.strip()]

    if not SPEAKERS:
        raise ValueError("Please specify at least one speaker from the speakers folder")

    # Load version 1
    MODEL_LANGUAGES_CODES_V1 = [lang for lang in MODEL_LANGUAGES_CODES_V1 if lang.strip()]

    if MODEL_LANGUAGES_CODES_V1:
        logger.info(" > Loading v1 tone color converter.")
        ckpt_converter = f'{OPENVOICE_PATH}/checkpoints/converter'
        tone_color_converter_v1 = ToneColorConverter(f'{ckpt_converter}/config.json', device=DEVICE_V1)
        tone_color_converter_v1.load_ckpt(f'{ckpt_converter}/checkpoint.pth')
        logger.info(" > Loading v1 models: " + ", ".join(MODEL_LANGUAGES_CODES_V1))
        for lang in MODEL_LANGUAGES_CODES_V1:
            lang = lang.upper()
            ckpt_base[lang] = f'{OPENVOICE_PATH}/checkpoints/base_speakers/{lang}'
            base_speaker_tts[lang] = BaseSpeakerTTS(f"{ckpt_base[lang]}/config.json", device=DEVICE_V1)
            base_speaker_tts[lang].load_ckpt(f"{ckpt_base[lang]}/checkpoint.pth")

    # Load version 2
    MODEL_LANGUAGES_V2 = [lang for lang in MODEL_LANGUAGES_V2 if lang.strip()]

    if MODEL_LANGUAGES_V2:
        logger.info(" > Loading v2 tone color converter.")
        ckpt_converter_v2 = f'{OPENVOICE_PATH}/checkpoints_v2/converter'
        tone_color_converter_v2 = ToneColorConverter(f'{ckpt_converter_v2}/config.json', device=DEVICE_V2)
        tone_color_converter_v2.load_ckpt(f'{ckpt_converter_v2}/checkpoint.pth')
        logger.info(" > Loading v2 models: " + ", ".join(MODEL_LANGUAGES_V2))
        for lang in MODEL_LANGUAGES_V2:
            lang = lang.upper()
            models[lang] = TTS(language=lang, device=DEVICE_V2)
            speaker_ids[lang] = models[lang].hps.data.spk2id

    # Load speakers
    for speaker in SPEAKERS:
        reference_speakers[speaker] = f'{BASE_DIRECTORY}/{SPEAKERS_FOLDER}/{speaker}.mp3'
        
        if MODEL_LANGUAGES_CODES_V1:
            logger.info(f" > Loading SE extractors v1 for speaker {speaker}")
            targets_v1[speaker], audio_name = se_extractor.get_se(reference_speakers[speaker], tone_color_converter_v1, vad=USE_VAD)
        
        if MODEL_LANGUAGES_V2:
            logger.info(f" > Loading SE extractors v2 for speaker {speaker}")
            targets_v2[speaker], audio_name = se_extractor.get_se(reference_speakers[speaker], tone_color_converter_v2, vad=USE_VAD)

    return (MODEL_LANGUAGES_CODES_V1, MODEL_LANGUAGES_NAMES_V1, reference_speakers, targets_v2, targets_v1, models, speaker_ids, ckpt_base, base_speaker_tts, tone_color_converter_v1, tone_color_converter_v2, STYLES_V1)
