import asyncio
from src.coverageimporter import CodecovCoverageImporter
from src.codecov import CodeCovCoverage
from src.utils import Utils
from src.codecov_logger import CodecovCoverageLogger

if __name__ == '__main__':
    codecov_repositories = Utils.repositories('codecov_repos.txt')
    logger = CodecovCoverageLogger()

    for codecov_repo in codecov_repositories:
        codecov = CodeCovCoverage(codecov_repo[0], codecov_repo[1], logger)
        coverage_importer = CodecovCoverageImporter(codecov)
        codecov_data = asyncio.get_event_loop().run_until_complete(
            coverage_importer.analyze_commits())
        try:
            Utils.save_into_file('FinalCodeCovAsyncResults.csv', codecov_data)
        except Exception as err:
            print(f'Error with saving data for Codecov, {err}')
            continue
