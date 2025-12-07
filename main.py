import asyncio
import base64
import io
import logging
from threading import Thread

import simpleaudio
import torch
import torchaudio
import uvicorn
from PIL import Image
from curl_cffi import AsyncSession
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from selenium import webdriver
from selenium.webdriver import ActionChains
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.actions.wheel_input import ScrollOrigin
from selenium.webdriver.common.by import By
from silero import silero_tts
from transliterate import translit

from config import RESOURCE_URL, TEMPERATURE, TOTAL_ITERATIONS, \
    CLOUDFLARE_ACCOUNT_ID, CLOUDFLARE_MODEL_NAME, CLOUDFLARE_API_KEY
from prompts import SYSTEM_PROMPT, COMMENT_IMAGE_PROMPT, GREETINGS_PROMPT, GOODBYE_PROMPT
from schemas import GradeEnum, CommentModel


class Webcam:
    def __init__(self, driver):
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

    def hide_element(self, element):
        self.driver.execute_script('arguments[0].style.visibility="hidden";', element)

    def show_element(self, element):
        self.driver.execute_script('arguments[0].style.visibility="visible";', element)

    def play_talking_animation(self, grade):
        element = self.driver.find_element(By.ID, f'{grade.value}_gif')
        self.show_element(element)

    def stop_talking_animation(self):
        for grade in GradeEnum:
            element = self.driver.find_element(By.ID, f'{grade.value}_gif')
            self.hide_element(element)

    def say_sound_with_animation(self, grade=GradeEnum.neutral):
        async def start_with_delay():
            await asyncio.sleep(0.5)
            self.play_talking_animation(grade)

        asyncio.create_task(start_with_delay())
        Thread(target=start_with_delay).start()
        simpleaudio.WaveObject.from_wave_file('sound/audio.wav').play().wait_done()
        self.stop_talking_animation()


class WPlaceDriver:
    def __init__(self):
        options = Options()
        options.add_argument('--disable-infobars')
        options.add_argument('--lang=en')
        options.add_argument('--disable-web-security')
        options.add_experimental_option('excludeSwitches', ['enable-automation'])
        driver = webdriver.Chrome(options=options)
        driver.implicitly_wait(10)
        driver.maximize_window()
        driver.get('https://wplace.live')
        self.driver = driver
        self.hide_interface()

    def hide_element(self, element):
        self.driver.execute_script('arguments[0].style.visibility="hidden";', element)

    def show_element(self, element):
        self.driver.execute_script('arguments[0].style.visibility="visible";', element)

    def hide_interface(self):
        elements = self.driver.find_elements(By.CLASS_NAME, 'absolute')
        for element in elements:
            self.hide_element(element)
        search_button = self.driver.find_element(By.XPATH, '//button[@title="Search"]')
        self.show_element(search_button)

    def get_screen(self):
        base64_string = self.driver.get_screenshot_as_base64()
        image = Image.open(io.BytesIO(base64.b64decode(base64_string)))
        image = image.crop((0, 0, image.width - 355, image.height))
        bio = io.BytesIO()
        bio.name = 'screen.png'
        image.save(bio, format='PNG')
        bio.seek(0)
        img_str = base64.b64encode(bio.getvalue()).decode('utf-8')
        return img_str

    def add_webcam(self):
        return Webcam(self.driver)

    async def go_to_random_place(self):
        self.driver.find_element(By.XPATH, '//button[@title="Search"]').click()
        self.driver.find_element(By.XPATH, '//button[@data-tip="Random place"]').click()
        await asyncio.sleep(7)
        scroll_origin = ScrollOrigin.from_viewport(
            int(self.driver.get_window_size()['width'] / 2),
            int(self.driver.get_window_size()['height'] / 2)
        )
        ActionChains(self.driver).scroll_from_origin(scroll_origin, 0, 400).perform()
        await asyncio.sleep(1)

    def quit(self):
        self.driver.quit()


