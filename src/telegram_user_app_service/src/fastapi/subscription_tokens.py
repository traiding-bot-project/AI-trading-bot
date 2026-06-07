"""FastAPI router for subscription token management."""

import logging
from typing import Annotated, Any

from fastapi import APIRouter, Depends, Path, status
from market_intel_lib.db import get_subscription_token_service
from market_intel_lib.db.subscriptions.subscription_token_service import (
    SubscriptionTokenService,
)
from src.models.fastapi.app import V1RouterTags
from src.models.subscription_token import SubscriptionToken

logger = logging.getLogger(__name__)

subscription_router = APIRouter(
    prefix="/token", tags=[V1RouterTags.SUBSCRIPTION_SERVICE]
)


@subscription_router.get(
    "/", response_model=SubscriptionToken, status_code=status.HTTP_201_CREATED
)
async def create_subscription_token(
    token_service: Annotated[
        SubscriptionTokenService, Depends(get_subscription_token_service)
    ],
) -> Any:
    """Create a new subscription token for a Telegram chat ID."""
    logger.info("GET /token - Creating subscription token")
    token = await token_service.create_token()
    logger.info("Token created successfully")
    return SubscriptionToken.model_validate(token)


@subscription_router.get(
    "/list", response_model=list[SubscriptionToken], status_code=status.HTTP_200_OK
)
async def list_subscription_tokens(
    token_service: Annotated[
        SubscriptionTokenService, Depends(get_subscription_token_service)
    ],
) -> Any:
    """List all subscription tokens."""
    logger.info("GET /token/list - Listing all subscription tokens")
    tokens = await token_service.list_tokens()
    return tokens


@subscription_router.get(
    "/{username}",
    response_model=list[SubscriptionToken],
    status_code=status.HTTP_200_OK,
)
async def get_subscription_token_by_username(
    username: Annotated[
        str,
        Path(
            ...,
            embed=True,
            title="Telegram Username",
            description="The Telegram username to list tokens for.",
        ),
    ],
    token_service: Annotated[
        SubscriptionTokenService, Depends(get_subscription_token_service)
    ],
) -> Any:
    """List subscription tokens created for a given chat ID."""
    logger.info("GET /token - Listing all subscription tokens")
    tokens = await token_service.list_tokens_for_username(username)
    return tokens
