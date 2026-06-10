import os
import shutil
import uuid
import time  # Importat pentru marcajele temporale diferențiale (T1, T2, T3, T4)
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
    original: str  
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
    print("\n========= START EVALUARE FLUX MULTIMEDIA (AUDIO) =========")
    
    # --- MĂSURARE T1: Salvare buffer și Transcodare/Normalizare implicită ---
    start_t1 = time.time()
    
    file_extension = os.path.splitext(file.filename)[1]
    temp_path = f"temp_{uuid.uuid4()}{file_extension}"
    
    try:
        with open(temp_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        end_t1 = time.time()
        t1_duration = end_t1 - start_t1
        print(f"[PERFORMANȚĂ] T1 (Salvare binar și Preprocesare): {t1_duration:.4f} secunde")
        
        # --- MĂSURARE T2: Recunoaștere vocală Azure STT (cu auto-detectare limbă) ---
        start_t2 = time.time()
        text_original, lang_detected = transcribe_audio(temp_path, source_lang=source_lang)
        end_t2 = time.time()
        t2_duration = end_t2 - start_t2
        print(f"[PERFORMANȚĂ] T2 (Azure Speech-to-Text): {t2_duration:.4f} secunde")
        
        # --- MĂSURARE T3: Traducere Neuronală Google Cloud AI ---
        start_t3 = time.time()
        text_tradus = translate_text(text_original, target_lang=target_lang)
        end_t3 = time.time()
        t3_duration = end_t3 - start_t3
        print(f"[PERFORMANȚĂ] T3 (Google NMT): {t3_duration:.4f} secunde")
        
        # --- MĂSURARE T4: Sinteză vocală Azure TTS și Analiză Lingvistică ---
        start_t4 = time.time()
        audio_file = generate_tts(text_tradus, target_lang)
        
        # Interogarea asincronă / paralelă a modulelor de dicționar
        dict_data = get_dictionary_info(text_tradus, target_lang)
        phonetics = dict_data.get("phonetic") if dict_data else None
        
        end_t4 = time.time()
        t4_duration = end_t4 - start_t4
        print(f"[PERFORMANȚĂ] T4 (Azure Text-to-Speech & Dicționar): {t4_duration:.4f} secunde")
        
        # Calculul latenței totale introduse strict de infrastructura serverului
        total_server_time = t1_duration + t2_duration + t3_duration + t4_duration
        print(f"[PERFORMANȚĂ] LATENȚĂ TOTALĂ SERVER BACKEND: {total_server_time:.4f} secunde")
        print("========= FINAL EVALUARE FLUX MULTIMEDIA (AUDIO) =========\n")
        
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
        if os.path.exists(temp_path): 
            os.remove(temp_path)

@app.post("/process-text")
async def process_text(text: str = Form(...), target_lang: str = Form("en")):
    print("\n========= START EVALUARE SCENARIU MANUAL (TEXT) =========")
    
    # În acest scenariu manual, T1 și T2 sunt 0 deoarece ocolim microfonul și transcrierea
    print("[PERFORMANȚĂ] T1 (Salvare/Preprocesare) = Ocolit (0.0000s)")
    print("[PERFORMANȚĂ] T2 (Azure Speech-to-Text) = Ocolit (0.0000s)")
    
    try:
        # --- MĂSURARE T3: Traducere Neuronală direct din câmpul text ---
        start_t3 = time.time()
        text_tradus = translate_text(text, target_lang=target_lang)
        end_t3 = time.time()
        t3_duration = end_t3 - start_t3
        print(f"[PERFORMANȚĂ] T3 (Google NMT): {t3_duration:.4f} secunde")
        
        # --- MĂSURARE T4: Generare audio TTS și Extragere metadate dicționar ---
        start_t4 = time.time()
        audio_file = generate_tts(text_tradus, target_lang)
        
        dict_data = get_dictionary_info(text_tradus, target_lang)
        phonetics = dict_data.get("phonetic") if dict_data else None
        
        end_t4 = time.time()
        t4_duration = end_t4 - start_t4
        print(f"[PERFORMANȚĂ] T4 (Azure Text-to-Speech & Dicționar): {t4_duration:.4f} secunde")
        
        total_server_time = t3_duration + t4_duration
        print(f"[PERFORMANȚĂ] LATENȚĂ TOTALĂ SERVER BACKEND (TEXT MODE): {total_server_time:.4f} secunde")
        print("========= FINAL EVALUARE SCENARIU MANUAL (TEXT) =========\n")

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