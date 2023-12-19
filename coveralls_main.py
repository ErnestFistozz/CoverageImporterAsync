import asyncio
from src.coveralls import CoverallsCoverage
from src.coverageimporter import CoverallsCoverageImporter
from src.utils import Utils
from src.coveralls_logger import CoverallsCoverageLogger

if __name__ == '__main__':
    coveralls_repositories = Utils.repositories('coveralls_repos.txt')
    logger = CoverallsCoverageLogger()

    for coveralls_repo in coveralls_repositories:
        coveralls = CoverallsCoverage(coveralls_repo[0], coveralls_repo[1], logger)
        coverage_importer = CoverallsCoverageImporter(coveralls)
        coveralls_data = asyncio.get_event_loop().run_until_complete(
            coverage_importer.analyze_commits())
        try:
            Utils.save_into_file('FinalCoverallsAsyncResults.csv', coveralls_data)
        except Exception as err:
            print(f'Error with saving data for Coveralls, {err}')
            continue