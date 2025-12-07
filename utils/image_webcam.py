import time
from threading import Thread

import simpleaudio
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.common.by import By

from config import RESOURCE_URL
from schemas import GradeEnum
from utils.selenium_utils import show_element, hide_element


class ImageWebcam:
    def __init__(self, driver: WebDriver):
        js_code = f"""
            const ids = ['normal_image', 'negative_gif', 'neutral_gif', 'positive_gif'];
            const srcs = ['{RESOURCE_URL}/normal.png', '{RESOURCE_URL}/negative.gif', '{RESOURCE_URL}/neutral.gif', '{RESOURCE_URL}/positive.gif'];
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

    def say_sound_with_animation(self, grade: GradeEnum = GradeEnum.neutral) -> None:
        def start_with_delay():
            time.sleep(0.5)
            self.play_talking_animation(grade)

        Thread(target=start_with_delay).start()
        simpleaudio.WaveObject.from_wave_file('sound/audio.wav').play().wait_done()
        self.stop_talking_animation()
