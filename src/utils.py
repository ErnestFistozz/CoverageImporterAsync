from datetime import datetime, timezone
import csv
import os
import platform
import pandas as pd
import subprocess
import logging

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
            return [line.split()[0].split("/") for line in file]

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
    def coverage_logger(filename: str, error_message: str) -> None:
        full_datetime = datetime.now()
        file_format = '{}_{}_{}_{}_{}_{}'.format(full_datetime.day,
                                                 full_datetime.month,
                                                 full_datetime.year,
                                                 full_datetime.second,
                                                 full_datetime.minute,
                                                 full_datetime.hour)
        match platform.system().lower():
            case 'linux' | 'darwin':
                full_filename = rf'/home/{Utils.determine_machine()}/repositories/{file_format}_{filename}.log'
            case 'windows':
                full_filename = rf'C:\Users\{Utils.determine_machine()}\Desktop\AzureDevOpsRepos\{file_format}_{filename}.log'
        logging.basicConfig(filename=full_filename,
                            encoding='utf-8',
                            format='%(asctime)s:%(levelname)s:%(message)s',
                            level=logging.DEBUG,
                            datefmt='%m/%d/%Y %I:%M:%S %p')
        logging.error(error_message)