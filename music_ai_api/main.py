from pathlib import Path
from fastapi import APIRouter, FastAPI, BackgroundTasks, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from routers import ffn
from routers import lstm_v1
from routers import lstm_v2
import os
from fastapi.responses import FileResponse

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

apirouter = APIRouter()

TEMP_DIR = "./generated_midis"

UPLOAD_FOLDER = "./uploaded_midis"
Path(UPLOAD_FOLDER).mkdir(parents=True, exist_ok=True)

@apirouter.post("/upload_midi")
async def upload_midi(file: UploadFile = File(...)):
    if not file.filename.endswith(".mid"):
        raise HTTPException(status_code=400, detail="Only .mid files are allowed")
    file_path = os.path.join(UPLOAD_FOLDER, file.filename)
    with open(file_path, "wb") as f:
        f.write(await file.read())
    return {"message": "File uploaded successfully", "filename": file.filename}

def remove_file(file_path: str):
    """Функція для видалення файлу після скачування"""
    try:
        if os.path.exists(file_path):
            os.remove(file_path)
            print(f"Файл {file_path} видалено")
    except Exception as e:
        print(f"Помилка видалення файлу {file_path}: {e}")

@apirouter.get("/download/{filename}")
def download_midi(filename: str, background_tasks: BackgroundTasks):
    print(f"Запит на скачування файлу {filename}")
    file_path = os.path.join(TEMP_DIR, filename)
    if not os.path.exists(file_path):
        return {"error": "Файл не знайдено"}

    background_tasks.add_task(remove_file, file_path)  # Видаляємо файл після відправки
    return FileResponse(file_path, media_type="audio/midi", filename=filename)

@apirouter.get("/preview/{filename}")
def preview_midi(filename: str):
    file_path = os.path.join(TEMP_DIR, filename)
    if not os.path.exists(file_path):
        return {"error": "Файл не знайдено"}

    return FileResponse(file_path, media_type="audio/midi", filename=filename)

apirouter.include_router(lstm_v1.router, prefix="/v1/lstm", tags=["LSTM_v1"])
apirouter.include_router(lstm_v2.router, prefix="/v2/lstm", tags=["LSTM_v2"])
apirouter.include_router(ffn.router, prefix="/ffn", tags=["FFN"])

app.include_router(apirouter, prefix="/api", tags=["API"])