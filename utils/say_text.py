import logging

from utils.ai_generate import generate_greetings_comment, generate_goodbye_comment, generate_comment_to_screen
from utils.audio_player import AudioPlayer
from utils.image_webcam import ImageWebcam
from utils.tts_model import TTSModel


def say_greetings_text(tts: TTSModel, webcam: ImageWebcam, player: AudioPlayer) -> None:
    comment_text = generate_greetings_comment()
    logging.info(f'Greetings text: {comment_text}')
    audio = tts.text_to_audio(comment_text)
    webcam.say_audio_with_animation(audio, player)


def say_goodbye_text(tts: TTSModel, webcam: ImageWebcam, player: AudioPlayer) -> None:
    comment_text = generate_goodbye_comment()
    logging.info(f'Goodbye text: {comment_text}')
    audio = tts.text_to_audio(comment_text)
    webcam.say_audio_with_animation(audio, player)


def say_comment_text(tts: TTSModel, webcam: ImageWebcam, player: AudioPlayer, screen_base64: str) -> None:
    comment = generate_comment_to_screen(screen_base64)
    logging.info(f'Comment to images: {comment.text}')
    logging.info(f'Grade to images: {comment.grade}')
    audio = tts.text_to_audio(comment.text)
    webcam.say_audio_with_animation(audio, player, comment.grade)
