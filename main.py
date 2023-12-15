import asyncio
from src.coveralls import CoverallsCoverage
from src.codecov import CodeCovCoverage
import csv
import json


# def save_into_file(filename: str, coverage: list) -> None:
#     with open(filename, "a+") as outfile:
#         csv_writer = csv.writer(outfile)
#         for row in coverage:
#             try:
#                 print(row)
#                 csv_writer.writerow([value for key, value in row.items()])
#                 print("I am writting")
#             except Exception as e:
#                 print(f"{str(e)}")
#                 continue

def save_into_file(filename: str, coverage: list) -> None:
    try:
        with open(filename, 'w') as file:
            json.dump(coverage, file, indent=2)
        print(f"Data saved to {filename} successfully.")
    except Exception as e:
        print(f"Error saving data to {filename}: {str(e)}")


if __name__ == '__main__':
    coveralls = CoverallsCoverage('apache', 'commons-math')
    result = asyncio.get_event_loop().run_until_complete(coveralls.collect_builds_data())
    # save_into_file('./results.csv', result)
    # files = asyncio.get_event_loop().run_until_complete(coveralls.fetch_source_files("cbd08d0e3ef31bf1fbccb2ad1ffe6c28a1574822"))
    # codecov = CodeCovCoverage('apache', 'commons-math')
    # result = asyncio.get_event_loop().run_until_complete(codecov.commit_report('dd9ed7a104a471dddc78b9bac1bf42872efbd434'))
    print(len(result))
