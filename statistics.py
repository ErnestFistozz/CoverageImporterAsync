import asyncio
import aiohttp
from typing import Optional
from dataclasses import dataclass
from typing import Union
from github import Github
from src.basecoverage import BaseCoverage
from src.utils import Utils

@dataclass
class ProjectKeyStatistics:
    StartSize: Optional[int] = 0
    total_builds: Optional[int] = 1  # total number of builds
    language: Optional[str] = None  # might have to exclude
    EndSize: Optional[int] = 0
    StartCoverage: Optional[float] = 0
    EndCoverage: Optional[float] = 0

class CoverallsStats(BaseCoverage):
    def __init__(self, org, repo) -> None:
        super().__init__(org, repo)

    async def total_builds_pages(self):
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
                    return await response.json()
        except Exception as err:
            print(err)
            return 0

    async def fetch_coveralls_page_data(self, page: int):
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
                        data = await res.json()
                        return data
        except Exception as err:
            print(str(err))
            return {}


class CodecovSts(BaseCoverage):
    def __init__(self, org, repo) -> None:
        super().__init__(org, repo)

    async def codecov_project(self, page: int):
        url = f'https://codecov.io/api/v2/gh/{self.organisation}/repos/{self.repository}/commits?page={page}'
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as res:
                    res.raise_for_status()
                    data = await res.json()
                    if not data:
                        return 0
                    return data
        except Exception as error:
            return {}


async def get_repository_details(gh_instance: Github, coverage_tool: Union[CoverallsStats, CodecovSts]) -> str:
    repository_language = gh_instance.get_organization(coverage_tool.organisation).get_repo(
        coverage_tool.repository).language
    return repository_language

async def main_codecov(gh: Github, codecov_sts: CodecovSts):
    build_res = await codecov_sts.codecov_project(1)
    if build_res:
        total_builds = build_res['count']  # number of builds
        end_coverage = build_res['results'][0]['totals']['coverage']  # last coverage point
        end_size = build_res['results'][0]['totals']['lines']  # last LOC

        total_pages = build_res['total_pages']  # number of pages
        earlier_res = await codecov_sts.codecov_project(total_pages)
        earlier_builds = earlier_res['results']
        start_coverage = earlier_builds[len(earlier_builds) - 1]['totals']['coverage']
        start_size = earlier_builds[len(earlier_builds) - 1]['totals']['lines']
        language = await get_repository_details(gh, codecov_sts)
        return ProjectKeyStatistics(StartSize=start_size,
                                    total_builds=total_builds,
                                    language=language,
                                    EndSize=end_size,
                                    StartCoverage=start_coverage,
                                    EndCoverage=end_coverage)

async def main_coveralls(gh: Github, coveralls_sts: CoverallsStats):
    build_res = await coveralls_sts.total_builds_pages()
    await asyncio.sleep(5)
    if build_res:
        total_builds = build_res['total']  # number of builds
        end_coverage = build_res['builds'][0]['covered_percent']  # last coverage point
        end_size = build_res['builds'][0]['relevant_lines']  # last LOC
        total_pages = build_res['pages']  # number of pages
        earlier_res = await coveralls_sts.fetch_coveralls_page_data(total_pages)
        earlier_builds = earlier_res['builds']
        start_coverage = earlier_builds[len(earlier_builds) - 1]['covered_percent']
        start_size = earlier_builds[len(earlier_builds) - 1]['relevant_lines']
        language = await get_repository_details(gh, coveralls_sts)
        return ProjectKeyStatistics(StartSize=start_size,
                                    total_builds=total_builds,
                                    language=language,
                                    EndSize=end_size,
                                    StartCoverage=start_coverage,
                                    EndCoverage=end_coverage)
async def coveralls_wrapper(projects: list) -> list:
    data = []
    if projects:
        gh_instance = Github()
        tasks = []
        for repo in projects:
            project = CoverallsStats(repo[0], repo[1])
            task = asyncio.create_task(main_coveralls(gh_instance, project))
            tasks.append(task)
        data.extend(await asyncio.gather(*tasks))
        flat_data = [item for sublist in data for item in sublist if item is not None]
        return flat_data
    return data

async def codecov_wrapper(projects: list) -> list:
    data = []
    if projects:
        gh_instance = Github()
        tasks = []
        for repo in projects:
            project = CodecovSts(repo[0], repo[1])
            task = asyncio.create_task(main_codecov(gh_instance, project))
            tasks.append(task)
        data.extend(await asyncio.gather(*tasks))
        flat_data = [item for sublist in data for item in sublist if item is not None]
        return flat_data
    return data

if __name__ == '__main__':
    repositories = Utils.repositories('earlier_coveralls_projects.txt')
    coveralls_data = asyncio.get_event_loop().run_until_complete(coveralls_wrapper(repositories))
    print(coveralls_data)

