from io import BytesIO

import torch
import torchaudio
from silero import silero_tts
from transliterate import translit

from config import SETTINGS


class TTSModel:
    def __init__(self):
        tts, _ = silero_tts(language='ru', speaker='v5_ru')
        device = torch.device(SETTINGS.TORCH_DEVICE)
        tts.to(device)
        self.tts = tts

    def text_to_audio(self, text: str) -> BytesIO:
        text = translit(text, 'ru')
        audio_tensor = self.tts.apply_tts(text=text, speaker=SETTINGS.SILERO_SPEAKER)
        audio = BytesIO()
        torchaudio.save(audio, audio_tensor.unsqueeze(0), sample_rate=48000, format='wav', bits_per_sample=16)
        audio.seek(0)
        return audio
