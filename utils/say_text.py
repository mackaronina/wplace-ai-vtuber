import logging

from utils.cloudflare_generate import generate_greetings_comment, generate_goodbye_comment, generate_comment_to_screen
from utils.image_webcam import ImageWebcam
from utils.sound_model import SoundModel


def say_greetings_text(sound_model: SoundModel, webcam: ImageWebcam) -> None:
    comment_text = generate_greetings_comment()
    logging.info(f'Greetings text: {comment_text}')
    sound_model.save_text_as_audio(comment_text)
    webcam.say_sound_with_animation()


def say_goodbye_text(sound_model: SoundModel, webcam: ImageWebcam) -> None:
    comment_text = generate_goodbye_comment()
    logging.info(f'Goodbye text: {comment_text}')
    sound_model.save_text_as_audio(comment_text)
    webcam.say_sound_with_animation()


def say_comment_text(sound_model: SoundModel, webcam: ImageWebcam, screen_base64: str) -> None:
    comment = generate_comment_to_screen(screen_base64)
    logging.info(f'Comment to images: {comment.text}')
    logging.info(f'Grade to images: {comment.grade}')
    sound_model.save_text_as_audio(comment.text)
    webcam.say_sound_with_animation(comment.grade)
