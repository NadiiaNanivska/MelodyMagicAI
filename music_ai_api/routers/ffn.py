from fastapi import APIRouter, HTTPException
import torch
import os
from datetime import datetime

from dto.response.generate_response import GenerateResponse
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
def harmonize_midi(filename: str):
    file_path = os.path.join(midi_file_path, filename)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="MIDI file not found")
    
    logger.info(f'Generating harmony for {filename}')
    harmony_generator = NetworkHarmonyGenerator(network)
    _, val_dataset = load_custom_midi_data(midi_file_path)
    (x_soprano_sample, _, _, _) = val_dataset[:constants.BATCH_SIZE]
    
    generated_song = harmony_generator.generate_harmony(x_soprano_sample)
    generated_note_infos = note_generator.generate_note_info(generated_song)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_filename = f'generated_file_{timestamp}.mid'
    output_path = os.path.join('generated_midis', output_filename)
    
    midi_generator.generate_midi(output_path, generated_note_infos)
    
    return GenerateResponse(message="Мелодія гармонізована успішно", midi_file=output_filename). model_dump()
