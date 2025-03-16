from fastapi import APIRouter, FastAPI, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from routers import lstm
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

    # background_tasks.add_task(remove_file, file_path)  # Видаляємо файл після відправки
    return FileResponse(file_path, media_type="audio/midi", filename=filename)


apirouter.include_router(lstm.router, prefix="/lstm", tags=["LSTM"])
# api_router.include_router(vae.router, prefix="/vae", tags=["VAE"])
# api_router.include_router(ffn.router, prefix="/ffn", tags=["FFN"])

app.include_router(apirouter, prefix="/api", tags=["API"])