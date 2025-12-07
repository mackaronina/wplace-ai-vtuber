import torch
import torchaudio
from silero import silero_tts
from transliterate import translit


class SoundModel:
    def __init__(self):
        tts, _ = silero_tts(language='ru', speaker='v5_ru')
        device = torch.device('cuda:0')
        tts.to(device)
        self.tts = tts

    def save_text_as_audio(self, text: str) -> None:
        text = translit(text, 'ru')
        audio_tensor = self.tts.apply_tts(text=text, speaker='eugene')
        torchaudio.save('sound/audio.wav', audio_tensor.unsqueeze(0), sample_rate=48000, format='wav',
                        bits_per_sample=16)
