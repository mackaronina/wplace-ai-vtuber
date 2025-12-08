import base64
import io
import time

from PIL import Image
from selenium import webdriver
from selenium.webdriver import ActionChains
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.actions.wheel_input import ScrollOrigin
from selenium.webdriver.common.by import By

from utils.image_webcam import ImageWebcam
from utils.selenium_utils import show_element, hide_element


# POM - PAGE OBJECT MODEL
class WPlacePOM:
    def __init__(self):
        options = Options()
        options.add_argument('--disable-infobars')
        options.add_argument('--lang=en')
        options.add_argument('--disable-web-security')
        prefs = {'profile.default_content_setting_values.geolocation': 2}
        options.add_experimental_option('prefs', prefs)
        options.add_experimental_option('excludeSwitches', ['enable-automation'])
        driver = webdriver.Chrome(options=options)
        driver.implicitly_wait(10)
        driver.maximize_window()
        driver.get('https://wplace.live')
        self.driver = driver
        self.hide_interface()

    def hide_interface(self) -> None:
        elements = self.driver.find_elements(By.CLASS_NAME, 'absolute')
        for element in elements:
            hide_element(self.driver, element)
        search_button = self.driver.find_element(By.XPATH, '//button[@title="Search"]')
        show_element(self.driver, search_button)

    def get_screen_as_base64(self) -> str:
        base64_string = self.driver.get_screenshot_as_base64()
        image = Image.open(io.BytesIO(base64.b64decode(base64_string)))
        image = image.crop((0, 0, image.width - 355, image.height))
        bio = io.BytesIO()
        bio.name = 'screen.png'
        image.save(bio, format='PNG')
        bio.seek(0)
        img_str = base64.b64encode(bio.getvalue()).decode('utf-8')
        return img_str

    def add_webcam(self) -> ImageWebcam:
        return ImageWebcam(self.driver)

    def go_to_random_place(self) -> None:
        self.driver.find_element(By.XPATH, '//button[@title="Search"]').click()
        self.driver.find_element(By.XPATH, '//button[@data-tip="Random place"]').click()
        time.sleep(7)
        scroll_origin = ScrollOrigin.from_viewport(
            int(self.driver.get_window_size()['width'] / 2),
            int(self.driver.get_window_size()['height'] / 2)
        )
        ActionChains(self.driver).scroll_from_origin(scroll_origin, 0, 400).perform()
        time.sleep(1)

    def quit(self) -> None:
        self.driver.quit()
