import asyncio
from src.coveralls import CoverallsCoverage
from src.coverageimporter import CoverageImporter
from src.codecov import CodeCovCoverage
from src.utils import Utils

if __name__ == '__main__':
    common_repos = Utils.repositories('common_repos.txt')
    coverage_importer = CoverageImporter()

    for repo in common_repos:
        coveralls = CoverallsCoverage(repo[0], repo[1])
        coveralls_data = asyncio.get_event_loop().run_until_complete(
            coverage_importer.analyze_coveralls_commits(coveralls))
        Utils.save_into_file('FinalCommonCoverallsAsyncResults.csv', coveralls_data)

    for repo in common_repos:
        codecov = CodeCovCoverage(repo[0], repo[1])
        codecov_data = asyncio.get_event_loop().run_until_complete(
            coverage_importer.analyze_codecov_commits(codecov))
        Utils.save_into_file('FinalCommonCodeCovAsyncResults.csv', codecov_data)
