import pytesseract
from pan_card.main import PanCardInfo
from ocrr_logging.ocrrlogging import OCRREngineLogging
from helpers.text_coordinates import TextCoordinates

class PanCardPattern2:
    def __init__(self, image_path) -> None:
        self.image_path = image_path
       # Configure logger
        config = OCRREngineLogging()
        logger = config.configure_logger()

    # func: search for coordinate of text below the matching text
    def search_coordinates_below_matching_text(self, matching_text: list) -> list:
        # Get the coordinates of all the texts
        all_coordinates = TextCoordinates(self.image_path).generate_text_coordinates()

        # Find the text below matching text
        matching_line = None
        text_below_matching_line = ""
        text = pytesseract.image_to_string(self.image_path)
        lines = text.split("\n")
        for line in lines:
            for text in matching_text:
                if text in line:
                    matching_line = line
                    break
            if matching_line is not None:
                break

        # Get the text below the matching line
        text_below_matching_line = ""
        full_name_list = []
        if matching_line is not None:
            for i in range(2):
                current_line = lines[lines.index(matching_line) + 1 + i]
                if current_line == "":
                    break
                text_below_matching_line += current_line + "\n"

        # Get text coordinates
        get_text_list = []
        for i in text_below_matching_line.split("\n"):
            if len(i.split()) == 1:
                get_text_list.extend(i.split())
            else:
                get_text_list.extend(i.split()[:-1])
        
        # Get the coordinates of matching text
        result = []
        count = 0
        for i, (x1, y1, x2, y2, text) in enumerate(all_coordinates):
            if text in get_text_list:
                result.append([x1, y1, x2, y2])
                get_text_list.remove(text)
            if len(get_text_list) == 0:
                break
        
        return result

    # func: collect PAN card informations for Redaction
    def collect_pan_card_info(self) -> list:
        pan_card_info_obj = PanCardInfo(self.image_path)
        pan_card_info_list = []
        matching_text_keyword = ["INCOME", "TAX", "DEPARTMENT"]

        # Collect: pan card number
        pan_card_number = pan_card_info_obj.extract_pan_card_number()
        if not pan_card_number or len(pan_card_number) == 0:
            self.logger.error("PANERR002")
            return False
        else:
            pan_card_info_list.append(pan_card_number)

        # Collect: pan card user name and father name
        pan_card_user_father_name = self.search_coordinates_below_matching_text(matching_text_keyword)
        pan_card_info_list.extend(pan_card_user_father_name)

        # Collect: pan card dob
        pan_card_dob = pan_card_info_obj.extract_dob()
        if not pan_card_dob or len(pan_card_dob) == 0:
            self.logger.error("PANERR003")
            return False
        else:
            pan_card_info_list.append(pan_card_dob)
        
        return pan_card_info_list
    