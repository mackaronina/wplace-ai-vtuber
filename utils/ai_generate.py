import logging
import time

from curl_cffi import Session
from pydantic import BaseModel

from config import SETTINGS
from prompts import COMMENT_IMAGE_PROMPT, GREETINGS_PROMPT, SYSTEM_PROMPT, GOODBYE_PROMPT
from schemas import CommentModel


def generate_with_cloudflare(content: str | list[dict],
                             json_model: type[BaseModel] | None = None) -> BaseModel | str | None:
    for attempts in range(5):
        try:
            link = (f'https://api.cloudflare.com/client/v4/accounts/{SETTINGS.CLOUDFLARE.ACCOUNT_ID}/ai/run/'
                    f'{SETTINGS.CLOUDFLARE.MODEL_NAME}')
            headers = {
                'Authorization': f'Bearer {SETTINGS.CLOUDFLARE.API_KEY.get_secret_value()}'
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
                'temperature': SETTINGS.CLOUDFLARE.MODEL_TEMPERATURE,
                'guided_json': json_model.model_json_schema() if json_model is not None else None
            }
            with Session() as session:
                resp = session.post(link, json=data, headers=headers, impersonate='chrome110',
                                    timeout=SETTINGS.CLOUDFLARE.REQUEST_TIMEOUT_SECONDS)
                result = resp.json()['result']['response']
                return json_model.model_validate(result) if json_model is not None else result
        except Exception as e:
            logging.error(f'Error with cloudlfare request: {e}', exc_info=True)
            time.sleep(1)
    return None


def generate_comment_to_screen(base64_image: str) -> CommentModel | None:
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
    return generate_with_cloudflare(content, CommentModel)


def generate_greetings_comment() -> str | None:
    return generate_with_cloudflare(GREETINGS_PROMPT)


def generate_goodbye_comment() -> str | None:
    return generate_with_cloudflare(GOODBYE_PROMPT)
