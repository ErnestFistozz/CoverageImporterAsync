import asyncio
from src.utils import Utils
from src.codecov import CodeCovCoverage
from src.coveralls import CoverallsCoverage
from src.coverageimporter import CoverallsCoverageImporter
from src.coverageimporter import CodecovCoverageImporter
from src.coveralls_logger import CoverallsCoverageLogger
from src.codecov_logger import CodecovCoverageLogger

if __name__ == '__main__':
    repositories = Utils.repositories('common_repos.txt')
    coveralls_logger = CoverallsCoverageLogger()
    codecov_logger = CodecovCoverageLogger()

    for repo in repositories:
        coveralls = CoverallsCoverage(repo[0], repo[1], coveralls_logger)
        codecov = CodeCovCoverage(repo[0], repo[1], codecov_logger)

        coverall_importer = CodecovCoverageImporter(codecov)
        codecov_importer = CoverallsCoverageImporter(coveralls)

        codecov_data = asyncio.get_event_loop().run_until_complete(coverall_importer.analyze_commits())
        coveralls_data = asyncio.get_event_loop().run_until_complete(codecov_importer.analyze_commits())
        try:
            Utils.save_into_file('FinalCoverallsCommonAsyncResults.csv', coveralls_data)
        except Exception as err:
            print(f'Error with saving data for Coveralls, {err}')
            continue
        try:
            Utils.save_into_file('FinalCodeCovCommonAsyncResults.csv', codecov_data)
        except Exception as er:
            print(f'Error with saving data for Codecov, {er}')
            continue
