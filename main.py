import asyncio
import logging
import time
from threading import Thread

from config import SETTINGS
from utils.audio_player import AudioPlayer
from utils.fastapi_server import FastAPIServer
from utils.llm_model import LLMModel
from utils.say_text import say_greetings_text, say_comment_text, say_goodbye_text
from utils.tts_model import TTSModel
from utils.wplace_pom import WPlacePOM


def main() -> None:
    logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')
    logging.info('Preparing to launch the stream...')

    server = FastAPIServer()
    Thread(target=asyncio.run, args=(server.run_server(),)).start()

    tts = TTSModel()
    wplace_driver = WPlacePOM()
    overlay = wplace_driver.add_overlay()
    player = AudioPlayer()
    llm = LLMModel()

    logging.info('Ready to start stream')
    input('Press enter to start\n')

    # Greetings
    say_greetings_text(tts, overlay, player, llm)

    # Main part of the stream
    for _ in range(SETTINGS.STREAM_ITERATIONS):
        wplace_driver.go_to_random_place()
        screen_base64 = wplace_driver.get_screen_as_base64()
        say_comment_text(tts, overlay, player, llm, screen_base64)

    # Farewell
    say_goodbye_text(tts, overlay, player, llm)

    time.sleep(1)
    wplace_driver.quit()
    player.quit()
    server.quit()


if __name__ == '__main__':
    main()
