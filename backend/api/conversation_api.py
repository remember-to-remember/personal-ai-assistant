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

app = (
    FastAPI(
        title="Personal AI Assistant API",
    )
    if config.CONFIG
    else FastAPI()
)


@app.get("/")
async def get_root() -> dict[str, str]:
    """Get root path."""

    logger = get_logger()
    logger.info("Starting get root path - '/' from conversation api")
    logger.info("Completed get root path - '/' from conversation api")

    return {"msg": "Welcome to the Personal AI Assistant API!"}


# async def get_caller(
#     api_key_header: str = Security(APIKeyHeader(name="WEBHOOK_VERIFY_TOKEN")),
# ) -> Caller:
#     caller = main.get_caller(api_key_header)
#     if caller:
#         return caller
#     raise HTTPException(
#         status_code=status.HTTP_401_UNAUTHORIZED,
#         detail="Missing or invalid webhook verify token!",
#     )


async def decode_jwt(token: str, required_permission: str) -> str:
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


async def get_caller(
    token: str = Depends(OAuth2PasswordBearer(tokenUrl="token")),
) -> Caller:
    """Get caller from token."""

    idp_id = await decode_jwt(token, "access:chat")
    caller = await main.get_caller(idp_id=idp_id)
    if caller:
        return caller

    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid token",
        headers={"WWW-Authenticate": "Bearer"},
    )


@app.post("/chat")
async def post_chat(
    chat_input: ChatInputModel, caller: Annotated[Caller, Depends(get_caller)]
) -> str:
    """Post chat."""

    logger = get_logger()
    logger.info("Starting post chat - '/chat' from conversation api")

    chat_output = await main.process_chat(chat_input, caller)

    logger.info("Completed post chat - '/chat' from conversation api")
    return chat_output


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
async def post_webhook(request: Request) -> dict[str, str]:
    """Post webhook."""

    logger = get_logger()
    logger.info("Starting post webhook - '/webhook' from conversation api")

    body = await request.json()

    logger.info("Completed post webhook - '/webhook' from conversation api")
    return await main.process_incoming_message(body)


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
