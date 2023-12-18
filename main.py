import asyncio
from src.coveralls import CoverallsCoverage
from src.coverageimporter import CoverageImporter
from src.codecov import CodeCovCoverage
import csv


def save_into_file(filename: str, data: list) -> None:
    try:
        with open(filename, 'a+', newline="") as file:
            writer = csv.DictWriter(file, fieldnames=data[0].keys())
            for row in data:
                writer.writerow(row)
    except Exception as e:
        print(f"Error saving data to {filename}: {str(e)}")


if __name__ == '__main__':
    # coveralls = CoverallsCoverage('apache', 'commons-math') coveralls = CoverallsCoverage('ErnestFistozz',
    # 'codecov-coveralls')
    coverage_importer = CoverageImporter()
    # data = asyncio.get_event_loop().run_until_complete(
    # coverage_importer.analyze_commits(coveralls)) #   coveralls.collect_builds_data()) save_into_file(
    # 'CoverallsAsync.csv', data) save_into_file('./results.csv', result) files = asyncio.get_event_loop(
    # ).run_until_complete(coveralls.fetch_source_files("cbd08d0e3ef31bf1fbccb2ad1ffe6c28a1574822")) codecov =
    # CodeCovCoverage('apache', 'commons-math') result = asyncio.get_event_loop().run_until_complete(
    # codecov.commit_report('dd9ed7a104a471dddc78b9bac1bf42872efbd434'))
    codecov = CodeCovCoverage('ErnestFistozz', 'codecov-coveralls')
    # coverage_importer.checkout_and_analyse_codecov_commit(codecov)
    # results = asyncio.get_event_loop().run_until_complete(codecov.collect_build_data())
    results = data = asyncio.get_event_loop().run_until_complete(
        coverage_importer.analyze_codecov_commits(codecov))
    save_into_file('CodeCovAsyncResults.csv', results)
