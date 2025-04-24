import asyncio
from fastapi import APIRouter, HTTPException
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

midi_file_path = 'uploaded_midis'

network = ForwardNetwork().to(device)
network.load_state_dict(torch.load('models/best_model_new.pth', map_location=device))
network.eval()

@router.get("/harmonize/{filename}")
async def harmonize_midi(filename: str):
    logger.info(f"Розпочато обробку запиту на гармонізацію файлу: {filename}")
    try:
        output_filename = await asyncio.get_event_loop().run_in_executor(
            EXECUTOR, 
            harmonize_melody, 
            filename
        )
        logger.info(f"Гармонізація мелодії успішно завершена. Вихідний файл: {output_filename}")
        return GenerateResponse(message="Мелодію успішно гармонізовано", midi_file=output_filename).model_dump()
    
    except HTTPException as he:
        raise he
    except Exception as e:
        error_msg = f"Помилка під час гармонізації: {str(e)}"
        logger.error(error_msg)
        raise HTTPException(status_code=500, detail=error_msg)

def harmonize_melody(filename):
    file_path = os.path.join(midi_file_path, filename)
    if not os.path.exists(file_path):
        logger.error(f"Файл не знайдено: {file_path}")
        raise HTTPException(status_code=404, detail="MIDI-файл не знайдено")
        
    logger.info(f'Ініціалізація генерації гармонії для {filename}')
    harmony_generator = NetworkHarmonyGenerator(network)
    _, val_dataset = load_custom_midi_data(midi_file_path)
    (x_soprano_sample, _, _, _) = val_dataset[:constants.BATCH_SIZE]
        
    logger.info('Генерація гармонії...')
    generated_song = harmony_generator.generate_harmony(x_soprano_sample)
    generated_note_infos = note_generator.generate_note_info(generated_song)
        
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_filename = f'generated_file_{timestamp}.mid'
    output_path = os.path.join('generated_midis', output_filename)
        
    logger.info(f'Збереження згенерованого MIDI файлу: {output_path}')
    midi_generator.generate_midi(output_path, generated_note_infos)
    return output_filename
