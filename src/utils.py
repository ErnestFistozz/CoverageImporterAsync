from datetime import datetime, timezone
import csv
import platform
import subprocess

class Utils:
    @staticmethod
    def index_finder(search_word: str, files: list[str]) -> int:
        for index, word in enumerate(files):
            if search_word.lower() in word.lower():
                return index
        return -1

    @staticmethod
    def date_formatter(timestamp: str):
        formated_timestamp = datetime.fromisoformat(timestamp[:-1]).astimezone(timezone.utc)
        return formated_timestamp.strftime('%Y-%m-%d %H:%M:%S')

    @staticmethod
    def repositories(file_name: str) -> list:
        with open(file_name, 'r') as file:
            data = [line.split()[0].split("/") for line in file]
            file.close()
            return data

    @staticmethod
    def determine_machine() -> str:
        match platform.system().lower():
            case 'linux' | 'darwin':
                cmd = "whoami"
                result = subprocess.run(cmd, capture_output=True, shell=True, text=True, check=True).stdout
                user = result.replace('\n', '')
                return user
            case 'windows':
                cmd = '$env:USERNAME'
                result = (subprocess.run(["powershell", "-Command", cmd],
                                         capture_output=True, shell=True).stdout)
                data = result.decode('utf8').replace("'", '"')
                username = data.replace('\n', '')
                return username

    @staticmethod
    def save_into_file(filename: str, data: list) -> None:
        file_path = rf'{Utils.file_path()}{filename}'
        if data:  # if empty results then all hashes must be ignored
            try:
                with open(file_path, 'a+', newline="") as file:
                    writer = csv.DictWriter(file, fieldnames=data[0].keys())
                    for row in data:
                        if 'patch_coverage' in row:
                            writer.writerow(row)    # ensures that data without full columns is skipped
                    file.close()
            except Exception as e:
                print(f"Error saving data to {file_path}: {str(e)}")

    @staticmethod
    def file_path() -> str:
        match platform.system().lower():
            case 'linux' | 'darwin':
                return rf'/home/{Utils.determine_machine()}/repositories/'
            case 'windows':
                return rf'C:\Users\{Utils.determine_machine()}\Desktop\AzureDevOpsRepos' + "\\"