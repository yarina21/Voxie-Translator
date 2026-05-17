import os
import uuid
import azure.cognitiveservices.speech as speechsdk
from dotenv import load_dotenv
from deep_translator import GoogleTranslator
from pydub import AudioSegment


# Setup căi și încărcare variabile de mediu
base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
env_path = os.path.join(base_dir, ".env")
load_dotenv(dotenv_path=env_path)

AZURE_KEY = os.getenv("AZURE_SPEECH_KEY")
AZURE_REGION = os.getenv("AZURE_SPEECH_REGION")

if not AZURE_KEY:
    print("!!! EROARE: Nu s-a putut incarca AZURE_SPEECH_KEY. Verifica fisierul .env !!!")
else:
    print(f"--- Voxie: Servicii Azure pregatite pe regiunea {AZURE_REGION} ---")

def transcribe_audio(audio_path: str, source_lang: str = None):
    """
    Transcrie audio folosind Azure Speech-to-Text.
    Daca source_lang este None, foloseste Auto-Detect (limitat la 4 limbi).
    Daca source_lang este specificat (ex: 'it-IT'), foloseste limba respectiva direct.
    """
    wav_path = audio_path + "_fix.wav"
    try:
        # 1. Preprocesare Audio cu Pydub
        print(f"--- Incepe conversia pentru: {audio_path} ---")
        audio = AudioSegment.from_file(audio_path)
        # Export obligatoriu la 16kHz, Mono, WAV pentru acuratețe maximă
        audio.export(wav_path, format="wav", parameters=["-ac", "1", "-ar", "16000"])
        print(f"--- Conversie reusita: {wav_path} ---")

        # 2. Configurare Azure Speech
        speech_config = speechsdk.SpeechConfig(subscription=AZURE_KEY, region=AZURE_REGION)
        audio_config = speechsdk.audio.AudioConfig(filename=wav_path)
        
        # LOGICA HIBRIDĂ: Auto-Detect vs Manual
        if source_lang and source_lang != "auto":
            # Modul Manual: Suportă orice limbă (ex: 'ja-JP', 'it-IT', 'ru-RU')
            speech_config.speech_recognition_language = source_lang
            recognizer = speechsdk.SpeechRecognizer(
                speech_config=speech_config, 
                audio_config=audio_config
            )
            print(f"--- Mod: Recunoastere fixa ({source_lang}) ---")
        else:
            # Modul Auto: Detectează automat între cele 4 limbi de bază
            # Aceasta configuratie evita eroarea 1007
            auto_detect_config = speechsdk.languageconfig.AutoDetectSourceLanguageConfig(
                languages=["ro-RO", "en-US", "fr-FR", "de-DE"]
            )
            recognizer = speechsdk.SpeechRecognizer(
                speech_config=speech_config, 
                audio_config=audio_config,
                auto_detect_source_language_config=auto_detect_config
            )
            print("--- Mod: Auto-Detect (RO, EN, FR, DE) ---")

        # 3. Execuție Recunoaștere
        result = recognizer.recognize_once()

        # 4. Procesare Rezultat
        if result.reason == speechsdk.ResultReason.RecognizedSpeech:
            # Extrage limba detectată (dacă s-a folosit auto-detect)
            if not source_lang or source_lang == "auto":
                detected_lang = result.properties[speechsdk.PropertyId.SpeechServiceConnection_AutoDetectSourceLanguageResult]
            else:
                detected_lang = source_lang
            
            print(f"--- Succes: [{detected_lang}] {result.text} ---")
            return result.text, detected_lang

        elif result.reason == speechsdk.ResultReason.NoMatch:
            return "Nu s-a detectat voce clara.", "none"

        elif result.reason == speechsdk.ResultReason.Canceled:
            details = result.cancellation_details
            print(f"!!! Azure Error: {details.reason} | {details.error_details} !!!")
            return f"Eroare Azure: {details.reason}", "error"

    except Exception as e:
        print(f"!!! EROARE CRITICA: {str(e)} !!!")
        return f"Eroare procesare: {str(e)}", "error"
        
    finally:
        # Șterge fișierul convertit pentru a elibera spațiul
        if os.path.exists(wav_path):
            os.remove(wav_path)

def translate_text(text: str, target_lang: str = "en"):
    """
    Traduce textul folosind Google Translator (NMT).
    """
    # Verificăm dacă textul este valid înainte de a trimite la Google
    if not text or len(text) < 2 or "Eroare" in text or "Azure Error" in text:
        return ""
    
    try:
        # 'auto' aici se referă la detectarea limbii textului sursă de către Google
        translation = GoogleTranslator(source='auto', target=target_lang).translate(text)
        return translation
    except Exception as e:
        print(f"!!! Eroare Google Translate: {str(e)} !!!")
        return f"Eroare la traducere: {str(e)}"
    
def generate_tts(text: str, lang_code: str):
    """
    Transformă textul tradus în audio (MP3) folosind Azure TTS.
    """
    # Mapare coduri scurte Google către coduri complete Azure TTS
    voices = {
        # EUROPA
    "ro": "ro-RO-AlinaNeural",      # Romana
    "en": "en-US-JennyNeural",      # Engleza (US)
    "en-GB": "en-GB-SoniaNeural",   # Engleza (UK)
    "it": "it-IT-ElsaNeural",       # Italiana
    "fr": "fr-FR-DeniseNeural",     # Franceza
    "de": "de-DE-KatjaNeural",      # Germana
    "es": "es-ES-ElviraNeural",     # Spaniola
    "pt": "pt-PT-RaquelNeural",     # Portugheza
    
    # ASIA & ORIENT
    "ja": "ja-JP-NanamiNeural",     # Japoneza
    "ko": "ko-KR-SunHiNeural",      # Coreeana
    "zh": "zh-CN-XiaoxiaoNeural",   # Chineza (Mandarina)
    "ar": "ar-SA-ZariyahNeural",    # Araba
    "hi": "hi-IN-SwaraNeural",      # Hindi
    "tr": "tr-TR-EmelNeural",       # Turca
    
    # ALTELE
    "ru": "ru-RU-SvetlanaNeural",   # Rusa
    "uk": "uk-UA-PolinaNeural",     # Ucraineana
    "el": "el-GR-AthinaNeural"      # Greaca
    }
    
    # Luăm vocea corespunzătoare sau fallback pe Engleză
    voice_name = voices.get(lang_code.split('-')[0], "en-US-JennyNeural")
    
    # Numele fișierului audio de ieșire
    output_filename = f"tts_{uuid.uuid4()}.mp3"
    output_path = os.path.join(os.getcwd(), output_filename)

    speech_config = speechsdk.SpeechConfig(subscription=AZURE_KEY, region=AZURE_REGION)
    speech_config.speech_synthesis_voice_name = voice_name
    
    # Configurăm ieșirea către un fișier
    audio_config = speechsdk.audio.AudioOutputConfig(filename=output_path)
    synthesizer = speechsdk.SpeechSynthesizer(speech_config=speech_config, audio_config=audio_config)

    result = synthesizer.speak_text_async(text).get()

    if result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
        return output_filename
    else:
        return None