class SoundModel:
    def __init__(self):
        tts, _ = silero_tts(language='ru', speaker='v5_ru')
        device = torch.device('cuda:0')
        tts.to(device)
        self.tts = tts

    def save_text_as_audio(self, text):
        text = translit(text, 'ru')
        audio_tensor = self.tts.apply_tts(text=text, speaker='eugene')
        torchaudio.save('sound/audio.wav', audio_tensor.unsqueeze(0), sample_rate=48000, format='wav',
                        bits_per_sample=16)


async def generate_with_cloudflare(content: str | list[dict], json_model: type[BaseModel] | None = None):
    for attempts in range(5):
        try:
            link = f'https://api.cloudflare.com/client/v4/accounts/{CLOUDFLARE_ACCOUNT_ID}/ai/run/{CLOUDFLARE_MODEL_NAME}'
            headers = {
                'Authorization': f'Bearer {CLOUDFLARE_API_KEY}'
            }
            data = {
                'messages': [
                    {
                        'role': 'system',
                        'content': SYSTEM_PROMPT
                    },
                    {
                        'role': 'user',
                        'content': content
                    }
                ],
                'temperature': TEMPERATURE,
                'guided_json': json_model.model_json_schema() if json_model is not None else None
            }
            async with AsyncSession() as session:
                resp = await session.post(link, json=data, headers=headers, impersonate='chrome110', timeout=10)
                result = resp.json()['result']['response']
                return json_model.model_validate(result) if json_model is not None else result
        except Exception as e:
            print(e)
            await asyncio.sleep(1)
    return None


async def generate_comment_to_screen(base64_image):
    content = [
        {
            'type': 'text',
            'text': COMMENT_IMAGE_PROMPT
        },
        {
            'type': 'image_url',
            'image_url': {
                'url': f'data:image/png;base64,{base64_image}'
            }
        }
    ]
    return await generate_with_cloudflare(content, CommentModel)


async def generate_greetings_comment():
    return await generate_with_cloudflare(GREETINGS_PROMPT)


async def generate_goodbye_comment():
    return await generate_with_cloudflare(GOODBYE_PROMPT)


async def run_server():
    app = FastAPI()
    app.mount('/static', StaticFiles(directory='static'), name='static')
    await uvicorn.Server(uvicorn.Config(app, host='127.0.0.1', port=8000)).serve()


async def say_greetings_text(sound_model, webcam):
    comment_text = await generate_greetings_comment()
    logging.info(f'Greetings text: {comment_text}')
    sound_model.save_text_as_audio(comment_text)
    logging.info('Ready to start stream')
    input('Press enter to start\n')
    await asyncio.sleep(3)
    webcam.say_sound_with_animation()


async def say_goodbye_text(sound_model, webcam):
    comment_text = await generate_goodbye_comment()
    logging.info(f'Goodbye text: {comment_text}')
    sound_model.save_text_as_audio(comment_text)
    webcam.say_sound_with_animation()


async def say_comment_text(sound_model, webcam, screen_base64):
    comment = await generate_comment_to_screen(screen_base64)
    logging.info(f'Comment to images: {comment.text}')
    logging.info(f'Grade to images: {comment.grage}')
    sound_model.save_text_as_audio(comment.text)
    webcam.say_sound_with_animation(comment.grade)


async def main():
    asyncio.create_task(run_server())
    logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')
    logging.info('Starting stream...')
    sound_model = SoundModel()
    wplace_driver = WPlaceDriver()
    webcam = wplace_driver.add_webcam()
    await say_greetings_text(sound_model, webcam)
    for _ in range(TOTAL_ITERATIONS):
        await wplace_driver.go_to_random_place()
        screen_base64 = wplace_driver.get_screen()
        await say_comment_text(sound_model, webcam, screen_base64)
    await say_goodbye_text(sound_model, webcam)
    await asyncio.sleep(1)
    wplace_driver.quit()


if __name__ == '__main__':
    asyncio.run(main())
