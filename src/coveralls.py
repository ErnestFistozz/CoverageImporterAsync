import asyncio
import aiohttp
from src.basecoverage import BaseCoverage
import urllib3
import json
from src.utils import Utils

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class CoverallsCoverage(BaseCoverage):
    def __init__(self, organisation: str, repository: str) -> None:
        super().__init__(organisation, repository)

    async def total_builds_pages(self) -> int:
        url = f'https://coveralls.io/github/{self.organisation}/{self.repository}.json?page=1&per_page=10'
        wait_time = 600
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, verify_ssl=False) as response:
                    if response.status != 200:
                        if response.status in [403, 429]:
                            await asyncio.sleep(wait_time)
                            async with session.get(url) as retry_response:
                                response = retry_response
                        else:
                            raise Exception
                    return (await response.json())['pages']
        except Exception as e:
            return 0

    async def collect_builds_data(self) -> list:
        data = []
        builds_pages = await self.total_builds_pages()
        if builds_pages != 0:
            tasks = []
            for page in range(1, builds_pages + 1):
                task = asyncio.create_task(self._fetch_builds_data(page))
                tasks.append(task)
        data.extend(await asyncio.gather(*tasks))
        flat_data = [item for sublist in data for item in sublist]
        return flat_data

    async def _fetch_builds_data(self, page: int) -> list:
        wait_time: int = 600
        url = f'https://coveralls.io/github/{self.organisation}/{self.repository}.json?page={page}&per_page=10'
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, verify_ssl=False) as res:
                    if res.status != 200:
                        if res.status in [403, 429]:
                            await asyncio.sleep(wait_time)
                            async with session.get(url, verify_ssl=False) as res_retry:
                                res = res_retry
                        else:
                            raise Exception
                    return [
                        {
                            'created_at': Utils.date_formatter(build['created_at']),
                            'commit_sha': build['commit_sha'],
                            'covered_percent': round(build['covered_percent'], 3),
                            'branch': build['branch'],
                            'repository_name': build['repo_name']
                        }
                        for build in (await res.json()).get('builds', [])
                    ]
        except Exception as e:
            return []

    async def fetch_source_files(self, commit_hash: str) -> list:
        source_files = []
        file_url = f"https://coveralls.io/builds/{commit_hash}/source_files.json"
        wait_time = 600
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(file_url) as response:
                    if response.status != 200:
                        if response.status in [403, 429]:
                            await asyncio.sleep(wait_time)
                            async with session.get(file_url) as retry_response:
                                response = retry_response
                        else:
                            raise Exception
                    total_pages = (await response.json())['total_pages']
                    if total_pages > 1:
                        for page in range(1, total_pages + 1):
                            page_url = f'{file_url}?&page={page}'
                            page_response = await session.get(page_url)

                            try:
                                if page_response.status != 200:
                                    if page_response.status in [403, 429]:
                                        await asyncio.sleep(wait_time)
                                        page_response = await session.get(page_url)
                                    else:
                                        raise Exception
                                current_files = (await page_response.json())['source_files']
                                source_files.extend(
                                    file['name'] for file in json.loads(current_files))
                            except Exception:
                                continue
                            await asyncio.sleep(5)
                    else:
                        files = (await response.json())['source_files']
                        source_files.extend(
                            source_file['name'] for source_file in json.loads(files))
                    return source_files
        except Exception as e:
            return []

    async def source_coverage_array(self, commit: str,  filename: str) -> list:
        url = f'https://coveralls.io/builds/{commit}/source.json?filename={filename}'
        wait_time = 600
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, ssl=False) as response:
                    if response.status != 200:
                        if response.status in [403, 429]:
                            await asyncio.sleep(wait_time)
                            async with session.get(url, ssl=False) as retry_response:
                                response = retry_response
                    return await response.json()
        except Exception as e:
            return []