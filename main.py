import os
import shutil
import uuid
from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from backend.services import (
    transcribe_audio, translate_text, generate_tts, 
    get_dictionary_info, get_wiki_trivia, 
    get_all_favorites, save_favorite, delete_favorite
)

app = FastAPI(title="Voxie API")
app.mount("/static", StaticFiles(directory="."), name="static")

app.add_middleware(
    CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"],
)

# Structura pentru elementele favorite
class FavoriteItem(BaseModel):
    id: int
    original: str  # Asigură-te că este str (string)
    translated: str
    from_lang: str
    to_lang: str
    timestamp: str

@app.get("/")
def home():
    return {"message": "Voxie Online - Backend is running"}

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
        
        dict_data = get_dictionary_info(text_tradus, target_lang)
        phonetics = dict_data.get("phonetic") if dict_data else None
        
        return {
            "status": "success",
            "detected_language": lang_detected,
            "original_text": text_original,
            "translated_text": text_tradus,
            "target_language": target_lang,
            "audio_url": f"http://127.0.0.1:8000/static/{audio_file}" if audio_file else None,
            "dictionary": dict_data,
            "phonetics": phonetics
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
        
        dict_data = get_dictionary_info(text_tradus, target_lang)
        phonetics = dict_data.get("phonetic") if dict_data else None

        return {
            "status": "success",
            "original_text": text,
            "translated_text": text_tradus,
            "audio_url": f"http://127.0.0.1:8000/static/{audio_file}" if audio_file else None,
            "dictionary": dict_data,
            "phonetics": phonetics
        }
    except Exception as e:
        print(f"DEBUG: EROARE ROUTE: {e}")
        return {"status": "error", "message": str(e)}

# --- RUTE PENTRU FAVORITE ---

@app.get("/api/favorites")
def fetch_favorites():
    return {"favorites": get_all_favorites()}

@app.post("/api/favorites")
def add_favorite(fav: FavoriteItem):
    updated_favs = save_favorite(fav.dict())
    return {"status": "success", "favorites": updated_favs}

@app.delete("/api/favorites/{fav_id}")
def remove_favorite(fav_id: int):
    updated_favs = delete_favorite(fav_id)
    return {"status": "success", "favorites": updated_favs}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)