import asyncio
import logging
import time
from threading import Thread

from config import TOTAL_ITERATIONS
from utils.audio_player import AudioPlayer
from utils.fastapi_server import FastAPIServer
from utils.say_text import say_greetings_text, say_comment_text, say_goodbye_text
from utils.tts_model import TTSModel
from utils.wplace_pom import WPlacePOM


def main() -> None:
    server = FastAPIServer()
    Thread(target=asyncio.run, args=(server.run_server(),)).start()
    logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')
    logging.info('Preparing to launch the stream...')
    player = AudioPlayer()
    tts = TTSModel()
    wplace_driver = WPlacePOM()
    webcam = wplace_driver.add_webcam()
    logging.info('Ready to start stream')
    input('Press enter to start\n')
    say_greetings_text(tts, webcam, player)
    for _ in range(TOTAL_ITERATIONS):
        wplace_driver.go_to_random_place()
        screen_base64 = wplace_driver.get_screen_as_base64()
        say_comment_text(tts, webcam, player, screen_base64)
    say_goodbye_text(tts, webcam, player)
    time.sleep(1)
    wplace_driver.quit()
    player.quit()
    server.quit()


if __name__ == '__main__':
    main()
