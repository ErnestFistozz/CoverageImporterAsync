import asyncio
import aiohttp
from typing import List, Optional
from dataclasses import dataclass
from src.utils import Utils


@dataclass
class ProjectKeyStatistics:
    size: Optional[int] = 1
    builds: Optional[int] = 1
    language: Optional[str] = None  # might have to exclude
    annotation: Optional[str] = None
    statingCoverage:  Optional[float] = 0

async def coveralls_project(organisation: str, repository: str) -> ProjectKeyStatistics | None:
    url = f'https://coveralls.io/github/{organisation}/{repository}.json?page=1'
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, allow_redirects=False) as response:
                response.raise_for_status()
                data = await response.json()
                if not data:
                    return None
                return ProjectKeyStatistics(
                    data['relevant_lines'],
                    data['total'], language=None, annotation=None)  # Language will have to be retrived via GitHub API
    except (RuntimeError, aiohttp.ClientResponseError) as err:
        print(f'Error occured while trying to retrieved repository statistics: {str(err)}')
        return None


async def codecov_project(organisation: str, repository: str) -> ProjectKeyStatistics:
    url = f'https://codecov.io/api/v2/gh/{organisation}/repos/{repository}/commits'
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as res:
                res.raise_for_status()
                data = await res.json()
                if not data:
                    return None
                return ProjectKeyStatistics(
                    data['results'][0]['totals']['lines'],
                    data['count'],
                    language=None, annotation=None)
    except Exception as error:
        print(f'Error occured while trying to retrieve repository statistics: {str(error)}')


def statistics_formatter(repositories: List, filename='repositoryStats', common_repos=False) -> None:
    data = []
    if not common_repos:
        for project in repositories:
            coveralls_data = coveralls_project(project[0], project[1])
            codecov_data = coveralls_project(project[0], project[1])
            data.append(codecov_data)
            data.append(coveralls_data)
    Utils.save_into_file(filename, data)


if __name__ == '__main__':
    statistics_formatter([])  # save nothing to the file --> just create an empty placeholder
