import asyncio
from src.coveralls import CoverallsCoverage
from src.coverageimporter import CoverageImporter
from src.utils import Utils

if __name__ == '__main__':
    codecov_repositories = Utils.repositories('coveralls_repos.txt')
    for coveralls_repo in codecov_repositories:
        coverage_importer = CoverageImporter()
        coveralls = CoverallsCoverage(coveralls_repo[0], coveralls_repo[1])
        coveralls_data = asyncio.get_event_loop().run_until_complete(
            coverage_importer.analyze_coveralls_commits(coveralls))
        Utils.save_into_file('FinalCodeCovAsyncResults.csv', coveralls_data)