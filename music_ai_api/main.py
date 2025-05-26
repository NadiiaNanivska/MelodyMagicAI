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
import cloudinary.api
from cloudinary.uploader import destroy
from cloudinary import Search
from apscheduler.schedulers.background import BackgroundScheduler


logger = setup_logger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    await asyncio.to_thread(clean_old_files)
    yield
    EXECUTOR.shutdown(wait=True)

app = FastAPI(lifespan=lifespan)

def clean_old_files():
    today_date = datetime.today().date()
    next_cursor = None
    batch_size = 1
    logger.info(f"Видалення файлів, які не відповідають сьогоднішній даті {today_date}")
    resources = cloudinary.api.resources_by_asset_folder(
            asset_folder="midi_files",
            max_results=batch_size,
            next_cursor=next_cursor
        )
    while True:   
        public_ids_to_delete = []
        for resource in resources['resources']:
            created_at = datetime.strptime(resource['created_at'], '%Y-%m-%dT%H:%M:%SZ').date()
            if created_at != today_date:
                public_ids_to_delete.append(resource['public_id'])

        if public_ids_to_delete:
            cloudinary.api.delete_resources(public_ids=public_ids_to_delete, resource_type='raw')
            logger.info(f"Батч файлів {public_ids_to_delete} успішно видалено")

        next_cursor = resources.get('next_cursor')
        if not next_cursor:
            break

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

apirouter = APIRouter()

async def delete_from_cloudinary(public_id: str):
    try:
        return destroy(public_id, resource_type="raw")
    except Exception as e:
        logger.debug(f"Помилка при видаленні файлу {public_id} з Cloudinary: {e}")

@apirouter.get("/download/{filename}")
async def download_midi(filename: str, background_tasks: BackgroundTasks):
    await asyncio.sleep(3)
    response_info = Search().expression(f"public_id:midi_files/generated_midis/{filename}").execute();
    logger.debug(f"Результат пошуку: {response_info}")
    if not response_info['resources']:
        raise HTTPException(status_code=404, detail="Файл не знайдено на Cloudinary")
    async with httpx.AsyncClient() as client:
        response = await client.get(response_info['resources'][0]['secure_url'])
        logger.debug(f"Код відповіді: {response.status_code}")

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
    logger.debug(f"Результат пошуку: {response_info}")
    if not response_info['resources']:
        raise HTTPException(status_code=404, detail="Файл не знайдено на Cloudinary")
    async with httpx.AsyncClient() as client:
        response = await client.get(response_info['resources'][0]['secure_url'])
        logger.debug(f"Код відповіді: {response.status_code}")

        return StreamingResponse(
            response.aiter_bytes(),
            media_type="audio/midi",
            headers={"Content-Disposition": f'inline; filename="{filename}"'}
        )
    
apirouter.include_router(lstm_v2.router, prefix="/v2/lstm", tags=["LSTM_v2"])
apirouter.include_router(ffn.router, prefix="/ffn", tags=["FFN"])

app.include_router(apirouter, prefix="/api", tags=["API"])

scheduler = BackgroundScheduler()
scheduler.add_job(clean_old_files, 'cron', hours=0)
scheduler.start()