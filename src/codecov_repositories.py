from .basecoverage import BaseCoverage
import aiohttp
import urllib3
import json

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class CodeCovRepositories(BaseCoverage):
    def __init__(self, organisation: str, repository=None):
        super().__init__(organisation, repository)

    '''
    method to retrieve the total number of pages from codecov
    uses the codecov repository API (which expects an organisation name or username)
    username/organisation name is instantiated with object creation

    @return <int> total number of pages --> each page contains 10 repositories
    '''

    async def get_total_pages(self) -> int | None:
        async with aiohttp.ClientSession() as session:
            try:
                url = f'https://codecov.io/api/v2/gh/{self.organisation}/repos?active=true'
                async with session.get(url, verify_ssl=False) as res:
                    res.raise_for_status()
                    return (await res.json())['total_pages']
            except (aiohttp.ClientError, json.JSONDecodeError, KeyError):
                return None

    '''
        method to retrieve all repositories
        iterates all pages based on the get_total_pages method above
        @return dict {
        name --> repository name
        language --> language of which the repository is written in 
        branch --> main branch (default branch), whilst the main branch can be any other branch other than main/master
            we assume main/master represent production code
        organisation --> this is the organisation or username 
        }
    '''

    async def repositories(self) -> list:
        pages = await self.get_total_pages()
        data = []
        async with aiohttp.ClientSession() as session:
            if pages != 0 and pages is not None:
                for page in range(1, pages + 1):
                    try:
                        url = f'https://codecov.io/api/v2/gh/{self.organisation}/repos?active=true&page={page}'
                        async with session.get(url, verify_ssl=False) as res:
                            res.raise_for_status()
                            data.extend(
                                [{
                                    "name": repos['name'],
                                    "language": repos['language'],
                                    "branch": repos['branch'],
                                    "organisation": repos['author']['username']
                                }
                                    for repos in (await res.json())['results']])
                    except (aiohttp.ClientError, json.JSONDecodeError, KeyError, RuntimeError):
                        continue
            return data


if __name__ == '__main__':
    codecov = CodeCovRepositories('apache')
