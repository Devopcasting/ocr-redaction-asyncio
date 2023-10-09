import os
import shutil
from aadhaar_card.front import AadhaarCardFront
from helpers.write_xml import WriteXML

class AadhaarCardFrontHandler:
    def __init__(self, image_path, xml_path, redacted_path) -> None:
        # paths
        self.image_path = image_path
        self.xml_path = xml_path
        self.redacted_path = redacted_path

        # image name
        self.image_file_name = os.path.basename(self.image_path)
    
    def aadhaarcard_front(self):
        # collect aadhaar card front information
        collect_aadhaar_card_info_obj = AadhaarCardFront(self.image_path).collect_aadhaar_card_info()
        if collect_aadhaar_card_info_obj:
            WriteXML(self.xml_path, self.image_file_name, collect_aadhaar_card_info_obj).writexml()
            shutil.move(self.image_path,  os.path.join(self.redacted_path, self.image_file_name))
            return True
        else:
            return False

