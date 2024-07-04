import magic, base64
from models.Response import Response
    
class Request:

    @staticmethod
    def set_vars(models, model_languages_v1, model_languages_v2, speakers, model_language_names_v1, styles_v1, supported_styles_v1, speaker_ids, reference_speakers):

        Request.models = models
        Request.model_languages_v1 = model_languages_v1
        Request.model_languages_v2 = model_languages_v2
        Request.speakers = speakers
        Request.model_language_names_v1 = model_language_names_v1
        Request.styles_v1 = styles_v1
        Request.supported_styles_v1 = supported_styles_v1
        Request.speaker_ids = speaker_ids
        Request.reference_speakers = reference_speakers
        Request.openvoice_versions = ['v1', 'v2']
        Request.valid_generate_audio_params = ['model', 'speed', 'input', 'response_format', 'voice']
        Request.valid_change_voice_mime_types = {'mp3': 'audio/mpeg', 'wav': 'audio/wav'}
        Request.valid_response_formats = ['url', 'bytes', 'stream', 'base64']

    @staticmethod
    async def validate_change_voice_request(args):

        args.setdefault('audio_data', None)
        audio_data = args.pop('audio_data')
        
        if audio_data is None or audio_data == '':
            error_message = "Parameter 'audio_data' is required"
            payload_response = Response.payload(False, 400, error_message)
            return payload_response
        
        try:
            audio_bytes = base64.b64decode(audio_data)
            mime = magic.Magic(mime=True)
            mime_type = mime.from_buffer(audio_bytes)
        except Exception as e:
            payload_response = Response.payload(False, 400, "Invalid base64 audio data")
            return payload_response
        
        if (mime_type == 'audio/x-wav'):
            mime_type = 'audio/wav'
        
        file_extension = None
        for ext, mime_val in Request.valid_change_voice_mime_types.items():
            
            if mime_type == mime_val:
                file_extension = ext
                break

        if file_extension is None:
            error_message = f"Unsupported audio file type: {mime_type}, valid extensions are: {', '.join(Request.valid_change_voice_mime_types.keys())}"
            payload_response = Response.payload(False, 400, error_message, {})
            return payload_response
        
        text = args.get('input', None)

        if text is not None and text != '__AUDIO_DATA__':
            error_message = "Invalid paramerter(s) 'input'"
            payload_response = Response.payload(False, 400, error_message)
            return payload_response
        
        args.setdefault('voice', 'raw')
        speaker = args.get('voice').lower()

        if speaker == 'raw':
            error_message = f"Parameter 'voice' cannot be used with raw value for change voice service."
            payload_response = Response.payload(False, 400, error_message)
            return payload_response
        
        style = args.get('style', None)

        if style is not None:
            error_message = "Parameter 'style' not supported for change voice service"
            payload_response = Response.payload(False, 400, error_message)
            return payload_response
        
        #accent = args.get('accent', None)

        #if accent is not None:
        #    error_message = "Parameter 'accent' not supported for change voice service"
        #    payload_response = Response.payload(False, 400, error_message)
        #    return payload_response

        speed = args.get('speed', None)

        if speed is not None:
            error_message = "Parameter 'speed' not supported for change voice service"
            payload_response = Response.payload(False, 400, error_message)
            return payload_response
        
        args['audio_bytes'] = audio_bytes
        args['file_extension'] = file_extension
        args.setdefault('input', '__AUDIO_DATA__')

        return {}

    @staticmethod
    async def validate_generate_audio_request(args, version, isOpenAI=False):

        args.setdefault('response_format', 'url')
        args.setdefault('speed', 1.0)

        valid_generate_audio_params = Request.valid_generate_audio_params.copy()

        if version not in Request.openvoice_versions:
            payload_response = Response.payload(False, 400, "Invalid version", {})
            return payload_response

        if version == 'v1':

            if not Request.model_languages_v1:
                payload_response = Response.payload(False, 500, 'version 1 module is not loaded')
                return payload_response
            
            valid_generate_audio_params.append('style')
            
        elif version == 'v2':

            if not Request.model_languages_v2:
                payload_response = Response.payload(False, 500, 'version 2 module is not loaded')
                return payload_response
        
            valid_generate_audio_params.append('accent')

        invalid_params = [param for param in args if param not in valid_generate_audio_params]
                
        if invalid_params:
            error_message = f"Invalid parameter(s) sent: {', '.join(invalid_params)}. valid params are: {', '.join(valid_generate_audio_params)}"
            payload_response = Response.payload(False, 400, error_message)
            return payload_response

        language = args.get('model', None)

        if language is None or language == '':
            error_message = "Parameter 'model' is required"
            payload_response = Response.payload(False, 400, error_message)
            return payload_response
        
        raw_response_format = args.get('response_format')
        response_format = raw_response_format.lower()
        valid_response_formats = Request.valid_response_formats if not isOpenAI else ['wav']
        
        if response_format not in valid_response_formats:
            error_message = f"Invalid response_format sent '{raw_response_format}', valid params are: {', '.join(valid_response_formats)}"
            payload_response = Response.payload(False, 400, error_message)
            return payload_response

        raw_lang = args.get('model')
        language = raw_lang.upper()

        if (version == 'v1' and language not in Request.model_languages_v1) or (version == 'v2' and language not in Request.models):

            if version == 'v1':
                valid_lang_keys = ", ".join(Request.model_languages_v1).lower()
            elif version == 'v2':
                valid_lang_keys = ", ".join(Request.model_languages_v2).lower()
            else:
                payload_response = Response.payload(False, 500, f"Version {version} not supported")
                return payload_response
            
            error_message = f"Invalid model '{raw_lang}', valid values are: " + valid_lang_keys
            payload_response = Response.payload(False, 400, error_message)
            return payload_response
        
        text = args.get('input', None)

        if (text != '__AUDIO_DATA__'):

            if text is None or text == '':
                error_message = "Parameter 'input' is required"
                payload_response = Response.payload(False, 400, error_message)
                return payload_response
        
        speed = args.get('speed')
        
        try:
            speed = float(speed)
        except ValueError:
            error_message = "Parameter 'speed' must be a number"
            payload_response = Response.payload(False, 400, error_message)
            return payload_response
        
        return {}
    
    @staticmethod
    async def validate_generate_audio_v1_params(args):

        #args.setdefault('voice', SPEAKERS[0])
        args.setdefault('voice', 'raw')
        args.setdefault('style', 'default')
        speaker = args.get('voice').lower()

        if speaker not in Request.speakers and speaker != 'raw':
            joined_keys = ' '.join(Request.speakers) + ", raw"
            error_message = f"Invalid voice '{speaker}', valid values are: " + joined_keys
            payload_response = Response.payload(False, 400, error_message)
            return payload_response
        
        text = args.get('input')
                    
        if speaker == 'raw' and text == '__AUDIO__DATA__':
            error_message = "Parameter 'voice' cannot be 'raw' when converting from audio."
            payload_response = Response.payload(False, 400, error_message)
            return payload_response

        style = args.get('style').lower()
        raw_lang = args.get('model')
        language = raw_lang.upper()

        if style != 'default' and Request.model_language_names_v1[language] not in Request.supported_styles_v1:
            joined_keys = ' '.join(Request.styles_v1)
            error_message = f"Param 'style' is not supported for language '{raw_lang}'"
            payload_response = Response.payload(False, 400, error_message)
            return payload_response
        
        if style not in Request.styles_v1:
            joined_keys = ' '.join(Request.styles_v1)
            error_message = f"Invalid style '{style}', valid values are: " + joined_keys
            payload_response = Response.payload(False, 400, error_message)
            return payload_response

        return {}
    
    @staticmethod
    async def validate_generate_audio_v2_params(args):

        #args.setdefault('voice', SPEAKERS[0])
        args.setdefault('voice', 'raw')
        raw_lang = args.get('model')
        language = raw_lang.upper()
        default_speaker_key = list( Request.speaker_ids[language].keys())[-1].lower()
        speaker_key = args.get('accent', default_speaker_key).lower()
        
        if speaker_key == 'en-default':
            format_speaker_key = 'EN-Default' 
        elif speaker_key == 'en-newest':
            format_speaker_key = 'EN-Newest' 
        else:
            format_speaker_key = speaker_key.upper()
        
        if format_speaker_key not in  Request.speaker_ids[language]:
            joined_keys = ', '.join([key.lower() for key in  Request.speaker_ids[language].keys()])
            error_message = f"Invalid accent '{speaker_key}', valid values are: " + joined_keys
            payload_response = Response.payload(False, 400, error_message)
            return payload_response
        
        speaker = args.get('voice').lower()

        if speaker not in Request.reference_speakers and speaker != 'raw':
            error_message = f"Invalid voice '{speaker}', valid values are: " + ", ".join(Request.reference_speakers) + ", raw"
            payload_response = Response.payload(False, 400, error_message)
            return payload_response
        
        text = args.get('input')
                    
        if speaker == 'raw' and text == '__AUDIO__DATA__':
            error_message = "Parameter 'voice' cannot be 'raw' when converting from audio."
            payload_response = Response.payload(False, 400, error_message)
            return payload_response

        return {}