import asyncio

from src.utils import Utils
from src.codecov import CodeCovCoverage
from src.codecov_logger import CodecovCoverageLogger
from src.coverageimporter import CodecovCoverageImporter
from src.codecov_repositories import CodeCovRepositories

orgs =  [
    'yelp', 'cfpb', 'square', 'didi', 'Esri', 'godaddy',
    'kubernetes', 'cloudflare', 'facebook', 'alibaba',
]
# 'ibm', 'apache', 'microsoft', 'adobe',

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    codecov_loger = CodecovCoverageLogger()
    for org in orgs:
        repo = CodeCovRepositories(org)
        repositories = loop.run_until_complete(repo.repositories())
        for active_repo in repositories:
            repo_name = active_repo['name']
            codecov = CodeCovCoverage(org, repo_name, codecov_loger)
            codecov_importer = CodecovCoverageImporter(codecov)
            codecov_data = loop.run_until_complete(codecov_importer.analyze_commits())
            try:
                Utils.save_into_file('FinalCodecovOrganisationAsyncResults.csv', codecov_data)
            except Exception as err:
                print(f'failed to save Codecov data: error - {err}')
                continue
