import logging

from app.utils.audio_player import AudioPlayer
from app.utils.image_overlay import ImageOverlay
from app.utils.llm_model import LLMModel
from app.utils.tts_model import TTSModel


def say_greetings_text(tts: TTSModel, overlay: ImageOverlay, player: AudioPlayer, llm: LLMModel) -> None:
    comment_text = llm.generate_greetings_comment()
    logging.info(f'Greetings text: {comment_text}')
    audio = tts.text_to_audio(comment_text)
    overlay.say_audio_with_animation(audio, player)


def say_goodbye_text(tts: TTSModel, overlay: ImageOverlay, player: AudioPlayer, llm: LLMModel) -> None:
    comment_text = llm.generate_goodbye_comment()
    logging.info(f'Goodbye text: {comment_text}')
    audio = tts.text_to_audio(comment_text)
    overlay.say_audio_with_animation(audio, player)


def say_comment_text(tts: TTSModel, overlay: ImageOverlay, player: AudioPlayer, llm: LLMModel,
                     screen_base64: str) -> None:
    comment = llm.generate_comment_to_screen(screen_base64)
    logging.info(f'Comment to images: {comment.text}')
    logging.info(f'Grade to images: {comment.grade}')
    audio = tts.text_to_audio(comment.text)
    overlay.say_audio_with_animation(audio, player, comment.grade)
