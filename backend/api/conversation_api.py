""" Module for conversation api. """

from typing import Annotated

import uvicorn
from authlib.jose import JoseError, JsonWebKey, jwt
from authlib.jose.errors import ExpiredTokenError
from fastapi import Depends, FastAPI, HTTPException, Request, Security, status
from fastapi.responses import PlainTextResponse
from fastapi.security import OAuth2PasswordBearer

# from fastapi.security import APIKeyHeader
from structlog import get_logger

from backend.api import config, main
from backend.api.entities import Caller, ChatInputModel


def init() -> None:
    """Entry point if called as an executable."""

    logger = get_logger()
    logger.info("Starting init from conversation api")

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
        "backend.api.conversation_api:app",
        host="0.0.0.0",
        port=config.CONFIG.conversation_api_port,
        reload=config.CONFIG.conversation_api_reload,
        log_level="debug" if config.CONFIG.debug_mode else "info",
        ssl_certfile="certs/api.remember2.co/fullchain.pem",
        ssl_keyfile="certs/api.remember2.co/privkey.pem",
    )

    logger.info("Completed init from conversation api")


if __name__ == "__main__":
    init()


app = FastAPI(
    title="Personal AI Assistant API",
)


@app.get("/")
async def get_root() -> dict[str, str]:
    """Get root path."""

    logger = get_logger()
    logger.info("Starting get root path - '/' from conversation api")
    logger.info("Completed get root path - '/' from conversation api")

    return {"msg": "Welcome to the Whatsapp API!"}


# def get_caller(
#     api_key_header: str = Security(APIKeyHeader(name="WEBHOOK_VERIFY_TOKEN")),
# ) -> Caller:
#     caller = main.get_caller(api_key_header)
#     if caller:
#         return caller
#     raise HTTPException(
#         status_code=status.HTTP_401_UNAUTHORIZED,
#         detail="Missing or invalid webhook verify token!",
#     )


def decode_jwt(token: str, required_permission: str) -> str:
    """Decode JWT token and check for required permission."""

    try:
        payload = jwt.decode(
            token,
            JsonWebKey.import_key(config.CONFIG.auth0_public_key, {"kty": "RSA"}),
            claims_options={
                "iss": {"essential": True, "value": config.CONFIG.auth0_issuer},
                "aud": {"essential": True, "value": config.CONFIG.auth0_audience},
            },
        )
        payload.validate()

        permissions = payload.get("permissions", [])
        if required_permission not in permissions:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Permission denied",
            )

        return payload.sub
    except ExpiredTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except JoseError as error:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid token error: {error}",
            headers={"WWW-Authenticate": "Bearer"},
        )


def get_caller(
    token: str = Depends(OAuth2PasswordBearer(tokenUrl="token")),
) -> Caller:
    """Get caller from token."""

    try:
        token, email = token.split(":")
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token format",
            headers={"WWW-Authenticate": "Bearer"},
        )

    idp_id = decode_jwt(token, "access:chat")

    caller = main.get_caller(idp_id=idp_id)
    if caller and caller.email == email:
        return caller

    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid token",
        headers={"WWW-Authenticate": "Bearer"},
    )


@app.post("/chat")
async def post_chat(
    chat_input: ChatInputModel, caller: Annotated[Caller, Depends(get_caller)]
) -> dict[str, str]:
    """Post chat."""

    logger = get_logger()
    logger.info("Starting post chat - '/chat' from conversation api")

    chat_output = main.process_chat(chat_input, caller)

    logger.info("Completed post sync - '/chat' from conversation api")
    return {
        k: str(v)
        for k, v in chat_output.__dict__.items()
        if k
        in (
            "job_id",
            "caller_id",
            "caller_job_id",
            "status",
            "response_content_url",
            "start_time",
            "end_time",
            "total_duration_seconds",
        )
    }


@app.get("/webhook", response_class=PlainTextResponse)
async def get_webhook(request: Request) -> str:
    """Get webhook."""

    logger = get_logger()
    logger.info("Starting get webhook - '/webhook' from conversation api")

    body = dict(request.query_params)
    response = await main.process_initial_connection(body)

    logger.info("Completed get webhook - '/webhook' from conversation api")
    if response:
        return response
    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")


@app.post("/webhook")
async def webhook_handler(request: Request):
    """Post webhook."""

    logger = get_logger()
    logger.info("Starting post webhook - '/webhook' from conversation api")

    body = await request.json()

    logger.info("Completed post webhook - '/webhook' from conversation api")
    return await main.process_incoming_message(body)
