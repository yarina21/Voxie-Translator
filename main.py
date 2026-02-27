import os
import shutil
from fastapi import FastAPI, UploadFile, File, Query
from backend.services import transcribe_audio, translate_text

app = FastAPI(title="Voxie API")

@app.get("/")
def home():
    return {"message": "Voxie Online"}

@app.post("/process-audio")
async def process_audio(
    target_lang: str = Query("en", description="Limba țintă (ex: en, es, fr)"),
    file: UploadFile = File(...)
):
    # Creăm un nume temporar pentru fișierul audio
    temp_path = f"temp_{file.filename}"
    
    try:
        # Salvăm fișierul primit pe disc
        with open(temp_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # PASUL 1: Transcrierea (Așteptăm 2 valori: text și limbă)
        text_original, lang_detected = transcribe_audio(temp_path)
        
        # PASUL 2: Traducerea (Folosim textul de la pasul 1)
        text_tradus = translate_text(text_original, target_lang=target_lang)
        
        # Trimitem rezultatul înapoi
        return {
            "status": "success",
            "detected_language": lang_detected,
            "original_text": text_original,
            "translated_text": text_tradus,
            "target_language": target_lang
        }
        
    except Exception as e:
        return {"status": "error", "message": str(e)}
        
    finally:
        # Curățăm fișierul audio după ce am terminat
        if os.path.exists(temp_path):
            os.remove(temp_path)
