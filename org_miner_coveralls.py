import asyncio

from src.utils import Utils
from src.coveralls import CoverallsCoverage
from src.coveralls_logger import CoverallsCoverageLogger
from src.coverageimporter import CoverallsCoverageImporter
from src.coveralls_repositories import CoverallsRepository

orgs = [
    'OSGeo', 'Esri', 'cloudflare', 'kubernetes', 'godaddy',
    'imb', 'square', 'yelp', 'cfpb', 'facebook', 'alibaba',
]
# 'apache', 'microsoft', 'adobe',

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    coveralls_loger = CoverallsCoverageLogger()
    user_agent = {
        "User-Agent": 'Linux PC/Firefox browser: Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:15.0) Gecko/20100101 '
                      'Firefox/15.0.1'}
    for org in orgs:
        repo = CoverallsRepository(org, request_headers=user_agent)
        repositories = loop.run_until_complete(repo.repositories())

        for active_repo in repositories:
            repo_name = active_repo
            coveralls = CoverallsCoverage(org, repo_name, coveralls_loger)
            coveralls_importer = CoverallsCoverageImporter(coveralls)
            coveralls_data = loop.run_until_complete(coveralls_importer.analyze_commits())
            try:
                Utils.save_into_file('FinalCoverallsOrganisationAsyncResults.csv', coveralls_data)
            except Exception as err:
                print(f'failed to save Coveralls data: error - {err}')
                continue
