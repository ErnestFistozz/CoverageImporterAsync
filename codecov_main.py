import asyncio
from src.coverageimporter import CoverageImporter
from src.codecov import CodeCovCoverage
from src.utils import Utils

if __name__ == '__main__':
    codecov_repositories = Utils.repositories('codecov_repos.txt')
    for codecov_repo in codecov_repositories:
        coverage_importer = CoverageImporter()
        codecov = CodeCovCoverage(codecov_repo[0], codecov_repo[1])
        codecov_data = asyncio.get_event_loop().run_until_complete(
            coverage_importer.analyze_codecov_commits(codecov))
        Utils.save_into_file('FinalCodeCovAsyncResults.csv', codecov_data)
