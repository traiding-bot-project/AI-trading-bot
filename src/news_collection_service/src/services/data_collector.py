"""Data collection logic for the News Collection service."""

import asyncio
import logging
import time
from collections.abc import AsyncGenerator, Callable
from typing import Any, cast

import httpx
from httpx import Response

from src.constants import (
    DATA_COLLECTOR_DOMAIN_DELAY_SECONDS,
    DATA_COLLECTOR_SLEEP_SECONDS,
    SERVICE_CLIENT_SESSION_TIMEOUT,
)
from src.models.collection_targets import CollectionTarget, DataSourceMetadata, NewsItem
from src.parsers import get_parser
from src.settings import settings
from src.settings.models.settings_model import DatasourceConfig, DatasourceType

logger = logging.getLogger(__name__)


class DataCollectorService:
    """Core logic for collecting news from various datasources."""

    def __init__(self) -> None:
        """Initialize the DataCollector."""
        self.visited_urls: set[str] = set()
        self.domain_last_fetched: dict[str, float] = {}
        self.client = httpx.AsyncClient(timeout=SERVICE_CLIENT_SESSION_TIMEOUT, follow_redirects=True)
        self.targets_by_domain: dict[str, list[CollectionTarget]] = self._build_targets_by_domain()

        total_targets = sum(len(t) for t in self.targets_by_domain.values())
        logger.info(
            f"Initialized DataCollector with {total_targets} feed target(s) "
            f"across {len(self.targets_by_domain)} domain(s)."
        )

    def _build_targets_by_domain(self) -> dict[str, list[CollectionTarget]]:
        """Build collection targets from settings, grouped by domain."""
        targets_by_domain: dict[str, list[CollectionTarget]] = {}

        for region_name, region_config in settings.datasource:
            for source_name, source_metadata in region_config:
                source_metadata = cast(DatasourceConfig, source_metadata)

                for category in source_metadata.available_categories:
                    target = CollectionTarget(
                        url=self._build_feed_url(
                            source_metadata.url_schema,
                            source_metadata.domain,
                            source_metadata.data_route,
                            category,
                            source_metadata.endpoint,
                        ),
                        domain=source_metadata.domain,
                        datasource_type=source_metadata.type,
                        category=category,
                        ignore_routes=source_metadata.ignore_routes,
                        metadata=DataSourceMetadata(
                            name=source_name,
                            language=source_metadata.language,
                            region=region_name,
                        ),
                    )
                    targets_by_domain.setdefault(source_metadata.domain, []).append(target)

        return targets_by_domain

    def _build_feed_url(
        self,
        url_schema: str,
        domain: str,
        data_route: str,
        category: str,
        endpoint: str | None,
    ) -> str:
        """Helper method to construct an RSS feed URL."""
        url = f"{url_schema}://{domain}/{data_route}/{category}{f'{endpoint}' if endpoint else ''}"
        return url

    def _get_content_type_config(
        self, content_type: DatasourceType
    ) -> tuple[dict[str, str], Callable[[Response], Any]]:
        """Return the appropriate headers and response handler based on the datasource type."""
        browser_headers = {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/91.0.4472.124 Safari/537.36"
            ),
        }
        content_type_mapping: dict[DatasourceType, tuple[dict[str, str], Callable[[Response], Any]]] = {
            DatasourceType.API: (
                browser_headers | {"Accept": "application/json"},
                (lambda r: r.json()),
            ),
            DatasourceType.RSS: (
                browser_headers | {"Accept": "application/rss+xml, application/xml, text/xml"},
                (lambda r: r.text),
            ),
            DatasourceType.TEXT: (
                browser_headers | {"Accept": "text/plain, text/html"},
                (lambda r: r.text),
            ),
            DatasourceType.TEXT: (
                browser_headers | {"Accept": "text/plain, text/html"},
                (lambda r: r.text),
            ),
        }
        return content_type_mapping[content_type]

    async def _send_get_request(self, url: str, content_type: DatasourceType = DatasourceType.API) -> Any:
        """Helper method to send a GET request and return the JSON response."""
        logger.debug(f"Sending GET request to: {url}")
        headers, response_handler = self._get_content_type_config(content_type)
        response = await self.client.get(url, headers=headers)
        try:
            response.raise_for_status()
        except httpx.HTTPStatusError as e:
            logger.error(f"GET request to {url} failed with status {e.response.status_code}: {e}")
            raise RuntimeError(f"Request to {url} failed: {e}")
        logger.debug("GET request successful")
        return response_handler(response)

    async def _fetch_rss_feed(self, target: CollectionTarget) -> list[NewsItem]:
        """Fetch and parse a specific feed target."""
        logger.debug(f"Fetching feed: {target.url}")
        parser = get_parser(target.datasource_type)
        try:
            feed_data = await self._send_get_request(target.url, content_type=target.datasource_type)
            items = parser.parse(feed_data, target)
            logger.debug(f"Parsed {len(items)} items from feed {target.url}")
            return items
        except Exception as e:
            logger.error(f"Failed to fetch or parse feed {target.url}: {e}")
            return []

    async def _fetch_raw_content(self, url: str) -> str | None:
        """Fetch the raw content from the page."""
        logger.debug(f"Fetching raw content: {url}")
        try:
            response: str = await self._send_get_request(url, content_type=DatasourceType.TEXT)
            return response
        except Exception as e:
            logger.error(f"Failed to fetch raw content from {url}: {e}")
            return None

    def _get_ready_domains(self) -> dict[str, list[CollectionTarget]]:
        """Return targets grouped by domain, filtered to domains past the delay window."""
        now = time.time()
        return {
            domain: targets
            for domain, targets in self.targets_by_domain.items()
            if now - self.domain_last_fetched.get(domain, 0) >= DATA_COLLECTOR_DOMAIN_DELAY_SECONDS
        }

    async def _process_feed_item(self, item: NewsItem) -> NewsItem:
        """Mark item as visited, fetch its article content, and return the populated item."""
        self.visited_urls.add(item.link)
        logger.info(f"New item found: {item.title} ({item.link})")
        item.raw_content = await self._fetch_raw_content(item.link)
        return item

    async def _poll_domain(self, domain: str, targets: list[CollectionTarget]) -> AsyncGenerator[NewsItem]:
        """Fetch all targets for a domain concurrently, then yield any unseen items."""
        logger.info(f"Polling {len(targets)} target(s) for domain '{domain}'")
        results: list[list[NewsItem] | BaseException] = await asyncio.gather(
            *[self._fetch_rss_feed(t) for t in targets],
            return_exceptions=True,
        )

        for target, result in zip(targets, results):
            if isinstance(result, BaseException):
                logger.error(f"Feed fetch failed for {target.url}: {result}")
                continue
            for item in result:
                if item.link not in self.visited_urls:
                    if any(f"/{route}" in item.link for route in target.ignore_routes):
                        self.visited_urls.add(item.link)
                        logger.debug(f"Ignoring item based on route: {item.title} ({item.link})")
                        continue
                    yield await self._process_feed_item(item)

    async def monitor(self) -> AsyncGenerator[NewsItem]:
        """Infinite generator that continuously polls all datasources and yields new items."""
        logger.info("Starting infinite data collection loop...")

        while True:
            ready_domains = self._get_ready_domains()

            if not ready_domains:
                await asyncio.sleep(DATA_COLLECTOR_SLEEP_SECONDS)
                continue

            now = time.time()
            for domain in ready_domains:
                self.domain_last_fetched[domain] = now

            for domain, targets in ready_domains.items():
                async for item in self._poll_domain(domain, targets):
                    yield item
