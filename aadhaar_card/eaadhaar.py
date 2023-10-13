import re
import cv2
import numpy as np
from PIL import Image
import pytesseract
from helpers.get_coordinates_cropped_left import LeftTextCoordinates
from helpers.get_coordinates_cropped_right import RightTextCoordinates
from helpers.get_coordinates import TextCoordinates
from ocrr_logging.ocrrlogging import OCRREngineLogging

class EAaadhaarCard:
    def __init__(self, image_path) -> None:
        self.image_path = image_path
        # Configure logger
        config = OCRREngineLogging()
        self.logger = config.configure_logger()
    
    # func: get the gender
    def extract_gender(self) -> list:
        coordinates = LeftTextCoordinates(self.image_path).generate_text_coordinates()
        gender_coordinates = []
        # Get the index of Male or Female
        for i ,(x1,y1,x2,y2,text) in enumerate(coordinates):
            if text.lower() in ["male", "female"]:
                gender_coordinates.append([coordinates[i - 1][0], coordinates[i - 1][1], x2, y2 ])
                break
        if len(gender_coordinates) == 0:
            return False
        else:
            return gender_coordinates
        
    # func: get the DOB
    def extract_dob(self):
        coordinates = LeftTextCoordinates(self.image_path).generate_text_coordinates()
        image = cv2.imread(self.image_path)
        height, width, channels = image.shape
        cropped_image = image[:, 0:width // 2]
        text = pytesseract.image_to_string(cropped_image)
        date_pattern = r'(\d{2})/(\d{2})/(\d{4})'
        dob_str = ""
        dob_str_coords = []
        result = []

        for i in text.split("\n"):
            if 'DOB' in i:
                match = re.search(date_pattern, i)
                if match:
                    day = match.group(1)
                    month = match.group(2)
                    year = match.group(3)
                    dob_str = f"{day}/{month}/{year}"
                    break
            if len(dob_str) != 0:
                break
        
        for i,(x1,y1,x2,y2,text) in enumerate(coordinates):
            if text == dob_str:
                dob_str_coords.append(x1)
                dob_str_coords.append(y1) 
                dob_str_coords.append(x2) 
                dob_str_coords.append(y2)
                break
        
        # calculate upto 6 character coordinates
        width = dob_str_coords[2] - dob_str_coords[0]
        height = dob_str_coords[3] - dob_str_coords[1]

        result.append(dob_str_coords[0])
        result.append(dob_str_coords[1])
        result.append(dob_str_coords[0] + int(0.6 * width))
        result.append(dob_str_coords[3])

        return result

    # func: get Aadhhar card numbers
    def extract_aadhaar_card_num(self):
        coordinates = TextCoordinates(self.image_path).generate_text_coordinates()
        image = Image.open(self.image_path)
        # height, width, channels = image.shape
        # cropped_image = image[:, 0:width // 2]
        text = pytesseract.image_to_string(image)
        
        # search for the coordinates
        search_coord = []
        match_index = 0
        coord_1 = []
        coord_2 = []
        temp = []
        result = []
    
        for i,(x1,y1,x2,y2,text) in enumerate(coordinates):
            if text.lower() == "vid":
                match_index = i
                break
        
        if match_index == 0:
            return False
        
        for i in range(match_index, -1 ,-1):
            if coordinates[i][4].isdigit() and len(coordinates[i][4]) == 4:
                search_coord.append(coordinates[i][4])
            if len(search_coord) == 3:
                break

        if len(search_coord) != 3:
            return False
        
        search_coord_reverse = search_coord[::-1][:-1]
        for i,(x1,y1,x2,y2,text) in enumerate(coordinates):
            if text == search_coord_reverse[0]:
                coord_1.append([x1,y1,x2,y2])
            if text == search_coord_reverse[1]:
                coord_2.append([x1,y1,x2,y2])

        if len(coord_1) and len(coord_2) != 3:
            return False
        
        for i in range(len(coord_1)):
            temp.append(coord_1[i][0])
            temp.append(coord_1[i][1])
            temp.append(coord_2[i][2])
            temp.append(coord_2[i][3])
            result.append(temp)
            temp = []
        
        return result

    # # func: collect name in english and other language
    # def extract_names(self):
    #     coordinates = TextCoordinates(self.image_path).generate_text_coordinates()
    #     text = pytesseract.image_to_string(self.image_path)
    #     start_index = 0
    #     result = []

    #     # Split the output by lines
    #     lines = [i for i in text.splitlines() if len(i) != 0]
    #     print(lines)
    #     for i,text in enumerate(lines):
    #         if "DOB" in text:
    #             start_index = i
    #             break
    #         if start_index != 0:
    #             break

    #     if start_index == 0:
    #         return False
        
    #     # get coordinates of name in english
    #     name_eng_lang_list = []
    #     name_eng_lang = lines[start_index -1].split()
    #     if len(name_eng_lang) > 1:
    #         name_eng_lang_list = name_eng_lang[:-1]
    #     else:
    #         name_eng_lang_list = name_eng_lang[0]

    #     print(name_eng_lang_list)
    #     # get the final coordinates
    #     for i in range(len(name_eng_lang_list)):
    #         for k,(x1,y1,x2,y2,text) in enumerate(coordinates):
    #             if text == name_eng_lang_list[i]:
    #                 result.append([x1,y1,x2,y2])
         
    #     return result

    # func: collect E Aadhaar card information
    def collect_e_aadhaar_card_info(self) -> list:
        e_aadhaar_card_info_list = []

        # # Collect: Name
        # if self.extract_names():
        #     e_aadhaar_card_info_list.extend(self.extract_names())
        # else:
        #     self.logger.error(f"AADERR004")
        #     return False

        # print(self.extract_names())
            
        #Collect: DOB
        aadhaar_card_dob = self.extract_dob()
        if not aadhaar_card_dob or len(aadhaar_card_dob) == 0:
            pass
        else:
            e_aadhaar_card_info_list.append(aadhaar_card_dob)
        
        #Collect: Gender
        aadhaar_card_gender = self.extract_gender()
        if aadhaar_card_gender:
            e_aadhaar_card_info_list.extend(aadhaar_card_gender)
        else:
            self.logger(f"AADERR002")
            return False
        
        # Collect: Aadhaar card number 
        left_aadhaar_card_num = self.extract_aadhaar_card_num()
        if len(left_aadhaar_card_num) != 0:
            e_aadhaar_card_info_list.extend(left_aadhaar_card_num)
        else:
            return False
        
        return e_aadhaar_card_info_list