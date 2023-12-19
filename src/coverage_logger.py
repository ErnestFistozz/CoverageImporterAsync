from abc import ABC, abstractmethod
import logging
from datetime import datetime
from src.utils import Utils

class CoverageLogger(ABC):
    @abstractmethod
    def warning(self, error_message) -> None:
        pass

    @abstractmethod
    def error(self, error_message) -> None:
        pass

    @abstractmethod
    def debug(self, error_message) -> None:
        pass

    @abstractmethod
    def information(self, error_message) -> None:
        pass

    @staticmethod
    def coverage_logger_configuration(filename: str) -> None:
        full_datetime = datetime.now()
        file_format = '{}_{}_{}_{}_{}_{}'.format(full_datetime.day,
                                                 full_datetime.month,
                                                 full_datetime.year,
                                                 full_datetime.second,
                                                 full_datetime.minute,
                                                 full_datetime.hour)
        full_filename = rf'{Utils.file_path()}{file_format}_{filename}.log'
        logging.basicConfig(filename=full_filename,
                            encoding='utf-8',
                            format='%(asctime)s:%(levelname)s:%(message)s',
                            level=logging.DEBUG,
                            datefmt='%m/%d/%Y %I:%M:%S %p')
