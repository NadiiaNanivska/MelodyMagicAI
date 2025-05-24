from contextlib import asynccontextmanager
from pathlib import Path
from fastapi import APIRouter, FastAPI, BackgroundTasks, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
import httpx
from common.constants import FILE_NOT_FOUND, EXECUTOR
from dto.response.generate_response import GenerateResponse
from routers import ffn, lstm_v2
import os
from fastapi.responses import FileResponse, StreamingResponse
from datetime import datetime
import asyncio
from utils.logger import setup_logger
from cloudinary.uploader import destroy 
from cloudinary import Search

logger = setup_logger(__name__)

TEMP_DIR = "./generated_midis"
Path(TEMP_DIR).mkdir(parents=True, exist_ok=True)

@asynccontextmanager
async def lifespan(app: FastAPI):
    await asyncio.to_thread(clean_old_files)
    yield
    EXECUTOR.shutdown(wait=True)

app = FastAPI(lifespan=lifespan)

def clean_old_files():
    today_date = datetime.today().strftime('%Y%m%d')
    logger.info(f"Видалення файлів, які не відповідають сьогоднішній даті {today_date}")
    for filename in os.listdir(TEMP_DIR):
        file_path = os.path.join(TEMP_DIR, filename)
        if not filename.__contains__(today_date):
            logger.info(f"Файл {filename} не відповідає сьогоднішній даті")
            if os.path.isfile(file_path):
                try:
                    os.remove(file_path)
                    logger.info(f"Файл {filename} видалено")
                except Exception as e:
                    logger.error(f"Помилка при видаленні файлу {filename}: {str(e)}")

def remove_file(file_path: str):
    """Функція для видалення файлу після завантаження"""
    try:
        if os.path.exists(file_path):
            os.remove(file_path)
            logger.info(f"Файл {file_path} видалено")
    except Exception as e:
        logger.warning(f"Помилка видалення файлу {file_path}: {e}")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

apirouter = APIRouter()

# @apirouter.get("/download/{filename}")
# async def download_midi(filename: str, background_tasks: BackgroundTasks):
#     logger.info(f"Запит на скачування файлу {filename}")
#     try:
#         file_path = os.path.join(TEMP_DIR, filename)
#         if not os.path.exists(file_path):
#             logger.warning(f"Файл не знайдено: {filename}")
#             return {"error": FILE_NOT_FOUND}

#         background_tasks.add_task(remove_file, file_path)
#         logger.info(f"Файл {filename} успішно відправлено на скачування")
#         return FileResponse(file_path, media_type="audio/midi", filename=filename)
#     except Exception as e:
#         logger.error(f"Помилка при скачуванні файлу {filename}: {str(e)}")
#         raise

# @apirouter.get("/preview/{filename}")
# async def preview_midi(filename: str):
#     logger.info(f"Запит на попередній перегляд файлу {filename}")
#     try:
#         file_path = os.path.join(TEMP_DIR, filename)
#         if not os.path.exists(file_path):
#             logger.warning(f"Файл не знайдено: {filename}")
#             return {"error": FILE_NOT_FOUND}

#         logger.info(f"Файл {filename} успішно відправлено на попередній перегляд")
#         return FileResponse(file_path, media_type="audio/midi", filename=filename)
#     except Exception as e:
#         logger.error(f"Помилка при попередньому перегляді файлу {filename}: {str(e)}")
#         raise

async def delete_from_cloudinary(public_id: str):
    try:
        destroy(public_id, resource_type="raw")
    except Exception as e:
        print(f"Error deleting file {public_id} from Cloudinary: {e}")

@apirouter.get("/download/{filename}")
async def download_midi(filename: str, background_tasks: BackgroundTasks):
    await asyncio.sleep(3)
    response_info = Search().expression(f"public_id:midi_files/generated_midis/{filename}").execute();
    logger.info(f"Search result: {response_info}")
    if not response_info['resources']:
        raise HTTPException(status_code=404, detail="File not found on Cloudinary")
    async with httpx.AsyncClient() as client:
        response = await client.get(response_info['resources'][0]['secure_url'])
        logger.info(f"Response status code: {response.status_code}")

        background_tasks.add_task(delete_from_cloudinary, f"midi_files/generated_midis/{filename}")

        return StreamingResponse(
            response.aiter_bytes(),
            media_type="audio/midi",
            headers={"Content-Disposition": f'inline; filename="{filename}"'}
        )


@apirouter.get("/preview/{filename}")
async def preview_midi(filename: str):
    await asyncio.sleep(3)
    response_info = Search().expression(f"public_id:midi_files/generated_midis/{filename}").execute();
    logger.info(f"Search result: {response_info}")
    if not response_info['resources']:
        raise HTTPException(status_code=404, detail="File not found on Cloudinary")
    async with httpx.AsyncClient() as client:
        response = await client.get(response_info['resources'][0]['secure_url'])
        logger.info(f"Response status code: {response.status_code}")

        return StreamingResponse(
            response.aiter_bytes(),
            media_type="audio/midi",
            headers={"Content-Disposition": f'inline; filename="{filename}"'}
        )
    
apirouter.include_router(lstm_v2.router, prefix="/v2/lstm", tags=["LSTM_v2"])
apirouter.include_router(ffn.router, prefix="/ffn", tags=["FFN"])

app.include_router(apirouter, prefix="/api", tags=["API"])