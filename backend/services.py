import os
import uuid
import requests
import json
import random
import re
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
        "es": "es-ES", "it": "it-IT", "pt": "pt-PT", "ja": "ja-JP",
        "ko": "ko-KR", "zh": "zh-CN", "ar": "ar-SA", "hi": "hi-IN",
        "tr": "tr-TR", "ru": "ru-RU", "uk": "uk-UA", "el": "el-GR"
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
        "pt": "pt-PT-RaquelNeural", "ja": "ja-JP-NanamiNeural", "ko": "ko-KR-SunHiNeural",
        "zh": "zh-CN-XiaoxiaoNeural", "ar": "ar-SA-ZariyahNeural", "hi": "hi-IN-SwaraNeural",
        "tr": "tr-TR-EmelNeural", "ru": "ru-RU-SvetlanaNeural", "uk": "uk-UA-PolinaNeural",
        "el": "el-GR-AthinaNeural"
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

def get_dictionary_info(word: str, lang: str):
    if len(word.split()) > 1:
        return None
        
    clean_word = "".join(c for c in word if c.isalpha() or c == "'").lower()
    
    if not clean_word: return None
    
    result = {}
    
    try:
        datamuse_url = f"https://api.datamuse.com/words?rel_syn={clean_word}&max=5"
        dm_res = requests.get(datamuse_url, timeout=3)
        
        if dm_res.status_code == 200:
            dm_data = dm_res.json()
            if dm_data:
                result["synonyms"] = [word["word"] for word in dm_data[:5]]
        
        fd_url = f"https://api.dictionaryapi.dev/api/v2/entries/en/{clean_word}"
        fd_res = requests.get(fd_url, timeout=3)
        
        if fd_res.status_code == 200:
            fd_data = fd_res.json()[0]
            
            if "phonetic" in fd_data and fd_data["phonetic"]:
                result["phonetic"] = fd_data["phonetic"]
            elif "phonetics" in fd_data and len(fd_data["phonetics"]) > 0:
                result["phonetic"] = fd_data["phonetics"][0].get("text", "")
            
            if "meanings" in fd_data and len(fd_data["meanings"]) > 0:
                meaning = fd_data["meanings"][0]
                result["partOfSpeech"] = meaning.get("partOfSpeech", "")
                
                if "synonyms" not in result and meaning.get("synonyms"):
                    result["synonyms"] = meaning.get("synonyms", [])[:5]
                
                if "definitions" in meaning and len(meaning["definitions"]) > 0:
                    result["definition"] = meaning["definitions"][0].get("definition", "")
        
        return result if result else None
        
    except Exception as e:
        print(f"DEBUG dict: EROARE - {e}")
    return None

def get_wiki_trivia(lang_name: str):
    try:
        page_title = f"Limba_{lang_name.lower()}"
        res = requests.get(f"https://ro.wikipedia.org/api/rest_v1/page/summary/{page_title}", timeout=3)
        if res.status_code == 200:
            extract = res.json().get("extract", "")
            if extract:
                # Divid textul în propoziții și aleg una random
                sentences = re.split(r'[.!]+', extract)
                sentences = [s.strip() for s in sentences if len(s.strip()) > 10]
                
                if sentences:
                    random_sentence = random.choice(sentences)
                    return random_sentence + '.'
                
                return extract.split('.')[0] + '.'
    except Exception as e:
        print(f"DEBUG trivia: EROARE - {e}")
    return "Știai că există peste 7.000 de limbi vorbite în prezent? 🌍"

# --- FUNCȚII PENTRU FAVORITE (PERSISTENȚĂ JSON) ---
FAVORITES_FILE = os.path.join(base_dir, "favorites.json")

def _ensure_favorites_file():
    if not os.path.exists(FAVORITES_FILE):
        with open(FAVORITES_FILE, "w", encoding="utf-8") as f:
            json.dump([], f)

def get_all_favorites():
    _ensure_favorites_file()
    try:
        with open(FAVORITES_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"Eroare la citirea favoritelor: {e}")
        return []

def save_favorite(fav_data: dict):
    favs = get_all_favorites()
    
    if not any(f.get("original") == fav_data.get("original") and f.get("translated") == fav_data.get("translated") for f in favs):
        favs.insert(0, fav_data) 
        with open(FAVORITES_FILE, "w", encoding="utf-8") as f:
            json.dump(favs, f, ensure_ascii=False, indent=2)
            
    return favs

def delete_favorite(fav_id: int):
    favs = get_all_favorites()
    favs = [f for f in favs if f.get("id") != fav_id]
    
    with open(FAVORITES_FILE, "w", encoding="utf-8") as f:
        json.dump(favs, f, ensure_ascii=False, indent=2)
        
    return favs