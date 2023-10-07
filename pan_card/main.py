import pytesseract
import cv2
import re
from helpers.text_coordinates import TextCoordinates

class PanCardInfo:
    def __init__(self, image_path) -> None:
        self.image_path = image_path

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
    
    # func: extract the pan card number
    def extract_pan_card_number(self):
        data = pytesseract.image_to_data(self.image_path, output_type=pytesseract.Output.DICT)
        matching_text = ["Permanent", "Pe@fanent", "Pe@ffignent"]
        
        # Find the coordinates of matching text
        matching_text_coords = []
        for i, text in enumerate(data["text"]):
            if text in matching_text:
                x1, y1, width, height = data["left"][i], data["top"][i], data["width"][i], data["height"][i]
                x2, y2 = x1 + width, y1 + height
                matching_text_coords.append((x1, y1, x2, y2, text))
                break

        # Get the coordinates of text below matching text
        if len(matching_text_coords) != 0:
            below_text_coords = {}
            for x1, y1, x2, y2, text in matching_text_coords:
                for i in range(len(data["text"])):
                    if data["top"][i] > y2 and len(data["text"][i]) != 0:
                        below_text_x1, below_text_y1, below_text_width, below_text_height = data["left"][i], data["top"][i], data["width"][i], data["height"][i]
                        below_text_x2, below_text_y2 = below_text_x1 + below_text_width, below_text_y1 + below_text_height
                        below_text = data["text"][i]
                        below_text_coords[below_text] = [below_text_x1, below_text_y1, below_text_x2, below_text_y2]

            # loop: below_text_crrods
            # All in caps and is alphanum
            pan_card_num_coords = []
            for i,k in below_text_coords.items():
                if i.isupper() and i.isalnum():
                    bound_box = self.bound_box_coords(i, 5)
                    pan_card_num_coords.append(bound_box[0][1][0])
                    pan_card_num_coords.append(bound_box[0][1][1])
                    pan_card_num_coords.append(bound_box[4][1][2])
                    pan_card_num_coords.append(bound_box[4][1][3])
                    return pan_card_num_coords
            return False
        else:
            return False
    
    # func: extract DOB from pan card
    def extract_dob(self):
        # date pattern DD/MM/YYY
        date_pattern = r'\d{2}/\d{2}/\d{4}'
        coordinates = TextCoordinates(self.image_path).generate_text_coordinates()

        dob_coords = []

        for i, (x1,y1,x2,y2,text) in enumerate(coordinates):
            match = re.search(date_pattern, coordinates[i][4])
            if match:
                bound_box = self.bound_box_coords(coordinates[i][4] , 6)
                dob_coords.append(bound_box[0][1][0])
                dob_coords.append(bound_box[0][1][1])
                dob_coords.append(bound_box[5][1][2])
                dob_coords.append(bound_box[5][1][3])
                return dob_coords              
        return False