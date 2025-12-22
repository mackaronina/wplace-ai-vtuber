import uvicorn
from fastapi import FastAPI
from starlette.staticfiles import StaticFiles

from app.config import SETTINGS, BASE_DIR


class FastAPIServer:

    def __init__(self):
        self.server = None

    async def run_server(self) -> None:
        app = FastAPI()
        app.mount('/static', StaticFiles(directory=f'{BASE_DIR}/app/static'), name='static')
        self.server = uvicorn.Server(uvicorn.Config(app, host=SETTINGS.SERVER_HOST, port=SETTINGS.SERVER_PORT))
        await self.server.serve()

    def quit(self) -> None:
        self.server.should_exit = True
        self.server.force_exit = True
