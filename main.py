import asyncio
from src.coveralls import CoverallsCoverage
from src.coverageimporter import CoverallsCoverageImporter, CodecovCoverageImporter
from src.codecov import CodeCovCoverage
from src.utils import Utils
from src.codecov_logger import CodecovCoverageLogger
from src.coveralls_logger import  CoverallsCoverageLogger

if __name__ == '__main__':
    common_repos = Utils.repositories('common_repos.txt')
    coveralls_loger = CoverallsCoverageLogger()
    codecov_loger = CodecovCoverageLogger()

    for repo in common_repos:
        coveralls = CoverallsCoverage(repo[0], repo[1], coveralls_loger)
        coveralls_importer = CoverallsCoverageImporter(coveralls)
        coveralls_data = asyncio.get_event_loop().run_until_complete(
            coveralls_importer.analyze_commits())
        try:
            Utils.save_into_file('FinalCommonCoverallsAsyncResults.csv', coveralls_data)
        except Exception as err:
            print(f'failed to save Coveralls data: error {err}')
            continue

    for repo in common_repos:
        codecov = CodeCovCoverage(repo[0], repo[1], codecov_loger)
        codecov_importer = CodecovCoverageImporter(codecov)
        codecov_data = asyncio.get_event_loop().run_until_complete(
            codecov_importer.analyze_commits())
        try:
            Utils.save_into_file('FinalCommonCodeCovAsyncResults.csv', codecov_data)
        except Exception as err:
            print(f'failed to save Codecov data: error - {err}')
            continue
