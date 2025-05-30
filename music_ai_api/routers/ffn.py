import asyncio
from fastapi import APIRouter, File, HTTPException, UploadFile
import torch
import os
from datetime import datetime

from dto.response.generate_response import GenerateResponse
from common.constants import EXECUTOR
import utils.ffn_utils.midi_generator as midi_generator
import utils.ffn_utils.dataset_note_info_generator as note_generator
import utils.ffn_utils.constants as constants

from utils.ffn_utils.data_midi_loader import load_custom_midi_data
from generation.ffn_generator.forward_network import ForwardNetwork
from generation.ffn_generator.network_harmony_generator import NetworkHarmonyGenerator
from utils.logger import setup_logger

logger = setup_logger(__name__)

router = APIRouter()

use_cuda = torch.cuda.is_available()
device = torch.device("cuda" if use_cuda else "cpu")

network = ForwardNetwork().to(device)
network.load_state_dict(torch.load('models/best_model_new.pth', map_location=device))
network.eval()

@router.post("/harmonize")
async def harmonize_midi(file: UploadFile = File(...)):
    logger.info(f"Запит на гармонізацію файлу: {file.filename}")
    try:
        if not file.filename.endswith(".mid"):
            logger.warning(f"Спроба завантажити файл з неправильним розширенням: {file.filename}")
            raise HTTPException(status_code=400, detail="Дозволені лише MIDI-файли")
        output_filename = await asyncio.get_event_loop().run_in_executor(
            EXECUTOR, 
            harmonize_melody, 
            file
        )
        logger.info(f"Гармонізація завершена. Файл: {output_filename}")
        return GenerateResponse(message="Мелодію успішно гармонізовано", midi_file=output_filename).model_dump()
    
    except HTTPException as he:
        raise he
    except Exception as e:
        error_msg = f"Помилка під час гармонізації: {str(e)}"
        logger.error(error_msg)
        raise HTTPException(status_code=500, detail=error_msg)

def harmonize_melody(file: UploadFile = File(...)):
    logger.debug(f'Ініціалізація генерації гармонії для {file.filename}')
    harmony_generator = NetworkHarmonyGenerator(network)
    _, val_dataset = load_custom_midi_data(file)
    (x_soprano_sample, _, _, _) = val_dataset[:constants.BATCH_SIZE]
        
    logger.debug('Генерація гармонії...')
    generated_song = harmony_generator.generate_harmony(x_soprano_sample)
    generated_note_infos = note_generator.generate_note_info(generated_song)
        
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_filename = f'generated_file_{timestamp}.mid'
    output_path = 'generated_midis/' + output_filename
        
    logger.debug(f'Збереження згенерованого MIDI файлу: {output_path}')
    midi_generator.generate_midi(output_path, generated_note_infos)
    return output_filename
