from src.coverage_logger import CoverageLogger
import logging

class CoverallsCoverageLogger(CoverageLogger):
    def warning(self, error_message) -> None:
        CoverageLogger.coverage_logger_configuration('FinalCoverallsWarningErrors')
        logging.warning(error_message)

    def information(self, error_message) -> None:
        CoverageLogger.coverage_logger_configuration('FinalCoverallsInformationErrors')
        logging.info(error_message)

    def error(self, error_message) -> None:
        CoverageLogger.coverage_logger_configuration('FinalCoverallsCriticalErrors')
        logging.error(error_message)

    def debug(self, error_message) -> None:
        CoverageLogger.coverage_logger_configuration('FinalCoverallsDebugErrors')
        logging.debug(error_message)