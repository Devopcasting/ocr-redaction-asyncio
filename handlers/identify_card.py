import shutil
import os
import pytesseract
from ocrr_logging.ocrrlogging import OCRREngineLogging
from helpers.process_text import CleanText
from helpers.identify_pan_card import IdentifyPanCard
from helpers.identify_aadhaar_card import IdentifyAadhaarCard

class IdentifyCard:
    def __init__(self, image_path, pancard_p1, pancard_p2, aadhaarcard_front, eaadhaar) -> None:
        # Get paths
        self.image_path = image_path
        self.file_name = os.path.basename(self.image_path)
        self.pancard_p1_path = pancard_p1
        self.pancard_p2_path = pancard_p2
        self.aadhaarcard_front_path = aadhaarcard_front
        self.eaadhaar_path = eaadhaar

        # Configure logger
        self.config = OCRREngineLogging()
        self.logger = self.config.configure_logger()

        # Configure tesseract
        self.tesseract_config = r'-l eng --oem 3 --psm 6'
    
    def identify(self):
        # Get the text in Dict from image
        data_text = pytesseract.image_to_string(self.image_path, output_type=pytesseract.Output.DICT,config=self.tesseract_config)
        clean_text = CleanText(data_text).clean_text()

        # Check for Pan card and Aadhaar card
        pan_card = IdentifyPanCard(clean_text)
        aadhaar_card = IdentifyAadhaarCard(clean_text)

        if pan_card.check_pan_card():
            if pan_card.identify_pan_card_pattern_1():
                self.logger.info(f"Pan card {self.file_name} is of pattern 1")
                shutil.move(self.image_path, os.path.join(self.pancard_p1_path, self.file_name))
                return True
            else:
                self.logger.info(f"Pan card {self.file_name} is of pattern 2")
                shutil.move(self.image_path, os.path.join(self.pancard_p2_path, self.file_name))
                return True
        elif aadhaar_card.check_aadhaar_card():
            if aadhaar_card.aadhaar_card_identifiers_eaadhaar:
                self.logger.info(f"E-Aaadhaar card {self.file_name}")
                shutil.move(self.image_path, os.path.join(self.eaadhaar_path, self.file_name))
                return True
            elif aadhaar_card.check_aadhaar_front():
                self.logger.info(f"Front-side of Aadhaar card found in {self.file_name}")
                shutil.move(self.image_path, os.path.join(self.aadhaarcard_front_path, self.file_name))
                return True
            else:
                return False
        else:
            return False

