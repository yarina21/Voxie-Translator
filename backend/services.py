import os
import azure.cognitiveservices.speech as speechsdk
from dotenv import load_dotenv
from deep_translator import GoogleTranslator
from pydub import AudioSegment

base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
env_path = os.path.join(base_dir, ".env")
load_dotenv(dotenv_path=env_path)

AZURE_KEY = os.getenv("AZURE_SPEECH_KEY")
AZURE_REGION = os.getenv("AZURE_SPEECH_REGION")


if not AZURE_KEY:
    print("!!! EROARE: Nu s-a putut incarca AZURE_SPEECH_KEY !!!")
else:
    print(f"--- Voxie: Servicii Azure pregatite pe regiunea {AZURE_REGION} ---")

def transcribe_audio(audio_path: str):
    wav_path = audio_path + "_fix.wav"
    try:
       
        print(f"--- Incepe conversia pentru: {audio_path} ---")
        audio = AudioSegment.from_file(audio_path)
        audio.export(wav_path, format="wav", parameters=["-ac", "1", "-ar", "16000"])
        print(f"--- Conversie reusita: {wav_path} ---")

        speech_config = speechsdk.SpeechConfig(subscription=AZURE_KEY, region=AZURE_REGION)
        audio_config = speechsdk.audio.AudioConfig(filename=wav_path)
        
        auto_detect_config = speechsdk.languageconfig.AutoDetectSourceLanguageConfig(
            languages=["ro-RO", "en-US", "fr-FR", "es-ES"]
        )
        
        recognizer = speechsdk.SpeechRecognizer(
            speech_config=speech_config, 
            audio_config=audio_config,
            auto_detect_source_language_config=auto_detect_config
        )

        result = recognizer.recognize_once()

        if result.reason == speechsdk.ResultReason.RecognizedSpeech:
            detected_lang = result.properties[speechsdk.PropertyId.SpeechServiceConnection_AutoDetectSourceLanguageResult]
            return result.text, detected_lang
        else:
            return f"Azure nu a recunoscut textul: {result.reason}", "unknown"

    except Exception as e:
        print(f"!!! EROARE CRITICA: {str(e)} !!!")
        return f"Eroare procesare: {str(e)}", "error"
    finally:
        if os.path.exists(wav_path):
            os.remove(wav_path)

def translate_text(text: str, target_lang: str = "en"):
    """
    Traducere text folosind Google Translator (Sursă automată).
    """
    if not text or len(text) < 2 or "Eroare" in text:
        return ""
    try:
        return GoogleTranslator(source='auto', target=target_lang).translate(text)
    except Exception as e:
        return f"Eroare la traducere: {str(e)}"