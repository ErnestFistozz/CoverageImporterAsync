import asyncio
import csv
from src.coveralls import CoverallsCoverage
from src.utils import Utils
from src.coveralls_logger import CoverallsCoverageLogger
from src.touched_files import CoverallsDQsData


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
    coveralls_repositories = Utils.repositories('coveralls_repos.txt')
    logger = CoverallsCoverageLogger()
    for coveralls_repo in coveralls_repositories:
        coveralls = CoverallsCoverage(coveralls_repo[0], coveralls_repo[1], logger)
        coveralls_dq = CoverallsDQsData(coveralls)
        coveralls_dqs_data = asyncio.get_event_loop().run_until_complete(
            coveralls_dq.analyze_commits())
        try:
            save_into_file('FinalCoverallsDQsResults.csv', coveralls_dqs_data)
        except Exception as err:
            print(f'Error with saving data for Coveralls, {err}')
            continue
