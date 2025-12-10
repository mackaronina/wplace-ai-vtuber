import wave
from io import BytesIO

import pyaudio

from config import SETTINGS


class AudioPlayer:
    def __init__(self):
        self.player = pyaudio.PyAudio()

    def play_wav_brom_binary(self, audio: BytesIO) -> None:
        with wave.open(audio, 'rb') as wf:
            stream = self.player.open(format=self.player.get_format_from_width(wf.getsampwidth()),
                                      channels=wf.getnchannels(),
                                      rate=wf.getframerate(),
                                      output=True
                                      )
            while len(data := wf.readframes(SETTINGS.AUDIO_CHUNK_SIZE)):  # Requires Python 3.8+ for :=
                stream.write(data)
            stream.close()

    def quit(self):
        self.player.terminate()
