import io
import mido
import pretty_midi
import cloudinary
import os 
from cloudinary.uploader import upload
from fastapi import HTTPException, status, UploadFile
from dotenv import load_dotenv
from typing import List

load_dotenv()

cloudinary.config(
    cloud_name=os.getenv("CLOUDINARY_CLOUD_NAME"),
    api_key=os.getenv("CLOUDINARY_API_KEY"),
    api_secret=os.getenv("CLOUDINARY_API_SECRET"),
    secure=True
)

def upload_pm_midi(pm: pretty_midi.PrettyMIDI, out_file: str) -> str:
    midi_io = io.BytesIO()
    pm.write(midi_io)
    midi_io.seek(0)

    try:
        upload_result = upload(
            midi_io,
            resource_type="raw",
            folder="midi_files",
            public_id=out_file,
            overwrite=True
        )
        return upload_result['secure_url']

    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Помилка під час завантаження MIDI файлу: {e}")
    

def upload_mido_midi(mid: mido.MidiFile, out_file: str) -> str:
    midi_io = io.BytesIO()
    mid.save(file=midi_io)
    midi_io.seek(0)
    # try:
    upload_result = upload(
        midi_io,
        resource_type="raw",
        folder="midi_files",
        public_id=out_file,
        overwrite=True
    )
    return upload_result['secure_url']

    # except Exception as e:
    #     raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Помилка під час завантаження MIDI файлу: {e}")