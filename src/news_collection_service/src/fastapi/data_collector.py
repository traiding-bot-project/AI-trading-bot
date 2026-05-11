"""FastAPI router for handling Ollama API interactions."""

import asyncio
import json
import logging
from collections.abc import AsyncGenerator
from typing import Annotated

from fastapi.responses import StreamingResponse

from fastapi import APIRouter, Query, status
from src.models.fastapi.app import V1RouterTags
from src.parsers.article_parser import ArticleParser
from src.services.data_collector import DataCollectorService

logger = logging.getLogger(__name__)

data_collector_router = APIRouter(prefix="/data-collector", tags=[V1RouterTags.DATA_COLLECTOR])


@data_collector_router.get(
    "/monitor",
    response_class=StreamingResponse,
    status_code=status.HTTP_200_OK,
)
async def monitor(
    limit: Annotated[int, Query(gt=0, description="Stop after this many items.")] = 100,
) -> StreamingResponse:
    """Endpoint to monitor the data collection process and stream parsed news items as NDJSON."""

    async def generate() -> AsyncGenerator[str]:
        collector = DataCollectorService()
        article_parser = ArticleParser()
        item_count = 0

        async for item in collector.monitor():
            item = article_parser.parse(item)
            item_count += 1

            payload = {
                "count": item_count,
                "source": f"{item.metadata.region}/{item.metadata.name}",
                "title": item.title,
                "url": item.link,
                "date": item.pub_date,
                "raw_content_chars": len(item.raw_content or ""),
                "prepared_content_chars": len(item.prepared_content or ""),
                "extraction_method": item.metadata.extraction_method,
            }

            logger.info(f"[{item_count}/{limit}] {payload['source']} — {item.title}")
            yield json.dumps(payload, ensure_ascii=False) + "\n"
            await asyncio.sleep(0)

            if item_count >= limit:
                break

    return StreamingResponse(generate(), media_type="application/x-ndjson")
