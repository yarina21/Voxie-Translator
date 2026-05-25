import os
import uuid
import requests
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
    print("!!! EROARE: Nu s-a putut incarca AZURE_SPEECH_KEY. Verifica fisierul .env !!!")
else:
    print(f"--- Voxie: Servicii Azure pregatite pe regiunea {AZURE_REGION} ---")

def transcribe_audio(audio_path: str, source_lang: str = None):
    wav_path = audio_path + "_fix.wav"
    azure_locales = {
        "ro": "ro-RO", "en": "en-US", "fr": "fr-FR", "de": "de-DE",
        "es": "es-ES", "it": "it-IT", "ja": "ja-JP", "zh": "zh-CN",
        "ar": "ar-SA", "ru": "ru-RU"
    }
    
    try:
        audio = AudioSegment.from_file(audio_path)
        audio.export(wav_path, format="wav", parameters=["-ac", "1", "-ar", "16000"])

        speech_config = speechsdk.SpeechConfig(subscription=AZURE_KEY, region=AZURE_REGION)
        audio_config = speechsdk.audio.AudioConfig(filename=wav_path)
        
        if source_lang and source_lang != "auto":
            mapped_lang = azure_locales.get(source_lang, "en-US")
            speech_config.speech_recognition_language = mapped_lang
            recognizer = speechsdk.SpeechRecognizer(speech_config=speech_config, audio_config=audio_config)
        else:
            auto_detect_config = speechsdk.languageconfig.AutoDetectSourceLanguageConfig(
                languages=["ro-RO", "en-US", "fr-FR", "de-DE"]
            )
            recognizer = speechsdk.SpeechRecognizer(
                speech_config=speech_config, audio_config=audio_config, auto_detect_source_language_config=auto_detect_config
            )

        result = recognizer.recognize_once()

        if result.reason == speechsdk.ResultReason.RecognizedSpeech:
            if not source_lang or source_lang == "auto":
                detected_lang_full = result.properties[speechsdk.PropertyId.SpeechServiceConnection_AutoDetectSourceLanguageResult]
                detected_lang = detected_lang_full.split('-')[0] if detected_lang_full else "auto"
            else:
                detected_lang = source_lang
            return result.text, detected_lang

        return "Nu s-a detectat voce clara.", "none"
    except Exception as e:
        return f"Eroare procesare: {str(e)}", "error"
    finally:
        if os.path.exists(wav_path):
            try: os.remove(wav_path)
            except: pass

def translate_text(text: str, target_lang: str = "en"):
    if not text or len(text) < 2 or "Eroare" in text: return ""
    try:
        return GoogleTranslator(source='auto', target=target_lang).translate(text)
    except Exception as e:
        return f"Eroare la traducere: {str(e)}"
    
def generate_tts(text: str, lang_code: str):
    if not text: return None
    voices = {
        "ro": "ro-RO-AlinaNeural", "en": "en-US-JennyNeural", "it": "it-IT-ElsaNeural",       
        "fr": "fr-FR-DeniseNeural", "de": "de-DE-KatjaNeural", "es": "es-ES-ElviraNeural",     
        "ja": "ja-JP-NanamiNeural", "zh": "zh-CN-XiaoxiaoNeural", "ar": "ar-SA-ZariyahNeural",    
        "ru": "ru-RU-SvetlanaNeural"      
    }
    prefix = lang_code.split('-')[0]
    voice_name = voices.get(prefix, "en-US-JennyNeural")
    output_filename = f"tts_{uuid.uuid4()}.mp3"
    output_path = os.path.join(os.getcwd(), output_filename)

    try:
        speech_config = speechsdk.SpeechConfig(subscription=AZURE_KEY, region=AZURE_REGION)
        speech_config.speech_synthesis_voice_name = voice_name
        audio_config = speechsdk.audio.AudioOutputConfig(filename=output_path)
        synthesizer = speechsdk.SpeechSynthesizer(speech_config=speech_config, audio_config=audio_config)
        result = synthesizer.speak_text_async(text).get()
        if result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted: return output_filename
        return None
    except:
        return None

# --- FUNCȚII NOI (MUTATE DIN FRONTEND) ---

def get_dictionary_info(word: str, lang: str):
    print(f"DEBUG dict: word='{word}', lang='{lang}'")  # <-- adaugă asta
    
    if lang != "en" or len(word.split()) > 1:
        print(f"DEBUG dict: skipped - lang={lang}, words={len(word.split())}")
        return None
        
    clean_word = "".join(c for c in word if c.isalpha() or c == "'").lower()
    print(f"DEBUG dict: clean_word='{clean_word}'")  # <-- și asta
    
    if not clean_word: return None
    
    try:
        res = requests.get(f"https://api.dictionaryapi.dev/api/v2/entries/en/{clean_word}", timeout=3)
        print(f"DEBUG dict: status={res.status_code}")  # <-- și asta
        if res.status_code == 200:
            data = res.json()[0]
            if "meanings" in data and len(data["meanings"]) > 0:
                meaning = data["meanings"][0]
                return {
                    "partOfSpeech": meaning.get("partOfSpeech", ""),
                    "synonyms": meaning.get("synonyms", [])[:3]
                }
    except Exception as e:
        print(f"DEBUG dict: EROARE - {e}")  # <-- și asta
    return None

def get_wiki_trivia(lang_name: str):
    """Extrage curiozități direct din Wikipedia pe backend."""
    try:
        page_title = f"Limba_{lang_name.lower()}"
        res = requests.get(f"https://ro.wikipedia.org/api/rest_v1/page/summary/{page_title}", timeout=3)
        if res.status_code == 200:
            extract = res.json().get("extract", "")
            if extract:
                return extract.split('.')[0] + '.'
    except:
        pass
    return "Știai că există peste 7.000 de limbi vorbite în prezent? 🌍"