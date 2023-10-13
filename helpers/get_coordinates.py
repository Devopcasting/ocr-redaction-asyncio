import pytesseract
import re
import cv2
from PIL import Image

class TextCoordinates:
    def __init__(self, image_path) -> None:
        self.image_path = image_path
    
    # func: generate coordinates
    def generate_text_coordinates(self):
        image = Image.open(self.image_path)
        data = pytesseract.image_to_data(image, output_type=pytesseract.Output.DICT)
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