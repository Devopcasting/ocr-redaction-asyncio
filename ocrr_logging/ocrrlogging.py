import logging
import configparser
import os

class OCRREngineLogging:
    def __init__(self, log_file='ocrr.log', log_level=logging.INFO) -> None:

        # create a ConfigParser object with the allow_no_value keyword argument
        config = configparser.ConfigParser(allow_no_value=True)
        # read config.ini
        config.read(r'C:\Users\pokhriyal\Desktop\Asyncio-OCRR-Pan_Card\config.ini')
        occr_log_path = config['Path']['log']

        self.log_file = os.path.join(occr_log_path,log_file)
        self.log_level = log_level
    
    def configure_logger(self):
        logger = logging.getLogger(__name__)
        logger.setLevel(self.log_level)

        file_handler = logging.FileHandler(self.log_file)
        file_handler.setLevel(self.log_level)

        formatter = logging.Formatter('%(process)d %(asctime)s %(levelname)s %(message)s')
        file_handler.setFormatter(formatter)

        logger.addHandler(file_handler)

        return logger
    