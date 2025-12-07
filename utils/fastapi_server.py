import logging

import uvicorn
from fastapi import FastAPI
from starlette.staticfiles import StaticFiles


class FastAPIServer:

    def __init__(self):
        self.server = None

    async def run_server(self) -> None:
        app = FastAPI()
        app.mount('/static', StaticFiles(directory='static'), name='static')
        logging.info('Starting server...')
        self.server = uvicorn.Server(uvicorn.Config(app, host='127.0.0.1', port=8000))
        await self.server.serve()

    def shutdown(self) -> None:
        logging.info('Stopping server...')
        self.server.should_exit = True
        self.server.force_exit = True
