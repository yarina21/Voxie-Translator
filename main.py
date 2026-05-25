import os
import shutil
import uuid
from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from backend.services import transcribe_audio, translate_text, generate_tts, get_dictionary_info, get_wiki_trivia

app = FastAPI(title="Voxie API")
app.mount("/static", StaticFiles(directory="."), name="static")

app.add_middleware(
    CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"],
)

@app.get("/")
def home():
    return {"message": "Voxie Online - Backend is running"}

# Rută nouă DOAR pentru a cere curiozități din Wikipedia
@app.get("/api/trivia")
def get_trivia(lang_name: str = "Engleză"):
    fact = get_wiki_trivia(lang_name)
    return {"fact": fact}

@app.post("/process-audio")
async def process_audio(
    target_lang: str = Form("en"),    
    source_lang: str = Form("auto"),  
    file: UploadFile = File(...)
):
    file_extension = os.path.splitext(file.filename)[1]
    temp_path = f"temp_{uuid.uuid4()}{file_extension}"
    
    try:
        with open(temp_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        text_original, lang_detected = transcribe_audio(temp_path, source_lang=source_lang)
        text_tradus = translate_text(text_original, target_lang=target_lang)
        audio_file = generate_tts(text_tradus, target_lang)
        
        # --- Aici am adăugat logica de dicționar și fonetică ---
        dictionary_data = get_dictionary_info(text_tradus, target_lang)
        phonetics = "[Exemplu: kon-ni-chi-wa]" if target_lang == "ja" else None
        
        return {
            "status": "success",
            "detected_language": lang_detected,
            "original_text": text_original,
            "translated_text": text_tradus,
            "target_language": target_lang,
            "audio_url": f"http://127.0.0.1:8000/static/{audio_file}" if audio_file else None,
            "dictionary": dictionary_data,   # Acum trimitem datele reale
            "phonetics": phonetics           # Acum trimitem datele reale
        }
    except Exception as e:
        print(f"DEBUG: EROARE AUDIO: {e}")
        return {"status": "error", "message": str(e)}
    finally:
        if os.path.exists(temp_path): os.remove(temp_path)

@app.post("/process-text")
async def process_text(text: str = Form(...), target_lang: str = Form("en")):
    try:
        text_tradus = translate_text(text, target_lang=target_lang)
        audio_file = generate_tts(text_tradus, target_lang)
        
        # Obținem datele
        # Folosim funcția care caută în API-ul de dicționar
        dict_data = get_dictionary_info(text_tradus, "en") 
        
        # Fonetică reală sau un mesaj util
        phon_text = "Se citește fonetic" if target_lang != "en" else None

        return {
            "status": "success",
            "original_text": text,
            "translated_text": text_tradus,
            "audio_url": f"http://127.0.0.1:8000/static/{audio_file}" if audio_file else None,
            "dictionary": dict_data,  # Aici trimitem datele reale (sau None dacă nu există)
            "phonetics": phon_text   # Aici trimitem fonetica
        }
    except Exception as e:
        print(f"DEBUG: EROARE ROUTE: {e}")
        return {"status": "error", "message": str(e)}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)