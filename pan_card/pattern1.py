import pytesseract
from pan_card.main import PanCardInfo
from ocrr_logging.ocrrlogging import OCRREngineLogging
from helpers.text_coordinates import TextCoordinates

class PanCardPattern1:
    def __init__(self, image_path) -> None:
        self.image_path = image_path
        # Configure logger
        config = OCRREngineLogging()
        self.logger = config.configure_logger()

    # func: search for coordinate of text below the matching text
    def search_coordinates_below_matching_text(self, matching_text: list) -> list:
        # Get the coordinates of all the texts
        all_coordinates = TextCoordinates(self.image_path).generate_text_coordinates()
        
        # Get the index of the matching text
        matching_text_index = 0
        for i, (x1, y1, x2, y2,text) in enumerate(all_coordinates):
            if text in matching_text:
                matching_text_index = i
                break

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

        for line in lines[lines.index(matching_line) + 1:]:
            if line == "":
                break
            text_below_matching_line += line + "\n"
        
        # Get the coordinates of text below matching text
        if len(text_below_matching_line.split()) > 1:
            text_below_matching_line_list = text_below_matching_line.split()[:-1]
        else:
            text_below_matching_line_list = text_below_matching_line.split()
        count = 0
        result = []
        search_status = False

        # If length of the text_below_matching_line_list
        if len(text_below_matching_line_list) == 1:
            for i in range(matching_text_index, len(all_coordinates)):
                if all_coordinates[i][4] in text_below_matching_line_list  and count < len(text_below_matching_line_list):
                    result.append([all_coordinates[i][k]for k in range(0, len(all_coordinates[i]) - 1)])
                    break
        else:
            for i in range(matching_text_index, len(all_coordinates)):
                if all_coordinates[i][4] in text_below_matching_line_list and count < len(text_below_matching_line_list):
                    result.append([all_coordinates[i][k]for k in range(0, len(all_coordinates[i]) - 1)])
                    count += 1

        return result

    # func: collect PAN card informations for Redaction
    def collect_pan_card_info(self) -> list:
        pan_card_info_obj = PanCardInfo(self.image_path)
        pan_card_info_list = []
        pan_card_user_name_keyword = ["Name"]
        pan_card_father_name_keyword = ["Father's", "Father"]

        # Collect : pan card number
        pan_card_number = pan_card_info_obj.extract_pan_card_number()
        if not pan_card_number or len(pan_card_number) == 0:
            self.logger.error("PANERR002")
            return False
        else:
            pan_card_info_list.append(pan_card_number)

        # Collect: pan card user name
        pan_card_user_name = self.search_coordinates_below_matching_text(pan_card_user_name_keyword)
        pan_card_info_list.extend(pan_card_user_name)

        # Collect: pan card father's name
        pan_card_father_name = self.search_coordinates_below_matching_text(pan_card_father_name_keyword)
        pan_card_info_list.extend(pan_card_father_name)

        # Collect: pan card dob
        pan_card_dob = pan_card_info_obj.extract_dob()
        if not pan_card_dob or len(pan_card_dob) == 0:
            self.logger.error("PANERR003") 
            return False
        else:
            pan_card_info_list.append(pan_card_dob)
        
        return pan_card_info_list
    