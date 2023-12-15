import asyncio
import aiohttp
from src.basecoverage import BaseCoverage
import json

class CodeCovCoverage(BaseCoverage):

    def __init__(self, organisation: str, repository: str) -> None:
        super().__init__(organisation, repository)

    async def total_builds_pages(self) -> int:
        url = f'https://codecov.io/api/v2/gh/{self.organisation}/repos/{self.repository}/commits'
        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(url, verify_ssl=False) as res:
                    res.raise_for_status()
                    data = await res.json()
                    return data.get('total_pages')
            except (aiohttp.ClientError, json.JSONDecodeError, KeyError) as e:
                print(e)
                return 0
            except Exception:
                return 0

    async def collect_build_data(self) -> list:
        data = []
        builds_pages = await self.total_builds_pages()
        if builds_pages != 0:
            tasks = []
            for page in range(1, builds_pages + 1):
                task = asyncio.create_task(self._fetch_build_data(page))
                tasks.append(task)
        data.extend(await asyncio.gather(*tasks))
        flat_data = [item for sublist in data for item in sublist]
        return flat_data

    async def _fetch_build_data(self, page: int) -> list:
        url = f'https://codecov.io/api/v2/gh/{self.organisation}/repos/{self.repository}/commits?page={page}'
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, verify_ssl=False) as res:
                    res.raise_for_status()
                    return [
                        {
                            'created_at': build['timestamp'],
                            'commit_sha': build['commitid'],
                            'covered_percent': round(build['totals']['coverage'], 3),
                            'branch': build['branch']
                        }
                        for build in (await res.json()).get('results', [])
                    ]
        except (aiohttp.ClientError, json.JSONDecodeError, KeyError, RuntimeError) as e:
            print(f"Error in fetch_build_data for page {page}: {e}")
            return []
        except Exception:
            return []

    async def commit_report(self, commit_hash: str):
        wait_time = 360
        try:
            url = f'https://codecov.io/api/v2/gh/{self.organisation}/repos/{self.repository}/report?sha={commit_hash}'
            async with aiohttp.ClientSession() as session:
                async with session.get(url, verify_ssl=False) as res:
                    res.raise_for_status()
                    if res.status != 200:
                        if res.status in [403, 429]:
                            await asyncio.sleep(wait_time)
                            async with session.get(url, verify_ssl=False) as res_retry:
                                res = res_retry
                        else:
                            raise Exception
                    return await res.json()
        except Exception as e:
            print(e)
            return {}

    @staticmethod
    def api_patch_coverage(commit_details: dict) -> float:
        if commit_details:
            try:
                if not isinstance(commit_details['totals']['diff'], type(None)):
                    if isinstance(commit_details['totals']['diff'], list):
                        if not isinstance(commit_details['totals']['diff'][5], type(None)):
                            return float(commit_details['totals']['diff'][5])
            except (KeyError, TypeError) as e:
                return 0
        return 0

    @staticmethod
    def computed_overall_coverage(commit_details: dict) -> float:
        if commit_details:
            try:
                source_files = commit_details['files']
                executable_lines = covered_lines = 0
                for file in source_files:
                    for file_line_coverage in file['line_coverage']:
                        if file_line_coverage[1] == 0:
                            covered_lines += 1
                    executable_lines += len(file['line_coverage'])
                if executable_lines == 0:
                    return 0
                else:
                    return round((covered_lines / executable_lines) * 100, 3)
            except Exception as e:
                return 0
        return 0

    @staticmethod
    def file_line_coverage_array(commit_details: dict, filename: str) -> list:
        if commit_details:
            try:
                data = [tuple(line_coverage) for file in commit_details['files'] if
                        file['name'].lower() == filename.lower() for line_coverage in file['line_coverage']]
                return data
            except Exception as e:
                return []
        return []

    @staticmethod
    def fetch_source_file_names(commit_details: dict) -> list:
        if commit_details:
            try:
                files = commit_details['files']
                full_file_names = [file['name'].lower() for file in files]
                return full_file_names
            except Exception as e:
                return []
        return []


