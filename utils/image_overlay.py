import time
from io import BytesIO
from threading import Thread

from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.common.by import By

from config import SETTINGS
from schemas import GradeEnum
from utils.audio_player import AudioPlayer
from utils.selenium_elements import show_element, hide_element


class ImageOverlay:
    def __init__(self, driver: WebDriver):
        js_code = f"""
            const ids = ['normal_image', 'negative_gif', 'neutral_gif', 'positive_gif'];
            const srcs = ['{SETTINGS.get_resource_url('normal.png')}', \
             '{SETTINGS.get_resource_url('negative.gif')}', \
             '{SETTINGS.get_resource_url('neutral.gif')}', \
            '{SETTINGS.get_resource_url('positive.gif')}'];
            const z_indexes = [100, 101, 101, 101]
            for (let i = 0; i < ids.length; i++) {{
                const img = document.createElement('img');
                img.id = ids[i];
                img.src = srcs[i];
                img.alt = 'Loading...';
                img.width = '300';
                img.height = '300';
                img.style.position = 'absolute';
                img.style.bottom = '0px';
                img.style.right = '0px';
                img.style.zIndex = z_indexes[i];
                document.body.appendChild(img);
            }}
        """
        driver.execute_script(js_code)
        self.driver = driver
        self.stop_talking_animation()

    def play_talking_animation(self, grade: GradeEnum = GradeEnum.neutral) -> None:
        element = self.driver.find_element(By.ID, f'{grade.value}_gif')
        show_element(self.driver, element)

    def stop_talking_animation(self) -> None:
        for grade in GradeEnum:
            element = self.driver.find_element(By.ID, f'{grade.value}_gif')
            hide_element(self.driver, element)

    def say_audio_with_animation(self, audio: BytesIO, player: AudioPlayer,
                                 grade: GradeEnum = GradeEnum.neutral) -> None:
        def start_with_delay():
            time.sleep(0.5)
            self.play_talking_animation(grade)

        Thread(target=start_with_delay).start()
        player.play_wav_brom_binary(audio)
        self.stop_talking_animation()
