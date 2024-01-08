from .coverage_repository import CoverageRepository
from requests_html import HTML
import urllib3
import aiohttp

urllib3.disable_warnings()


class CoverallsRepository(CoverageRepository):

    def __init__(self, organisation: str, request_headers: dict, repository=None):
        super().__init__(organisation, repository)
        self.request_headers = request_headers

    '''
        Method total number of paginations representing ALL pages with repositories for that Organisation in coveralls
        Coveralls.IO currently does not have an API for retrive all repositories covered  per organisation
        In fact, they don't have the concept of an organisation at all

        @param <request_headers: str> --> currently requires headers (each computer has its own headers)
            I will have to remove this as the base methods do not have this signature
        @return <int> --> total number of pages representing all repositories configured to have coveralls
    '''

    async def get_total_pages(self) -> int:
        async with aiohttp.ClientSession() as session:
            url = f"https://coveralls.io/github/{self.organisation}?page=1"
            async with session.get(url) as res:
                if res.status == 200:
                    html_content = await res.text()
                    html = HTML(html=html_content)
                    page_elements = html.find('ul.pagination')
                    if len(page_elements) == 0 or page_elements is None:
                        return 1
                    else:
                        pagination = page_elements[0].find('a')
                        array_size = len(pagination)
                        length_elem = pagination[array_size - 2]
                        return int(length_elem.find('a')[0].text)
                return 0

    '''
        Method for scrapping repository names from organisation page in coveralls
        Based on the total number of paginations above, this will scrap each and retrieve the organisation
        name. Currently using requests_html for WebScrapping

        @param <request_headers: str> --> computer specific request headers
        @return <list> --> returns a list of all repository names
    '''

    async def _fetch_repo_names(self, session, page):
        url = f"https://coveralls.io/github/{self.organisation}?page={page}"
        async with session.get(url) as response:
            if response.status == 200:
                html_content = await response.text()
                html = HTML(html=html_content)
                page_elements = html.find('div.repoChartInfo')
                for repo in page_elements:
                    repository_name = repo.find('a')
                    if not repository_name:
                        continue
                    else:
                        try:
                            org_project_name = repository_name[1].find('a')
                            current_repo = org_project_name[0].text
                            self.repo_names.append(current_repo)
                        except Exception as err:
                            print(f'Exception occured, skipping page')
                            continue


if __name__ == '__main__':
    codecov = CoverallsRepository('kubernetes')
