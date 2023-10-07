import os
import shutil
from pan_card.pattern1 import PanCardPattern1
from helpers.write_xml import WriteXML


class PanCardPattern1Handler:
    def __init__(self, image_path, xml_path, redacted_path) -> None:
        # paths
        self.image_path = image_path
        self.xml_path = xml_path
        self.redacted_path = redacted_path

        # image name
        self.image_file_name = os.path.basename(self.image_path)
    
    
    def pancard_p1(self):
        # Collect pan card informations
        collect_pan_card_info_obj = PanCardPattern1(self.image_path).collect_pan_card_info()

        if collect_pan_card_info_obj:
            WriteXML(self.xml_path, self.image_file_name, collect_pan_card_info_obj ).writexml()
            shutil.move(self.image_path,  os.path.join(self.redacted_path, self.image_file_name))
            return True
        else:
            return False
