import asyncio
import csv
from src.codecov import CodeCovCoverage
from src.utils import Utils
from src.codecov_logger import CodecovCoverageLogger
from src.touched_files import CodeCovDQsData


def save_into_file(filename: str, data: list) -> None:
    file_path = rf'{Utils.file_path()}{filename}'
    if data:
        try:
            with open(file_path, 'a+', newline="") as file:
                writer = csv.DictWriter(file, fieldnames=data[0].keys())
                for row in data:
                    writer.writerow(row)
                file.close()
        except Exception as e:
            print(f"Error saving data to {file_path}: {str(e)}")


if __name__ == '__main__':
    codecov_repositories = Utils.repositories('codecov_repos.txt')
    logger = CodecovCoverageLogger()

    for codecov_repo in codecov_repositories:
        codecov = CodeCovCoverage(codecov_repo[0], codecov_repo[1], logger)
        codecov_dqs = CodeCovDQsData(codecov)
        codecov_dqs_data = asyncio.get_event_loop().run_until_complete(codecov_dqs.analyze_commits())
        try:
            save_into_file('FinalCodeCovDQsResults.csv', codecov_dqs_data)
        except Exception as err:
            print(f'Error with saving data for Codecov, {err}')
            continue
