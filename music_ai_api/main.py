from fastapi import FastAPI, BackgroundTasks
from routers import lstm
import os
from fastapi.responses import FileResponse

app = FastAPI()

app.include_router(lstm.router, prefix="/lstm", tags=["LSTM"])
# app.include_router(vae.router, prefix="/vae", tags=["VAE"])
# app.include_router(ffn.router, prefix="/ffn", tags=["FFN"])

TEMP_DIR = "./generated_midis"

def remove_file(file_path: str):
    """Функція для видалення файлу після скачування"""
    try:
        if os.path.exists(file_path):
            os.remove(file_path)
            print(f"Файл {file_path} видалено")
    except Exception as e:
        print(f"Помилка видалення файлу {file_path}: {e}")

@app.get("/download/{filename}")
def download_midi(filename: str, background_tasks: BackgroundTasks):
    file_path = os.path.join(TEMP_DIR, filename)
    if not os.path.exists(file_path):
        return {"error": "Файл не знайдено"}

    # background_tasks.add_task(remove_file, file_path)  # Видаляємо файл після відправки
    return FileResponse(file_path, media_type="audio/midi", filename=filename)
