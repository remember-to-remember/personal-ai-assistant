""" Module for acceptor api. """

import uvicorn
from fastapi import FastAPI, HTTPException, Request, Security, status
from fastapi.responses import PlainTextResponse
from fastapi.security import APIKeyHeader
from structlog import get_logger

from core import config, main
from core.data_repository import Caller

def init() -> None:
    """Entry point if called as an executable."""

    logger = get_logger()
    logger.info("Starting init from acceptor api")

    main.init()

    # configure uvicorn logging formatters
    uvicorn_log_config = uvicorn.config.LOGGING_CONFIG
    uvicorn_log_default_formatter = uvicorn_log_config["formatters"]["default"]
    uvicorn_log_default_formatter["fmt"] = "%(asctime)s [%(levelprefix)s] %(message)s"
    uvicorn_log_access_formatter = uvicorn_log_config["formatters"]["access"]
    uvicorn_log_access_formatter["fmt"] = (
        '%(asctime)s [%(levelprefix)s] %(client_addr)s - "%(request_line)s" %(status_code)s'
    )
    uvicorn_log_access_formatter["datefmt"] = uvicorn_log_default_formatter[
        "datefmt"
    ] = "%Y-%m-%d %H:%M:%S"

    # run uvicorn
    uvicorn.run(
        "core.api:app",
        host="0.0.0.0",
        port=config.CONFIG.api_port,
        reload=config.CONFIG.api_reload,
        log_level="debug" if config.CONFIG.debug_mode else "info",
        ssl_certfile="certs/api.remember2.co/fullchain.pem",
        ssl_keyfile="certs/api.remember2.co/privkey.pem",
    )

    logger.info("Completed init from acceptor api")


if __name__ == "__main__":
    init()


app = FastAPI(
    title="Personal AI Assistant API",
    version="0.1.0",
)


@app.get("/")
async def get_root() -> dict[str, str]:
    """Get root path."""

    logger = get_logger()
    logger.info("Starting get root path - '/' from acceptor api")
    logger.info("Completed get root path - '/' from acceptor api")

    return {"msg": "Welcome to the Whatsapp API!"}


def get_caller(
    api_key_header: str = Security(APIKeyHeader(name="WEBHOOK_VERIFY_TOKEN")),
) -> Caller:
    caller = main.get_caller(api_key_header)
    if caller:
        return caller
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Missing or invalid webhook verify token!",
    )


@app.get("/webhook", response_class=PlainTextResponse)
async def get_webhook(request: Request) -> str:
    """Get webhook."""

    logger = get_logger()
    logger.info("Starting get webhook - '/webhook' from acceptor api")

    body = dict(request.query_params)
    response = await main.process_initial_connection(body)

    logger.info("Completed get webhook - '/webhook' from acceptor api")
    if response:
        return response
    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")


@app.post("/webhook")
async def webhook_handler(request: Request):
    """Post webhook."""

    logger = get_logger()
    logger.info("Starting post webhook - '/webhook' from acceptor api")

    body = await request.json()

    logger.info("Completed post webhook - '/webhook' from acceptor api")
    return await main.process_incoming_message(body)
