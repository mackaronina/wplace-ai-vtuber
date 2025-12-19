import logging
import time
from datetime import datetime

from pydantic import BaseModel
from requests import Session

from config import SETTINGS
from prompts import GREETINGS_PROMPT, SYSTEM_PROMPT, GOODBYE_PROMPT, FIRST_COMMENT_IMAGE_PROMPT, \
    SCHEMA_DESCRIPTION, SECOND_COMMENT_IMAGE_PROMPT
from schemas import CommentModel


def generate_with_cloudflare(content: str | list[dict],
                             json_model: type[BaseModel] | None = None) -> BaseModel | str:
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
                        'content': SYSTEM_PROMPT.format(current_date=datetime.now().strftime("%d.%m.%Y"))
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
                resp = session.post(link, json=data, headers=headers,
                                    timeout=SETTINGS.CLOUDFLARE.REQUEST_TIMEOUT_SECONDS)
                result = resp.json()['result']['response']
                return json_model.model_validate(result) if json_model is not None else result
        except Exception as e:
            logging.error(f'Error with cloudlfare request: {e}', exc_info=True)
            time.sleep(1)
    raise Exception('Generation error')


class LLMModel:
    def __init__(self):
        self.last_grade = None

    def generate_comment_to_screen(self, base64_image: str) -> CommentModel:
        if self.last_grade is None:
            prompt = FIRST_COMMENT_IMAGE_PROMPT.format(schema_description=SCHEMA_DESCRIPTION)
        else:
            prompt = SECOND_COMMENT_IMAGE_PROMPT.format(last_grade=self.last_grade.value,
                                                        schema_description=SCHEMA_DESCRIPTION)
        content = [
            {
                'type': 'text',
                'text': prompt
            },
            {
                'type': 'image_url',
                'image_url': {
                    'url': f'data:image/png;base64,{base64_image}'
                }
            }
        ]
        comment = generate_with_cloudflare(content, CommentModel)
        self.last_grade = comment.grade
        return comment

    def generate_greetings_comment(self) -> str:
        return generate_with_cloudflare(GREETINGS_PROMPT)

    def generate_goodbye_comment(self) -> str:
        return generate_with_cloudflare(GOODBYE_PROMPT)
