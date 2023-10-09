import re
import cv2
import pytesseract
from helpers.text_coordinates import TextCoordinates
from ocrr_logging.ocrrlogging import OCRREngineLogging

class AadhaarCardFront:
    def __init__(self, image_path) -> None:
        self.image_path = image_path
        # Configure logger
        config = OCRREngineLogging()
        self.logger = config.configure_logger()
    
    # func: get the Bound box coordinates of each char of a string
    def bound_box_coords(self, text: str, indexcount: int) -> list:
        image = cv2.imread(self.image_path)
        h, w, c = image.shape
        text_to_match = list(text)
        len_text_to_match = len(text_to_match)
        result = []
        coords = []

        # process image and bound boxes on each char
        boxes = pytesseract.image_to_boxes(self.image_path)

        for b in boxes.splitlines():
            b = b.split(' ')
            x1, y1, x2, y2 = int(b[1]), h - int(b[2]), int(b[3]), h - int(b[4])
            text = b[0]
            coords.append([text,(x1,y1,x2,y2)])

        for i,w in enumerate(coords):
            if coords[i][0] == text_to_match[0] and coords[i+1][0] == text_to_match[1]:
                result.append(coords[i])
                result.append(coords[i+1])
                text_to_match.pop(0)
                text_to_match.pop(0)
            if len(result) == len_text_to_match:
                break
        return result[:indexcount]
    
    # func: get the gender
    def extract_gender(self) -> list:
        coordinates = TextCoordinates(self.image_path).generate_text_coordinates()
        gender_coordinates = []
        result = []
        matching_index = 0
        # Get the index of Male or Female
        for i ,(x1,y1,x2,y2,text) in enumerate(coordinates):
            if text.lower() in ["male", "female"]:
                matching_index = i
                break
        # Reverse loop from Male/Female index until DOB comes
        for i in range(matching_index, -1, -1):
            if re.match(r'^\d{2}/\d{2}/\d{4}$', coordinates[i][4]) or re.match(r'^\d{4}$', coordinates[i][4]):
                break
            else:
                gender_coordinates.append([coordinates[i][0], coordinates[i][1], coordinates[i][2], coordinates[i][3]])

        # Prepare final coordinates
        result1 = [i for i in gender_coordinates[::-1]]
        result.append(result1[0][0])
        result.append(result1[0][1])
        result.append(result1[-1][2])
        result.append(result1[-1][3])

        return result
    
    # func: get the DOB
    def extract_dob(self):
        coordinates = TextCoordinates(self.image_path).generate_text_coordinates()
        date_pattern = r'\d{2}/\d{2}/\d{4}'
        dob_coords = []
        for i, (x1, y1, x2, y2, text) in enumerate(coordinates):
            match = re.search(date_pattern, coordinates[i][4])
            if match:
                bound_box = self.bound_box_coords(coordinates[i][4] , 6)
                dob_coords.append(bound_box[0][1][0])
                dob_coords.append(bound_box[0][1][1])
                dob_coords.append(bound_box[5][1][2])
                dob_coords.append(bound_box[5][1][3])
                return dob_coords              
        return False

    # func: get aadhaar card number
    def extract_aadhaar_card_num(self):
        coordinates = TextCoordinates(self.image_path).generate_text_coordinates()
        start_index = 0
        aadhaar_num = []
        result = []
        pattern = r'[реж-реп]+'

        # Get the start index
        for i,(x1,y1,x2,y2,text) in enumerate(coordinates):
            if text.lower() in ["male", "female"]:
                start_index = i
                break
        
        for i in range(start_index, len(coordinates)):
            text = coordinates[i][4]
            if len(text) == 4 and text.isdigit() and not re.search(pattern, text):
                aadhaar_num.append([coordinates[i][0],coordinates[i][1],coordinates[i][2],coordinates[i][3]])
            if len(aadhaar_num) == 2:
                break
            
        if len(aadhaar_num) < 2:
            return False
        else:
            result.append(aadhaar_num[0][0])
            result.append(aadhaar_num[0][1])
            result.append(aadhaar_num[1][2])
            result.append(aadhaar_num[1][3])
            return result

    # func: collect name in english and other language
    def extract_names(self):
        coordinates = TextCoordinates(self.image_path).generate_text_coordinates()
        text = pytesseract.image_to_string(self.image_path, lang="eng")
        start_index = 0
        matching_text = ["Year", "DOB"]
        result = []

        # Split the output by lines
        lines = [i for i in text.splitlines() if len(i) != 0]
        for i,text in enumerate(lines):
            if "Year" in text or "DOB" in text:
                start_index = i
                break
            if start_index != 0:
                break

        if start_index == 0:
            return False
        
        # get coordinates of name in english
        name_eng_coordinates = []
        name_eng_lang_list = []
        name_eng_lang = lines[start_index -1].split()
        if len(name_eng_lang) > 1:
            name_eng_lang_list = name_eng_lang[:-1]
        else:
            name_eng_lang_list = name_eng_lang[0]

        for i,(x1,y1,x2,y2,text) in enumerate(coordinates):
            if text in name_eng_lang_list:
                name_eng_coordinates.append([x1,y1,x2,y2])
                name_eng_lang_list.remove(text)
                break
            if len(name_eng_lang_list) == 0:
                break
        return name_eng_coordinates



    # func: collect Aadhaar card information
    def collect_aadhaar_card_info(self) -> list:
        aadhaar_card_info_list = []

        # Collect: Name
        if self.extract_names():
            aadhaar_card_info_list.extend(self.extract_names())
        else:
            self.logger.error(f"AADERR004")
            return False
        
        # Collect: DOB
        aadhaar_card_dob = self.extract_dob()
        if not aadhaar_card_dob or len(aadhaar_card_dob) == 0:
            pass
        else:
            aadhaar_card_info_list.append(aadhaar_card_dob)

        # Collect: Gender
        aadhaar_card_gender = self.extract_gender()
        if aadhaar_card_gender:
            aadhaar_card_info_list.append(aadhaar_card_gender)
        else:
            self.logger(f"AADERR002")
            return False
        
        # Collect: Aadhaar card number
        aadhaar_num = self.extract_aadhaar_card_num()
        if aadhaar_num:
            aadhaar_card_info_list.append(aadhaar_num)
        else:
            self.logger(f"AADERR003")
            return False
        
        return aadhaar_card_info_list