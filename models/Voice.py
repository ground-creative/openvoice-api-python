import torch
from datetime import datetime

class Voice:

    @staticmethod
    def set_vars(logger, language_names, speaker_ids, openvoice_path, models, ckpt_base, base_speaker, watermark):
        
        Voice.logger = logger
        Voice.language_names = language_names
        Voice.speaker_ids = speaker_ids
        Voice.openvoice_path = openvoice_path
        Voice.models = models
        Voice.ckpt_base = ckpt_base
        Voice.base_speaker = base_speaker
        Voice.watermark = watermark

    @staticmethod
    async def tts_v1(args, output_file, device):

        speaker = args.get('voice').lower()
        style = args.get('style').lower()
        raw_lang = args['model']
        language = raw_lang.upper()
        text = args['input']
        speed = args['speed']
        Voice.logger.debug(f' > Loading speaker v1 model for {language}...')
        source_se = torch.load(f'{Voice.ckpt_base[language]}/{raw_lang}_default_se.pth').to(device)
        Voice.logger.debug(f' > Converting text to audio...')
        Voice.base_speaker[language].tts(text, output_file, speaker=style, language=Voice.language_names[language], speed=speed)
        return source_se
    
    @staticmethod
    async def tts_v2(args, output_file, device):
    
        raw_lang = args.get('model')
        language = raw_lang.upper()
        text = args.get('input')
        speed = args.get('speed')
        default_speaker_key = list(Voice.speaker_ids[language].keys())[-1].lower()
        speaker_key = args.get('accent', default_speaker_key).lower()
        
        if speaker_key == 'en-default':
            format_speaker_key = 'EN-Default' 
        elif speaker_key == 'en-newest':
            format_speaker_key = 'EN-Newest' 
        else:
            format_speaker_key = speaker_key.upper()
            
        final_speaker_key = speaker_key.replace('_', '-')
        speaker_id = Voice.speaker_ids[language][format_speaker_key]
        Voice.logger.debug(f' > Loading speaker v2 model for {final_speaker_key}...')
        source_se = torch.load(f'{Voice.openvoice_path}/checkpoints_v2/base_speakers/ses/{final_speaker_key}.pth', map_location=device)
        Voice.logger.debug(f' > Converting text to audio...')
        Voice.models[language].tts_to_file(text, speaker_id, output_file, speed=speed)
        return source_se

    #@staticmethod
    async def convert(src_file, output_file, src_se, tgt_se, converter):

        converter.convert(
            audio_src_path=src_file, 
            src_se=src_se, 
            tgt_se=tgt_se, 
            output_path=output_file,
            message=Voice.watermark
        )
        return True
    
    #@staticmethod
    async def build_source_se(args, version, device):

        if version == 'v1':
            raw_lang = args.get('model')
            language = raw_lang.upper()
            Voice.logger.debug(f' > Loading speaker v1 model for {language}...')
            return torch.load(f'{Voice.ckpt_base[language]}/{raw_lang}_default_se.pth').to(device)
        
        elif version == 'v2':
            raw_lang = args.get('model')
            language = raw_lang.upper()
            default_speaker_key = list(Voice.speaker_ids[language].keys())[-1].lower()
            speaker_key = args.get('accent', default_speaker_key).lower()
            final_speaker_key = speaker_key.replace('_', '-')
            Voice.logger.debug(f' > Loading speaker v2 model for {final_speaker_key}...')
            return torch.load(f'{Voice.openvoice_path}/checkpoints_v2/base_speakers/ses/{final_speaker_key}.pth', map_location= device)

    #@staticmethod
    def generate_random_filename(prefix='', ext='wav'):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")[:-3]
        random_filename = f"{prefix}{timestamp}.{ext}"
        return random_filename

