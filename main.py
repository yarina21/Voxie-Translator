import os
import shutil
import uuid
from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from backend.services import transcribe_audio, translate_text, generate_tts

app = FastAPI(title="Voxie API")

# --- CONFIGURARE STATICE ---
# Permite accesarea fișierelor audio generate prin URL (ex: http://localhost:8000/static/fisier.mp3)
app.mount("/static", StaticFiles(directory="."), name="static")

# --- CONFIGURARE CORS ---
# Permite aplicației React (sau Swagger) să comunice cu backend-ul
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def home():
    return {"message": "Voxie Online - Backend is running"}

@app.post("/process-audio")
async def process_audio(
    target_lang: str = Form("en"),    # Limba în care se traduce
    source_lang: str = Form("auto"),  # "auto" sau cod fix (ex: "it-IT")
    file: UploadFile = File(...)
):
    # Generăm un nume unic pentru fișierul audio primit (input)
    file_extension = os.path.splitext(file.filename)[1]
    temp_path = f"temp_{uuid.uuid4()}{file_extension}"
    
    try:
        # 1. Salvare fișier primit de la client
        with open(temp_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # 2. Transcriere (Azure STT)
        text_original, lang_detected = transcribe_audio(temp_path, source_lang=source_lang)
        
        # 3. Traducere (Google NMT)
        text_tradus = translate_text(text_original, target_lang=target_lang)
        
        # 4. Generare Sinteză Vocală (Azure TTS)
        # Atenție: generate_tts trebuie să fie definită în services.py
        audio_file = generate_tts(text_tradus, target_lang)
        
        # 5. Returnăm rezultatul complet
        return {
            "status": "success",
            "detected_language": lang_detected,
            "original_text": text_original,
            "translated_text": text_tradus,
            "target_language": target_lang,
            "audio_url": f"http://localhost:8000/static/{audio_file}" if audio_file else None
        }
        
    except Exception as e:
        print(f"!!! Eroare Backend: {str(e)} !!!")
        return {"status": "error", "message": str(e)}
        
    finally:
        # 6. Curățenie: Ștergem fișierul audio de intrare (cel temporar)
        # Fișierul TTS rămâne în folderul curent pentru a fi servit prin /static
        if os.path.exists(temp_path):
            os.remove(temp_path)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)