from abc import ABC, abstractmethod

import aiohttp
import asyncio

from .basecoverage import BaseCoverage


class CoverageRepository(BaseCoverage, ABC):
    def __init__(self, organisation: str, repository=None):
        super().__init__(organisation, repository)
        self.repo_names = []
    @abstractmethod
    async def get_total_pages(self) -> int:
        pass

    @abstractmethod
    async def _fetch_repo_names(self, session, page):
        pass

    @abstractmethod
    async def repositories(self) -> list:
        start_page = 1
        total_pages = await self.get_total_pages()
        async with aiohttp.ClientSession() as session:
            tasks = [self._fetch_repo_names(session, page) for page in range(start_page, total_pages + 1)]
            await asyncio.gather(*tasks)
        return self.repo_names

