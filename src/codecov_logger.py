from src.coverage_logger import CoverageLogger
import logging


class CodecovCoverageLogger(CoverageLogger):
    def warning(self, error_message) -> None:
        CoverageLogger.coverage_logger_configuration('FinalCodecovWarningErrors')
        logging.warning(error_message)

    def information(self, error_message) -> None:
        CoverageLogger.coverage_logger_configuration('FinalCodecovInformationErrors')
        logging.info(error_message)

    def error(self, error_message) -> None:
        CoverageLogger.coverage_logger_configuration('FinalCodecovCriticalErrors')
        logging.error(error_message) # error and critical errors are treated the same in this context

    def debug(self, error_message) -> None:
        CoverageLogger.coverage_logger_configuration('FinalCodecovDebugErrors')
        logging.debug(error_message)