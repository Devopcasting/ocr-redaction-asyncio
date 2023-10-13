import pytesseract
import re
import cv2

class RightTextCoordinates:
    def __init__(self, image_path) -> None:
        self.image_path = image_path
    
    # func: generate coordinates
    def generate_text_coordinates(self):
        image = cv2.imread(self.image_path)
        height, width, channels = image.shape
        cropped_image = image[:, width // 2:]
        data = pytesseract.image_to_data(cropped_image, output_type=pytesseract.Output.DICT)

        special_characters = r'[!@#$%^&*()_\-+{}\[\]:;<>,.?~\\|]'
        coordinates = []

        for i in range(len(data['text'])):
            text = data['text'][i]
            x1 = data['left'][i]
            y1 = data['top'][i]
            x2 = x1 + data['width'][i]
            y2 = y1 + data['height'][i]
            # Filter out empty strings and  special characters
            if not re.search(special_characters, text) and len(text) != 0:
                coordinates.append((x1, y1, x2, y2,text))
        return coordinates